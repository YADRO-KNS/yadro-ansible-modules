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
module: bmc_time
short_description: Manage BMC time.
version_added: "1.0.0"
description:
  - Configures NTP servers. Timezone is always set to GMT.
  - This module supports check mode.
author: "Radmir Safin (@radmirsafin)"
extends_documentation_fragment:
  - yadro.obmc.connection_options
options:
  ntp_enabled:
    required: false
    type: bool
    description: Indicates if NTP protocol is enabled or disabled. If disabled host time will be used.
  ntp_servers:
    required: false
    type: list
    description:
      - List of NTP servers IP. Supported up to 3 NTP servers.
      - If empty list is set, all servers configuration will be removed.
    elements: str
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
- name: Configure NTP servers
  yadro.obmc.bmc_time:
    connection:
      hostname: "{{ server }}"
      username: "{{ username }}"
      password: "{{ password }}"
    ntp_enabled: true
    ntp_servers:
      - 192.168.1.100
      - 192.168.2.100

- name: Change NTP servers
  yadro.obmc.bmc_time:
    connection:
      hostname: "{{ server }}"
      username: "{{ username }}"
      password: "{{ password }}"
    ntp_enabled: true
    ntp_servers:
      - 192.168.3.100

- name: Remove NTP servers
  yadro.obmc.bmc_time:
    connection:
      hostname: "{{ server }}"
      username: "{{ username }}"
      password: "{{ password }}"
    ntp_enabled: true
    ntp_servers: []

- name: Disable NTP support
  yadro.obmc.bmc_time:
    connection:
      hostname: "{{ server }}"
      username: "{{ username }}"
      password: "{{ password }}"
    ntp_enabled: false
"""


from functools import partial
from ansible_collections.yadro.obmc.plugins.module_utils.obmc_module import OpenBmcModule


class OpenBmcTimeModule(OpenBmcModule):

    def __init__(self):
        argument_spec = {
            "ntp_enabled": {"type": "bool", "required": False},
            "ntp_servers": {"type": "list", "required": False, "elements": "str"},
        }
        super(OpenBmcTimeModule, self).__init__(
            argument_spec=argument_spec,
            supports_check_mode=True
        )

    def _run(self):
        changes = []

        if self.params["ntp_servers"] and len(self.params["ntp_servers"]) > 3:
            self.fail_json(
                msg="Cannot configure NTP servers.",
                error="Supported no more than 3 NTP servers.",
                changed=False
            )

        manager = self.redfish.get_manager("bmc")
        network_protocol = manager.get_network_protocol()

        if self.params["ntp_enabled"] is not None and \
                self.params["ntp_enabled"] != network_protocol.get_ntp_enabled():
            changes.append(partial(
                network_protocol.set_ntp_enabled,
                self.params["ntp_enabled"],
            ))

        if self.params["ntp_servers"] is not None and \
                self.params["ntp_servers"] != network_protocol.get_ntp_servers():
            changes.append(partial(
                network_protocol.set_ntp_servers,
                self.params["ntp_servers"],
            ))

        if changes:
            if not self.check_mode:
                for action in changes:
                    action()
            self.exit_json(msg="Operation successful.", changed=True)
        else:
            self.exit_json(msg="No changes required.", changed=False)


def main():
    OpenBmcTimeModule().run()


if __name__ == "__main__":
    main()
