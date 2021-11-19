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
module: bmc_account
short_description: Manage BMC accounts.
version_added: "1.0.0"
description:
  - This module supports check mode.
author: "Radmir Safin (@radmirsafin)"
extends_documentation_fragment:
  - yadro.obmc.connection_options
options:
  username:
    required: True
    type: str
    description: The user name of the account.
  password:
    type: str
    description:
      - The password of the account.
      - Required when creating a new user.
      - Module can't compare passwords, so if I(password) field is set, module
      - step will always finished with C(changed) result.
  role:
    type: str
    choices: [Administrator, Operator, ReadOnly, NoAccess]
    description:
      - The role of the account that restricts user permissions.
      - Required when creating a new user.
  enabled:
    type: bool
    description:
      - Indication of whether an account is enabled.
      - Required when creating a new user.
      - C(true) if the account is enabled, the user can log in.
      - C(false) if the account is disabled, the user cannot log in.
  state:
    type: str
    choices: [present, absent]
    default: present
    description:
      - C(present) creates a new account if I(username) does not exists.
      - If account exists module will try to modify it.
      - C(absent) deletes an existing account.
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
- name: Create TestUser
  yadro.obmc.bmc_account:
    connection:
      hostname: "localhost"
      username: "username"
      password: "password"
    username: "TestUser"
    password: "TestPassword"
    role: "Operator"
    enabled: true
    state: "present"

- name: Modify TestUser
  yadro.obmc.bmc_account:
    connection:
      hostname: "localhost"
      username: "username"
      password: "password"
    username: "TestUser"
    enabled: false
    role: "ReadOnly"

- name: Delete TestUser
  yadro.obmc.bmc_account:
    connection:
      hostname: "localhost"
      username: "username"
      password: "password"
    username: "TestUser"
    state: "absent"
"""


from ansible_collections.yadro.obmc.plugins.module_utils.obmc_module import OpenBmcModule


class OpenBmcAccountModule(OpenBmcModule):

    def __init__(self):
        argument_spec = {
            "username": {"type": "str", "required": True},
            "password": {"type": "str", "required": False, "no_log": True},
            "role": {
                "type": "str",
                "required": False,
                "choices": ["Administrator", "Operator", "ReadOnly", "NoAccess"]
            },
            "enabled": {"type": "bool", "required": False},
            "state": {
                "type": "str",
                "required": False,
                "default": "present",
                "choices": ["present", "absent"]
            },
        }
        super(OpenBmcAccountModule, self).__init__(argument_spec=argument_spec, supports_check_mode=True)

    def _run(self):
        action = None
        payload = {}

        accounts = self.client.get_account_collection()
        if self.params["state"] == "present":
            if self.params["username"] in accounts:
                action = "update"
                user_account = self.client.get_account(self.params["username"])
                if self.params["password"]:
                    payload["Password"] = self.params["password"]
                if self.params["role"] and self.params["role"] != user_account["RoleId"]:
                    payload["RoleId"] = self.params["role"]
                if self.params["enabled"] is not None and self.params["enabled"] != user_account["Enabled"]:
                    payload["Enabled"] = self.params["enabled"]
            else:
                action = "create"
                missed_args = []
                for k in ["password", "role", "enabled"]:
                    if self.params[k] is None:
                        missed_args.append(k)
                if missed_args:
                    self.fail_json(
                        msg="Cannot create new account.",
                        error_info="Fields required: {0}.".format(", ".join(missed_args)),
                        changed=False
                    )

                payload = {
                    "UserName": self.params["username"],
                    "Password": self.params["password"],
                    "RoleId": self.params["role"],
                    "Enabled": self.params["enabled"],
                }
        else:
            if self.params["username"] in accounts:
                action = "delete"

        if action == "create" and payload:
            if not self.check_mode:
                self.client.create_account(payload)
            self.exit_json(msg="Account created.", changed=True)
        elif action == "update" and payload:
            if not self.check_mode:
                self.client.update_account(self.params["username"], payload)
            self.exit_json(msg="Account updated.", changed=True)
        elif action == "delete":
            if not self.check_mode:
                self.client.delete_account(self.params["username"])
            self.exit_json(msg="Account deleted.", changed=True)
        else:
            self.exit_json(msg="No changes required.", changed=False)


def main():
    OpenBmcAccountModule().run()


if __name__ == "__main__":
    main()
