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
module: firmware_info
short_description: Return BMC and BIOS firmware information.
version_added: "1.0.0"
description:
  - This module supports check mode.
author: "Radmir Safin (@radmirsafin)"
extends_documentation_fragment:
  - yadro.obmc.connection_options
"""

RETURN = r"""
---
msg:
  type: str
  returned: always
  description: Operation status message.
error_info:
  type: str
  returned: on error
  description: Error details if raised.
firmware_info:
  type: dict
  returned: on success
  description: BMC, BIOS firmware versions.
  sample: {
    "BMC": {
        "Description": "BMC image",
        "Status": {
          "Health": "OK",
          "HealthRollup": "OK",
          "State": "Enabled"
        },
        "Updateable": true,
        "Version": "v1.0"
    },
    "BIOS": {
      "Description": "BIOS image",
      "Status": {
        "Health": "OK",
        "HealthRollup": "OK",
        "State": "Enabled"
      },
      "Updateable": true,
      "Version": "v1.0"
    },
  }
"""

EXAMPLES = r"""
---
- name: Get firmware information
  yadro.obmc.firmware_info:
    connection:
      hostname: "localhost"
      username: "username"
      password: "password"
  register: firmware_info
"""


from ansible_collections.yadro.obmc.plugins.module_utils.obmc_module import OpenBmcModule


class OpenBmcFirmwareInfoModule(OpenBmcModule):

    def __init__(self):
        super(OpenBmcFirmwareInfoModule, self).__init__(supports_check_mode=True)

    def _run(self):
        manager_info = self.client.get_manager()
        bios_info = self.client.get_bios()
        self.exit_json(msg="Firmware information successfully read.", firmware_info={
            "BMC": self.client.get_software_inventory(manager_info["Links"]["ActiveSoftwareImage"]),
            "BIOS": self.client.get_software_inventory(bios_info["Links"]["ActiveSoftwareImage"]),
        })


def main():
    OpenBmcFirmwareInfoModule().run()


if __name__ == "__main__":
    main()
