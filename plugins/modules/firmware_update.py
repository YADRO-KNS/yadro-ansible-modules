#!/usr/bin/python
# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.0.0
# Copyright (c) 2022 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r"""
---
module: firmware_update
short_description: Updates bmc or host firmware.
version_added: "1.1.0"
description:
  - Updates bmc or host firmware depending on the provided image.
  - Can update only single device at time, so if you want to update both,
    you should use this module twice with different images.
  - Supports http, https, tftp servers or local storage as image location.
author: "Sergey Kovalev (@kvlvs)"
extends_documentation_fragment:
  - yadro.obmc.connection_options
options:
  image_path:
    required: True
    type: str
    description:
      - Path to the image. It can be http, https, tftp server or local storage.
  validate_certs:
    required: False
    type: bool
    default: True
    description:
      - Indicates a need for certificate validation
      - Actual only for https server as image location
  upload_timeout:
    required: False
    type: int
    default: 1800
    description:
      - How many seconds to wait for the image to be uploaded to the server.
  activate_timeout:
    required: False
    type: int
    default: 300
    description:
      - How many seconds to wait for the image to be activated on BMC or on the host.
"""

RETURN = r"""
---
msg:
  type: str
  returned: always
  description: Operation status message.
error:
  type: str
  returned: on error
  description: Error details if raised.
"""

EXAMPLES = r"""
---
- name: Update BMC firmware
  yadro.obmc.firmware_update:
    connection:
      hostname: "localhost"
      username: "username"
      password: "password"
    path: path-to-image/bmc-firmware.bin
"""


import os
import time
import json
from io import open
from ansible_collections.yadro.obmc.plugins.module_utils.obmc_module import OpenBmcModule
from ansible.module_utils.urls import open_url
from ansible.module_utils.six.moves.urllib.error import URLError, HTTPError


BMC_ACTIVE_ID = 'bmc_active'
BIOS_ACTIVE_ID = 'bios_active'
BMC_IMAGE_DESC = 'BMC image'
BIOS_IMAGE_DESC = 'Host image'


class OpenBmcFirmwareUpdate(OpenBmcModule):

    def __init__(self):
        argument_spec = {
            'image_path': {'type': 'str', 'required': True},
            'validate_certs': {
                'type': 'bool',
                'required': False,
                'default': True,
            },
            'upload_timeout': {
                'type': 'int',
                'required': False,
                'default': 1800,
            },
            'activate_timeout': {
                'type': 'int',
                'required': False,
                'default': 300,
            }
        }
        super(OpenBmcFirmwareUpdate, self).__init__(
            argument_spec=argument_spec,
            supports_check_mode=False,
        )

    def _run(self):
        system = self.redfish.get_system('system')
        if system.get_power_state() != 'Off':
            self.fail_json(
                error='Host is not powered off',
                msg='Host must be powered off for updating firmware',
                changed=False,
            )

        # Save initial images identifiers for
        # determine new uploaded image
        init_img_ids = self._get_init_images_ids()

        self._upload_image()

        new_image = self._determine_new_image(
            init_img_ids=init_img_ids,
        )

        self._wait_image_activation(new_image)
        self._reboot_updated_device(new_image)

        self.exit_json(msg="Operation successful.", changed=True)

    def _upload_image(self):
        upd_service = self.redfish.get_update_service()

        if os.path.exists(self.params['image_path']):
            if not os.path.isfile(self.params['image_path']):
                self.fail_json(
                    error='Wrong local path was given',
                    msg='{0} is not a file. Path to image file is required'.format(
                        self.params['image_path']),
                    changed=False,
                )

            with open(self.params['image_path'], 'rb') as file:
                upd_service.upload_image(file.read())

        elif self.params['image_path'].startswith(('http://', 'https://')):
            response = None
            try:
                response = open_url(
                    url=self.params['image_path'],
                    method='GET',
                    validate_certs=self.params['validate_certs'],
                    timeout=60,
                )
            except HTTPError as e:
                self.fail_json(
                    error=(str(e)),
                    msg='Error while getting image from {0}'.format(
                        self.params['image_path']),
                    changed=False,
                )
            except URLError as e:
                self.fail_json(
                    error=str(e.reason),
                    msg='Error while getting image from {0}'.format(
                        self.params['image_path']),
                    changed=False,
                )
            except Exception as e:
                self.fail_json(
                    error=str(e),
                    msg='Unexpected error while getting image from {0}'.format(
                        self.params['image_path']),
                    changed=False,
                )

            upd_service.upload_image(response.read())

        elif self.params['image_path'].startswith('tftp://'):
            upd_service.simple_update(self.params['image_path'])

        else:
            self.fail_json(
                error='Unknown image location {0}'.format(
                    self.params['image_path']),
                msg='Only http, https, tftp ot local '
                    'system location are supported',
                changed=False,
            )

    def _get_init_images_ids(self):
        upd_service = self.redfish.get_update_service()
        init_images = upd_service.get_firmware_inventory_collection()
        return set(img.get_id() for img in init_images)

    def _determine_new_image(self, init_img_ids):
        # We have to wait until image will be uploaded. Generally, it is
        # actual for tftp download, which is really long and processing
        # on the server's side. This is the reason for a big timeout

        new_image = None
        start_time = time.time()

        while not new_image:
            time.sleep(1)
            # refresh firmware collection
            upd_service = self.redfish.get_update_service()
            current_images = upd_service.get_firmware_inventory_collection()
            # if count of images was changed, we suppose
            # that new image was uploaded
            if len(current_images) > len(init_img_ids):
                for image in current_images:
                    is_active = image.get_id() in (BMC_ACTIVE_ID, BIOS_ACTIVE_ID)
                    # if one of images has id that was not saved
                    # at the beginning, then it is new uploaded image
                    if image.get_id() not in init_img_ids and not is_active:
                        new_image = image
                        break

            if time.time() - start_time > self.params['upload_timeout']:
                self.fail_json(
                    error='Timeout error',
                    msg='New image was not found or was not '
                        'upload for {timeout} seconds'.format(
                            timeout=self.params['upload_timeout']),
                    changed=True,
                )

        return new_image

    def _wait_image_activation(self, image):
        start_time = time.time()
        while not self._is_upload_active(image):
            timedelta = time.time() - start_time
            if timedelta > self.params['activate_timeout']:
                self.fail_json(
                    error='Timeout error',
                    msg='Image {id} was not found in '
                        'Active status'.format(id=image.get_id()),
                    changed=True,
                )

            time.sleep(1)

    def _is_upload_active(self, image):
        connection = self.params['connection']
        url = '{hostname}:{port}/xyz/openbmc_project/software/{image_id}'.format(
            hostname=connection['hostname'],
            port=connection['port'],
            image_id=image.get_id()
        )

        response = open_url(
            url,
            url_username=connection['username'],
            url_password=connection['password'],
            force_basic_auth=True,
            method='GET',
            timeout=60,
            validate_certs=connection['validate_certs'],
        )

        activation_status = json.loads(response.read())['data']['Activation']
        return activation_status == 'xyz.openbmc_project.Software.Activation.Activations.Active'

    def _reboot_updated_device(self, image):
        description = image.get_description()

        if description == BMC_IMAGE_DESC:
            manager = self.redfish.get_manager('bmc')
            manager.reset_graceful()

        elif description == BIOS_IMAGE_DESC:
            system = self.redfish.get_system('system')
            system.power_on_graceful()

        else:
            self.fail_json(
                error='Could not recognize image description',
                msg='New image description is {new_desc}. '
                    'Expected: {exp_desc}. '
                    'Host and BMC were not restarted'.format(
                        new_desc=description,
                        exp_desc=(BMC_IMAGE_DESC, BIOS_IMAGE_DESC)),
                changed=True,  # Image was uploaded without restart
            )


def main():
    OpenBmcFirmwareUpdate().run()


if __name__ == "__main__":
    main()
