# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.0.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

try:
    from typing import Callable, Tuple, Any, Dict, List
except ImportError:
    # Satisfy Python 2 which doesn't have typing.
    Callable = Tuple = Any = Dict = List = None

import json
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.redfish import RedfishAPI
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.auth import BasicAuth, SessionAuth
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.exceptions import RedfishError


class OpenBmcModule(AnsibleModule):

    def __init__(self, argument_spec=None, supports_check_mode=False, required_if=None):
        # type: (Dict, bool, List) -> None
        _argument_spec = {
            "connection": {
                "required": True,
                "type": "dict",
                "options": {
                    "hostname": {"required": True, "type": "str"},
                    "username": {"required": False, "type": "str"},
                    "password": {"required": False, "type": "str", "no_log": True},
                    "session_key": {"required": False, "type": "str", "no_log": True},
                    "port": {"required": False, "type": "int", "default": 443},
                    "timeout": {"required": False, "type": "int", "default": 30},
                    "validate_certs": {"required": False, "type": "bool", "default": True},
                }
            },
        }
        if argument_spec and isinstance(argument_spec, dict):
            _argument_spec.update(argument_spec)

        super(OpenBmcModule, self).__init__(
            argument_spec=_argument_spec,
            supports_check_mode=supports_check_mode,
            required_if=required_if,
        )

        self.redfish = None  # type: RedfishAPI

    def run(self):  # type: () -> None
        try:
            connection = self.params["connection"]
            if connection["session_key"]:
                auth = SessionAuth(connection["session_key"])
            elif connection["username"] and connection["password"]:
                auth = BasicAuth(connection["username"], connection["password"])
            else:
                self.fail_json(msg="Cannot define authentication method.")

            self.redfish = RedfishAPI(
                hostname=connection["hostname"],
                base_prefix="/redfish/v1",
                port=connection["port"],
                validate_certs=connection["validate_certs"],
                timeout=connection["timeout"],
                auth=auth,
            )

            self._run()
        except RedfishError as e:
            self.fail_json(msg="Operation failed.", error=str(e))

    def _run(self):  # type: () -> None
        raise NotImplementedError("Method not implemented!")
