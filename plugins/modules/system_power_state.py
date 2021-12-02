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
module: system_power_state
short_description: System power operations.
version_added: "1.0.0"
description:
  - This module supports check mode.
author: "Radmir Safin (@radmirsafin)"
extends_documentation_fragment:
  - yadro.obmc.connection_options
options:
  state:
    required: True
    type: str
    choices: ["Online", "Offline", "Restarted"]
    description: Describes server target state.
  force:
    type: bool
    default: False
    description: It indicates system will be turned off right away. May cause data corruption.
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
- name: Ensure system offline
  yadro.obmc.system_power_state:
    connection:
      hostname: "localhost"
      username: "username"
      password: "password"
    state: Offline

- name: Ensure system online
  yadro.obmc.system_power_state:
    connection:
      hostname: "localhost"
      username: "username"
      password: "password"
    state: Online

- name: Force restart system
  yadro.obmc.system_power_state:
    connection:
      hostname: "localhost"
      username: "username"
      password: "password"
    state: Restarted
    force: true
"""


from functools import partial
from ansible_collections.yadro.obmc.plugins.module_utils.obmc_module import OpenBmcModule


class OpenBmcPowerStateModule(OpenBmcModule):

    def __init__(self):
        argument_spec = {
            "state": {
                "type": "str",
                "required": True,
                "choices": ["Online", "Offline", "Restarted"]
            },
            "force": {
                "type": "bool",
                "required": False,
                "default": False
            }
        }
        super(OpenBmcPowerStateModule, self).__init__(
            argument_spec=argument_spec,
            supports_check_mode=True
        )

    def _run(self):
        changes = []

        system = self.redfish.get_system("system")
        current_state = system.get_power_state()
        if self.params["state"] == "Online":
            if current_state != "On":
                if self.params["force"]:
                    changes.append(partial(system.power_on_force))
                else:
                    changes.append(partial(system.power_on_graceful))
        elif self.params["state"] == "Offline":
            if current_state != "Off":
                if self.params["force"]:
                    changes.append(partial(system.power_off_force))
                else:
                    changes.append(partial(system.power_off_graceful))
        else:
            if self.params["force"]:
                changes.append(partial(system.power_reset_force))
            else:
                changes.append(partial(system.power_reset_graceful))

        if changes:
            if not self.check_mode:
                for action in changes:
                    action()
            self.exit_json(msg="Operation successful.", changed=True)
        else:
            self.exit_json(msg="No changes required.", changed=False)


def main():
    OpenBmcPowerStateModule().run()


if __name__ == "__main__":
    main()
