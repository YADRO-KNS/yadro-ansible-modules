# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.0.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.yadro.obmc.plugins.module_utils.client.bmc import OpenBmcRestClient


class DMTFMockupRestClient(OpenBmcRestClient):

    def __init__(self, *args, **kwargs):
        super(DMTFMockupRestClient, self).__init__(*args, **kwargs)

    def get_manager(self, manager_id):
        data = self.get("/Managers/{0}".format(manager_id)).json_data
        return {
            "Id": data["Id"],
            "Name": data["Name"],
            "Description": data.get("Description", ""),
            "Links": {
                "ActiveSoftwareImage": "BMC"
            }
        }

    def get_software_inventory(self, software_id):
        data = self.get("/UpdateService/FirmwareInventory/{0}".format(software_id)).json_data
        return {
            "Id": data["Id"],
            "Name": data["Name"],
            "Description": data.get("Description", ""),
            "Status": data["Status"].update({"HealthRollup": "OK"}),
            "Updateable": data["Updateable"],
            "Version": data["Version"],
        }

    def create_account(self, username, password, role, enabled):
        data = {
            "@odata.type": "#ManagerAccount..v1_8_0.ManagerAccount",
            "AccountTypes": [
                "Redfish"
            ],
            "Description": "User Account",
            "Enabled": enabled,
            "Id": username,
            "Links": {
                "Role": {
                    "@odata.id": "/redfish/v1/AccountService/Roles/{0}".format(role)
                }
            },
            "Locked": False,
            "Locked@Redfish.AllowableValues": [
                "false"
            ],
            "Name": "User Account",
            "Password": None,
            "PasswordChangeRequired": False,
            "RoleId": role,
            "UserName": username
        }
        self.post("/AccountService/Accounts", body=data)
