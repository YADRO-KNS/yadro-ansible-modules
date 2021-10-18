# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.0.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.yadro.obmc.plugins.module_utils.client.bmc import OpenBmcRestClient, validate_schema


class DMTFMockupRestClient(OpenBmcRestClient):

    def __init__(self, *args, **kwargs):
        super(DMTFMockupRestClient, self).__init__(*args, **kwargs)

    def create_account(self, payload):
        schema = {
            "UserName": {"required": True, "type": str},
            "Password": {"required": True, "type": str},
            "RoleId": {"required": True, "type": str},
            "Enabled": {"required": False, "type": bool},
        }
        validate_schema(schema, payload)

        data = {
            "@odata.type": "#ManagerAccount..v1_8_0.ManagerAccount",
            "AccountTypes": [
                "Redfish"
            ],
            "Description": "User Account",
            "Enabled": payload["Enabled"],
            "Id": payload["UserName"],
            "Links": {
                "Role": {
                    "@odata.id": "/redfish/v1/AccountService/Roles/{0}".format(payload["RoleId"])
                }
            },
            "Locked": False,
            "Locked@Redfish.AllowableValues": [
                "false"
            ],
            "Name": "User Account",
            "Password": None,
            "PasswordChangeRequired": False,
            "RoleId": payload["RoleId"],
            "UserName": payload["UserName"],
        }
        self.post("/AccountService/Accounts", body=data)
