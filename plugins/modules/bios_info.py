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
module: bios_info
short_description: Return BIOS information.
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
bios_info:
  type: dict
  returned: on success
  description: BIOS firmware information.
  sample: {
    "Description": "BIOS image",
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
- name: Get BIOS information
  yadro.obmc.bios_info:
    connection:
      hostname: "localhost"
      username: "username"
      password: "password"
  register: bios_info
"""


from ansible_collections.yadro.obmc.plugins.module_utils.obmc_module import OpenBmcModule


class OpenBmcBiosInfoModule(OpenBmcModule):

    def __init__(self):
        super(OpenBmcBiosInfoModule, self).__init__(supports_check_mode=True)

    def _run(self):
        bios_info = self.client.get_bios()
        bios_firmware_info = self.client.get_software_inventory(bios_info["Links"]["ActiveSoftwareImage"])
        self.exit_json(msg="BIOS information successfully read.", bios_info=bios_firmware_info)


def main():
    OpenBmcBiosInfoModule().run()


if __name__ == "__main__":
    main()
