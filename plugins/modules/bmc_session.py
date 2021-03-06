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
short_description: Manage BMC sessions.
version_added: "1.0.0"
description:
  - Creates user session and returns session key. Connection username and password required.
  - Closes previously created sessions.
  - This module supports check mode.
author: "Radmir Safin (@radmirsafin)"
extends_documentation_fragment:
  - yadro.obmc.connection_options
options:
  session_id:
    type: str
    description: Session ID. Required to close session.
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
error:
  type: str
  returned: on error
  description: Error details if raised.
session:
  type: dict
  returned: on success and state present
  description: Contains session information.
  sample: {
    "id": "IzQa2ZTHT5",
    "key" : "UOaFqhn7mYnmg5hMaCsx",
  }
"""

EXAMPLES = r"""
---
- name: Create session
  yadro.obmc.bmc_session:
    connection:
      hostname: "localhost"
      username: "username"
      password: "password"
    state: present
  register: result

- name: Read firmware info via session key
  yadro.obmc.firmware_info:
    connection:
      hostname: "localhost"
      session_key: "{{ result['session']['key'] }}"

- name: Close session
  yadro.obmc.bmc_session:
    connection:
      hostname: "localhost"
      username: "username"
      password: "password"
    session_key: "{{ result['session']['id'] }}"
    state: absent
"""


from functools import partial
from ansible_collections.yadro.obmc.plugins.module_utils.obmc_module import OpenBmcModule


class OpenBmcSessionModule(OpenBmcModule):

    def __init__(self):
        argument_spec = {
            "session_id": {"required": False, "type": "str"},
            "state": {
                "type": "str",
                "required": False,
                "default": "present",
                "choices": ["present", "absent"],
            },
        }
        required_if = [
            ["state", "absent", ["session_id"]],
        ],

        super(OpenBmcSessionModule, self).__init__(
            argument_spec=argument_spec,
            supports_check_mode=True,
        )

    def _run(self):
        if not (self.params["connection"]["username"] and self.params["connection"]["password"]):
            self.fail_json(
                msg="Cannot create session.",
                error="Connection username and password required to create session.",
                changed=False,
            )

        if self.params["state"] == "present":
            result = {"id": "", "key": ""}
            if not self.check_mode:
                session = self.redfish.create_session(
                    self.params["connection"]["username"],
                    self.params["connection"]["password"],
                )
                result = {
                    "id": session.get_id(),
                    "key": session.get_token(),
                }
            self.exit_json(msg="Operation successful.", changed=True, session=result)
        else:
            session_service = self.redfish.get_session_service()
            session = session_service.get_session(self.params["session_id"])
            if session:
                if not self.check_mode:
                    session_service.delete_session(self.params["session_id"])
                self.exit_json(msg="Operation successful.", changed=True)
            else:
                self.exit_json(msg="No changes required.", changed=False)


def main():
    OpenBmcSessionModule().run()


if __name__ == "__main__":
    main()
