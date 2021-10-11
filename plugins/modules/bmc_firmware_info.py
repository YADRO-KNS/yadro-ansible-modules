#!/usr/bin/python
# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.0.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


DOCUMENTATION = r"""
---
module: bmc_firmware_info
short_description: Returns OpenBmc firmware information.
version_added: "1.0.0"
description: Returns OpenBmc firmware information.
extends_documentation_fragment:
  - yadro.obmc.connection_options
requirements:
  - "python >= 2.7.5"
author: "Radmir Safin (@radmirsafin)"
"""

RETURN = r"""
---
msg:
  type: str
  returned: always
  description: Operation status message.
  sample: Firmware information successfully fetched.
error_info:
  type: dict
  returned: on error
  description: Error details.
firmware_info:
  type: dict
  returned: on success
  description: OpenBmc firmware information.
  sample: {
    "Description": "BMC image",
    "Status": {
      "Health": "OK",
      "HealthRollup": "OK",
      "State": "Enabled"
    },
    "Updateable": true,
    "Version": "v1.0"
  }
"""

EXAMPLES = r"""
---
- name: Get server information
  yadro.obmc.bmc_firmware_info:
    connection:
      hostname: "192.168.0.1"
      username: "username"
      password: "password"
  register: firmware_info
"""

import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import ConnectionError, SSLValidationError
from ansible.module_utils.six.moves.urllib.error import URLError, HTTPError
from ansible_collections.yadro.obmc.plugins.module_utils.bmc_client import create_client


def main():
    module = AnsibleModule(
        argument_spec={
            "connection": {
                "type": "dict",
                "required": True,
                "options": {
                    "hostname": {"required": True, "type": "str"},
                    "username": {"required": True, "type": "str"},
                    "password": {"required": True, "type": "str", "no_log": True},
                    "port": {"required": False, "default": 443, "type": "int"},
                    "validate_certs": {"required": False, "default": True, "type": "bool"},
                }
            }
        },
        supports_check_mode=False
    )

    try:
        client = create_client(**module.params["connection"])
        managers = client.get_manager_collection()
        if len(managers) != 1:
            module.fail_json(
                msg="Can't identify BMC manager.",
                error_info="Operations with only one BMC manager supported. Found: {0}".format(len(managers))
            )
        active_firmware = client.get_manager(managers[0])["Links"]["ActiveSoftwareImage"]
        firmware_info = client.get_software_inventory(active_firmware)
    except HTTPError as e:
        module.fail_json(msg="Request finished with error.", error_info=str(e))
    except URLError as e:
        module.fail_json(msg="Can't connect to server.", error_info=str(e))
    except (SSLValidationError, ConnectionError) as e:
        module.fail_json(msg="Can't read firmware information.", error_info=str(e))
    else:
        module.exit_json(msg="Firmware information successfully read.", firmware_info=firmware_info)


if __name__ == "__main__":
    main()
