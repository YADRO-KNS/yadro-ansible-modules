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
  - Set system’s hostname.
  - This module supports check mode.
author: "Radmir Safin (@radmirsafin)"
extends_documentation_fragment:
  - yadro.obmc.connection_options
options:
  name:
    required: True
    type: str
    description: Name of the BMC.
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
- name: Set BMC hostname
  yadro.obmc.bmc_hostname:
    connection:
      hostname: "localhost"
      username: "username"
      password: "password"
    name: "bmc-01"
"""


from ansible_collections.yadro.obmc.plugins.module_utils.obmc_module import OpenBmcModule


class OpenBmcHostnameModule(OpenBmcModule):

    def __init__(self):
        argument_spec = {
            "name": {"required": True, "type": "str"},
        }

        super(OpenBmcHostnameModule, self).__init__(argument_spec=argument_spec, supports_check_mode=True)

    def _run(self):
        iface = self.client.get_ethernet_interface_collection()[0]
        config = self.client.get_ethernet_interface(iface)

        payload = {}
        if self.params["name"] != config["HostName"]:
            payload["HostName"] = self.params["name"]

        if payload:
            if not self.check_mode:
                self.client.update_ethernet_interface(iface, payload)
            self.exit_json(msg="Hostname updated.", changed=True)
        else:
            self.exit_json(msg="No changes required.", changed=False)


def main():
    OpenBmcHostnameModule().run()


if __name__ == "__main__":
    main()
