#!/usr/bin/python
# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.1.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


DOCUMENTATION = r"""
---
module: bmc_security_config
short_description: Manage BMC security protocols.
version_added: "1.1.0"
description:
  - Enables/disables SSH and IPMI access.
  - This module supports check mode.
author: "Sergey Kovalev (@kvlvs)"
extends_documentation_fragment:
  - yadro.obmc.connection_options
options:
  ssh_enabled:
    required: false
    type: bool
    description: Indicates if SSH protocol is enabled or disabled.
  ipmi_enabled:
    required: false
    type: bool
    description: Indicates if IPMI remote management is enabled or disabled.
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
- name: Enable SSH support
  yadro.obmc.bmc_security_config:
    connection:
      hostname: "{{ server }}"
      username: "{{ username }}"
      password: "{{ password }}"
    ssh_enabled: true

- name: Disable IPMI support
  yadro.obmc.bmc_security_config:
    connection:
      hostname: "{{ server }}"
      username: "{{ username }}"
      password: "{{ password }}"
    ipmi_enabled: false
"""


from functools import partial
from ansible_collections.yadro.obmc.plugins.module_utils.obmc_module import OpenBmcModule


class OpenBmcSecurityConfigModule(OpenBmcModule):

    def __init__(self):
        argument_spec = {
            "ssh_enabled": {"type": "bool", "required": False},
            "ipmi_enabled": {"type": "bool", "required": False},
        }

        super(OpenBmcSecurityConfigModule, self).__init__(
            argument_spec=argument_spec,
            supports_check_mode=True,
        )

    def _run(self):
        changes = []

        network_protocol = self.redfish.get_manager("bmc").get_network_protocol()

        if self.params["ssh_enabled"] is not None and \
                self.params["ssh_enabled"] != network_protocol.get_ssh_enabled():
            changes.append(partial(
                network_protocol.set_ssh_enabled,
                self.params["ssh_enabled"],
            ))

        if self.params["ipmi_enabled"] is not None and \
                self.params["ipmi_enabled"] != network_protocol.get_ipmi_enabled():
            changes.append(partial(
                network_protocol.set_ipmi_enabled,
                self.params["ipmi_enabled"]
            ))

        if changes:
            if not self.check_mode:
                for action in changes:
                    action()
            self.exit_json(msg="Operation successful.", changed=True)
        else:
            self.exit_json(msg="No changes required.", changed=False)


def main():
    OpenBmcSecurityConfigModule().run()


if __name__ == "__main__":
    main()
