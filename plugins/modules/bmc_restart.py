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
module: bmc_restart
short_description: Resets the BMC.
version_added: "1.0.0"
description:
  - This module supports check mode.
author: "Radmir Safin (@radmirsafin)"
extends_documentation_fragment:
  - yadro.obmc.connection_options
options:
  force:
    type: bool
    default: False
    description: It indicates BMC will be restart right away.
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
"""

EXAMPLES = r"""
---
- name: Restart BMC
  yadro.obmc.bmc_restart:
    connection:
      hostname: "localhost"
      username: "username"
      password: "password"

- name: Force restart BMC
  yadro.obmc.bmc_restart:
    connection:
      hostname: "localhost"
      username: "username"
      password: "password"
    force: true
"""


from ansible_collections.yadro.obmc.plugins.module_utils.obmc_module import OpenBmcModule


class OpenBmcRestartModule(OpenBmcModule):

    def __init__(self):
        argument_spec = {"force": {"required": False, "type": "bool", "default": False}}
        super(OpenBmcRestartModule, self).__init__(argument_spec=argument_spec, supports_check_mode=True)

    def _run(self):
        payload = {"ResetType": "GracefulRestart"}
        if self.params["force"]:
            payload["ResetType"] = "ForceRestart"

        if not self.check_mode:
            self.client.reset(payload)
        self.exit_json(msg="BMC restart scheduled.", changed=True)


def main():
    OpenBmcRestartModule().run()


if __name__ == "__main__":
    main()
