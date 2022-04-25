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
module: bmc_reset_to_defaults
short_description: Reset BMC to factory settings
version_added: "1.1.0"
description:
  - This module supports check mode
author: "Sergey Kovalev (@kvlvs)"
extends_documentation_fragment:
  - yadro.obmc.connection_options
options:
  reset_type:
    required: True
    type: str
    choices: [all]
    description: Reset type
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
- name: Reset BMC to defaults
  yadro.obmc.bmc_reset_to_defaults:
    connection:
      hostname: "localhost"
      username: "username"
      password: "password"
    reset_type: all
"""


from ansible_collections.yadro.obmc.plugins.module_utils.obmc_module import OpenBmcModule


class OpenBmcResetToDefaultsModule(OpenBmcModule):

    def __init__(self):
        argument_spec = {
            "reset_type": {
                "type": "str",
                "required": True,
                "choices": ["all", ],
            }
        }
        super(OpenBmcResetToDefaultsModule, self).__init__(
            argument_spec=argument_spec,
            supports_check_mode=True
        )

    def _run(self):

        manager = self.redfish.get_manager("bmc")
        if not self.check_mode:
            manager.reset_to_defaults(self.params["reset_type"])

        self.exit_json(msg="Operation successful.", changed=True)


def main():
    OpenBmcResetToDefaultsModule().run()


if __name__ == "__main__":
    main()
