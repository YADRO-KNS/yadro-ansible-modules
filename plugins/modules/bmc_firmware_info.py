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
short_description: Returns BMC firmware information.
version_added: "1.0.0"
description:
  - Returns BMC firmware information.
  - This module supports check mode.
extends_documentation_fragment:
  - yadro.obmc.connection_options
author: "Radmir Safin (@radmirsafin)"
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
  description: BMC firmware information.
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
- name: Get firmware information
  yadro.obmc.bmc_firmware_info:
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
        firmware_info = self.client.get_software_inventory(manager_info["Links"]["ActiveSoftwareImage"])
        self.exit_json(msg="Firmware information successfully read.", firmware_info=firmware_info)


def main():
    OpenBmcFirmwareInfoModule().run()


if __name__ == "__main__":
    main()
