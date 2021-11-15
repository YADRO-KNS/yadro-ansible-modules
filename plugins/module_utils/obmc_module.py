# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.0.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import ConnectionError, SSLValidationError
from ansible.module_utils.six.moves.urllib.error import URLError, HTTPError

from ansible_collections.yadro.obmc.plugins.module_utils.client.client import create_client
from ansible_collections.yadro.obmc.plugins.module_utils.client.auth import BasicAuth, SessionAuth


class OpenBmcModule(AnsibleModule):

    def __init__(self, argument_spec=None, supports_check_mode=False, required_if=None):
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

        # Initialized when module starts
        self.client = None

    def _create_client(self):
        conn = self.params["connection"]
        if conn["session_key"]:
            auth = SessionAuth(conn["session_key"])
        elif conn["username"] and conn["password"]:
            auth = BasicAuth(conn["username"], conn["password"])
        else:
            self.fail_json(msg="Required connection options missed. Username and password "
                               "or session_key must be defined")

        return create_client(conn["hostname"], auth, validate_certs=conn["validate_certs"],
                             port=conn["port"], timeout=conn["timeout"])

    def run(self):
        try:
            self.client = self._create_client()
            self._run()
        except HTTPError as e:
            self.fail_json(msg="Request finished with error.", error_info=json.load(e))
        except (URLError, SSLValidationError, ConnectionError) as e:
            self.fail_json(msg="Can't connect to server.", error_info=str(e))

    def _run(self):
        raise NotImplementedError("Method not implemented!")
