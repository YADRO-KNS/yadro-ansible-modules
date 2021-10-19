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
short_description: Module for managing OpenBmc accounts.
version_added: "1.0.0"
description: Creates, deletes and updates user accounts.
extends_documentation_fragment:
  - yadro.obmc.connection_options
author: "Radmir Safin (@radmirsafin)"
options:
  username:
    required: true
    type: str
    description: The user name of the account.
  password:
    type: str
    description:
      - The password of the account.
      - Required when creating a new user.
      - Module can't compare passwords, so if I(password) field is set, module
      - step will always finished with Changed result.
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
  sample: Account created.
error_info:
  type: str
  returned: on error
  description: Error details.
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

import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import ConnectionError, SSLValidationError
from ansible.module_utils.six.moves.urllib.error import URLError, HTTPError
from ansible_collections.yadro.obmc.plugins.module_utils.client.client import create_client


def run_module(module):
    params = module.params
    action = None
    payload = {}

    client = create_client(**params["connection"])
    accounts = client.get_account_collection()
    if params["state"] == "present":
        if params["username"] in accounts:
            action = "update"
            user_account = client.get_account(params["username"])
            if params["password"]:
                payload["Password"] = params["password"]
            if params["role"] and params["role"] != user_account["RoleId"]:
                payload["RoleId"] = params["role"]
            if params["enabled"] is not None and params["enabled"] != user_account["Enabled"]:
                payload["Enabled"] = params["enabled"]
            if payload:
                payload["UserName"] = params["username"]
        else:
            action = "create"
            for k in ["password", "role", "enabled"]:
                if params[k] is None:
                    module.fail_json(
                        msg="Can't create new account.",
                        error_info="Field required: {0}.".format(k),
                        changed=False
                    )
            payload = {
                "UserName": params["username"],
                "Password": params["password"],
                "RoleId": params["role"],
                "Enabled": params["enabled"],
            }
    else:
        if params["username"] in accounts:
            action = "delete"

    if action == "create" and payload:
        if not module.check_mode:
            client.create_account(payload)
        module.exit_json(msg="Account created.", changed=True)
    elif action == "update" and payload:
        if not module.check_mode:
            client.update_account(payload)
        module.exit_json(msg="Account updated.", changed=True)
    elif action == "delete":
        if not module.check_mode:
            client.delete_account(params["username"])
        module.exit_json(msg="Account deleted.", changed=True)
    else:
        module.exit_json(msg="No changes required.", changed=False)


def main():
    module = AnsibleModule(
        argument_spec={
            "connection": {
                "required": True,
                "type": "dict",
                "options": {
                    "hostname": {"required": True, "type": "str"},
                    "username": {"required": True, "type": "str"},
                    "password": {"required": True, "type": "str", "no_log": True},
                    "port": {"required": False, "type": "int", "default": 443},
                    "validate_certs": {"required": False, "type": "bool", "default": True},
                }
            },
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
        },
        supports_check_mode=True
    )

    try:
        run_module(module)
    except HTTPError as e:
        module.fail_json(msg="Request finished with error.", error_info=json.load(e))
    except (URLError, SSLValidationError, ConnectionError) as e:
        module.fail_json(msg="Can't connect to server.", error_info=str(e))


if __name__ == "__main__":
    main()
