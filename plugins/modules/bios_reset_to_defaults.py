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
module: bios_reset_to_defaults
short_description: Reset BIOS to factory settings
version_added: "1.1.0"
description:
  - This module supports check mode
author: "Sergey Kovalev (@kvlvs)"
extends_documentation_fragment:
  - yadro.obmc.connection_options
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
- name: Reset BIOS to defaults
  yadro.obmc.bios_reset_to_defaults:
    connection:
      hostname: "localhost"
      username: "username"
      password: "password"
"""


from ansible_collections.yadro.obmc.plugins.module_utils.obmc_module import OpenBmcModule


class BiosResetToDefaultsModule(OpenBmcModule):

    def __init__(self):
        super(BiosResetToDefaultsModule, self).__init__(
            supports_check_mode=True
        )

    def _run(self):
        bios = self.redfish.get_system("system").get_bios()
        if not self.check_mode:
            bios.reset()
        self.exit_json(msg="Operation successful.", changed=True)


def main():
    BiosResetToDefaultsModule().run()


if __name__ == "__main__":
    main()
