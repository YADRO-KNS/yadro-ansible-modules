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
  returned: on HTTP error
  description: Error details.
firmware_info:
  type: dict
  returned: success
  description: OpenBmc firmware information.
  sample: {
    "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/bmc_active",
    "@odata.type": "#SoftwareInventory.v1_1_0.SoftwareInventory",
    "Description": "BMC image",
    "Id": "bmc_active",
    "Members@odata.count": 1,
    "Name": "Software Inventory",
    "RelatedItem": [
      {
        "@odata.id": "/redfish/v1/Managers/bmc"
      }
    ],
    "Status": {
      "Health": "OK",
      "HealthRollup": "OK",
      "State": "Enabled"
    },
    "Updateable": true,
    "Version": "v1.3rb93fad"
  }
"""

EXAMPLES = r"""
---
- name: Get server information
  yadro.obmc.bmc_firmware_info:
    hostname: "192.168.0.1"
    username: "username"
    password: "password"
  register: firmware_info
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.yadro.obmc.plugins.module_utils.client import OpenBmcRestClient, RestClientError


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
                    "verify_certs": {"required": False, "default": True, "type": "bool"},
                }
            }
        },
        supports_check_mode=True
    )

    client = OpenBmcRestClient(
        hostname=module.params["connection"]["hostname"],
        username=module.params["connection"]["username"],
        password=module.params["connection"]["password"],
        verify_certs=module.params["connection"]["verify_certs"],
        port=module.params["connection"]["port"]
    )

    try:
        firmware_info = client.get_bmc_firmware_info()
    except Exception as e:
        module.fail_json(msg="Can't read firmware information.", error_info=e.msg)
    else:
        module.exit_json(msg="Firmware information successfully read.", firmware_info=firmware_info)


if __name__ == "__main__":
    main()
