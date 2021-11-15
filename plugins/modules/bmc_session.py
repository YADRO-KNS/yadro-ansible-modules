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
module: bmc_session
short_description: Manages BMC sessions.
version_added: "1.0.0"
description:
  - Creates user session and returns session key.
  - Closes previously created sessions.
  - This module supports check mode.
author: "Radmir Safin (@radmirsafin)"
extends_documentation_fragment:
  - yadro.obmc.connection_options
options:
  username:
    type: str
    description: Session username. Required to create session.
  password:
    type: str
    description: Session user password. Required to create session.
  session_id:
    type: str
    description: Session id. Required to close session.
  state:
    type: str
    choices: [present, absent]
    default: present
    description:
      - C(present) always creates a new session.
      - C(absent) deletes an existing session.
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
session:
  type: dict
  returned: on success and state present
  description: Contains session information.
  sample: {
    "Id": "IzQa2ZTHT5",
    "Key" : "UOaFqhn7mYnmg5hMaCsx",
  }
"""

EXAMPLES = r"""
---
- name: Create readonly user session
  yadro.obmc.bmc_session:
    connection:
      hostname: "localhost"
      username: "username"
      password: "password"
    username: "readonly"
    password: "password"
    state: present
  register: result

- name: Read BMC firmware info via session key
  yadro.obmc.bmc_firmware_info:
    connection:
      hostname: "localhost"
      session_key: "{{ result['session']['key'] }}"

- name: Close readonly user session
  yadro.obmc.bmc_session:
    connection:
      hostname: "localhost"
      username: "username"
      password: "password"
    session_key: "{{ result['session']['id'] }}"
    state: absent
"""


from ansible_collections.yadro.obmc.plugins.module_utils.obmc_module import OpenBmcModule


class OpenBmcSessionModule(OpenBmcModule):

    def __init__(self):
        argument_spec = {
            "username": {"required": False, "type": "str"},
            "password": {"required": False, "type": "str", "no_log": True},
            "session_id": {"required": False, "type": "str"},
            "state": {
                "type": "str",
                "required": False,
                "default": "present",
                "choices": ["present", "absent"],
            },
        }
        required_if = [
            ["state", "present", ["username", "password"]],
            ["state", "absent", ["session_id"]],
        ],

        super(OpenBmcSessionModule, self).__init__(argument_spec=argument_spec, supports_check_mode=True)

    def _run(self):
        if self.params["state"] == "present":
            result = {"id": "", "key": ""}
            if not self.check_mode:
                result = self.client.create_session({
                    "UserName": self.params["username"],
                    "Password": self.params["password"],
                })
            self.exit_json(msg="Session created.", changed=True, session=result)
        else:
            if not self.check_mode:
                self.client.delete_session(self.params["session_id"])
            self.exit_json(msg="Session deleted.", changed=True)


def main():
    OpenBmcSessionModule().run()


if __name__ == "__main__":
    main()
