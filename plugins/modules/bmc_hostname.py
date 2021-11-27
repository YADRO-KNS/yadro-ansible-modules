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
module: bmc_hostname
short_description: Manage BMC hostname.
version_added: "1.0.0"
description:
  - This module supports check mode.
author: "Radmir Safin (@radmirsafin)"
extends_documentation_fragment:
  - yadro.obmc.connection_options
options:
  name:
    required: True
    type: str
    description: The DNS Host Name of this BMC, without any domain information.
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
- name: Set BMC hostname
  yadro.obmc.bmc_hostname:
    connection:
      hostname: "localhost"
      username: "username"
      password: "password"
    name: "bmc-01"
"""


from functools import partial
from ansible_collections.yadro.obmc.plugins.module_utils.obmc_module import OpenBmcModule


class OpenBmcHostnameModule(OpenBmcModule):

    def __init__(self):
        argument_spec = {"name": {"required": True, "type": "str"}}
        super(OpenBmcHostnameModule, self).__init__(
            argument_spec=argument_spec,
            supports_check_mode=True
        )

    def _run(self):
        changes = []

        network_protocol = self.redfish.get_manager("bmc").get_network_protocol()
        if self.params["name"] != network_protocol.get_hostname():
            changes.append(partial(
                network_protocol.set_hostname,
                self.params["name"],
            ))

        if changes:
            if not self.check_mode:
                for action in changes:
                    action()
            self.exit_json(msg="Operation successful.", changed=True)
        else:
            self.exit_json(msg="No changes required.", changed=False)


def main():
    OpenBmcHostnameModule().run()


if __name__ == "__main__":
    main()
