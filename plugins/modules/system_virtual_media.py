#!/usr/bin/python
# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.1.0
# Copyright (c) 2022 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


DOCUMENTATION = r"""
---
module: system_virtual_media
short_description: Connect or disconnect virtual media image to host.
version_added: "1.1.0"
description:
  - Inserts/eject os image as virtual media through given URI.
  - Reboots host if corresponding flag is passed.
  - Supports HTTP, HTTPS, SMB, NFS, FTP, SFTP and SCP protocols.
  - Common usage is os deploying. Virtual media with the os
    unattended image connects to host with following reboot.
author: "Sergey Kovalev (@kvlvs)"
extends_documentation_fragment:
  - yadro.obmc.connection_options
options:
  image_path:
    type: str
    description:
      - Path to image file on the server
      - Option is required if state is present
    required: False
  state:
    type: str
    choices: [present, absent]
    default: present
    description:
      - C(present) inserts virtual media.
      - C(absent) ejects virtual media.
  reboot_host:
    type: bool
    default: False
    description:
      - Indicates if reboot host is needed after inject or eject virtual media.
  media_type:
    type: str
    description: Type of inserting media
    required: False
    choices: ['USBStick', 'HDD', 'CD']
    default: 'USBStick'
  username:
    type: str
    description: Login to access the URI
    required: False
  password:
    type: str
    description: Password to access the URI
    required: False
  transfer_method:
    type: str
    description: Transfer method to use with the image
    required: False
    default: 'Stream'
  write_protected:
    type: bool
    description: Indication of whether the remote media is treated as write-protected
    required: False
    default: True
  inserted:
    type: bool
    description: An indication of whether the image is treated as inserted upon completion of the action
    required: False
    default: True
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
- name: Inject virtual media
  yadro.obmc.system_virtual_media:
    connection:
      hostname: 'localhost'
      username: 'username'
      password: 'password'
    image_path: 'http://image-server.com/image.iso'
    username: 'username'
    password: 'password'
    reboot_host: True

- name: Eject virtual media
  yadro.obmc.system_virtual_media:
    connection:
      hostname: 'localhost'
      username: 'username'
      password: 'password'
    state: absent
    reboot_host: True
"""


from ansible_collections.yadro.obmc.plugins.module_utils.obmc_module import OpenBmcModule


class OpenBmcVirtualMedia(OpenBmcModule):

    def __init__(self):
        argument_spec = {
            'image_path': {'type': 'str', 'required': False},
            "state": {
                "type": "str",
                "required": False,
                "default": "present",
                "choices": ["present", "absent"],
            },
            'reboot_host': {
                'type': 'bool',
                'required': False,
                'default': False,
            },
            'media_type': {
                'type': 'str',
                'required': False,
                'default': 'USBStick',
                'choices': ['USBStick', 'HDD', 'CD'],
            },
            'username': {'type': 'str', 'required': False},
            'password': {'type': 'str', 'required': False, 'no_log': True},
            'transfer_method': {
                'type': 'str',
                'required': False,
                'default': 'Stream',
            },
            'write_protected': {
                'type': 'bool',
                'required': False,
                'default': True,
            },
            'inserted': {
                'type': 'bool',
                'required': False,
                'default': True,
            },
        }

        super(OpenBmcVirtualMedia, self).__init__(
            argument_spec=argument_spec,
            supports_check_mode=False,
            required_if=[['state', 'present', ['image_path']]],
        )

    def _run(self):
        manager = self.redfish.get_manager('bmc')
        vm = manager.get_virtual_media('USB1')

        if self.params['state'] == 'present':
            vm.insert(
                image_path=self.params['image_path'],
                media_type=self.params['media_type'],
                username=self.params['username'],
                password=self.params['password'],
                transfer_method=self.params['transfer_method'],
                write_protected=self.params['write_protected'],
                inserted=self.params['inserted'],
            )
        else:
            vm.eject()

        if self.params['reboot_host']:
            self._reboot_host()

        self.exit_json(msg="Operation successful.", changed=True)

    def _reboot_host(self):
        system = self.redfish.get_system('system')
        if system.get_power_state() == 'Off':
            system.power_on_graceful()
        else:
            system.power_reset_graceful()


def main():
    OpenBmcVirtualMedia().run()


if __name__ == "__main__":
    main()
