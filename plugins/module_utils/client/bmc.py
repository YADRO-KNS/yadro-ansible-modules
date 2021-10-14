# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.0.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.yadro.obmc.plugins.module_utils.client.rest import RestClient


def _parse_members(data):
    return [member["@odata.id"].split("/")[-1] for member in data["Members"]]


class OpenBmcRestClient(RestClient):

    def __init__(self, *args, **kwargs):
        super(OpenBmcRestClient, self).__init__(*args, **kwargs)

    def get_chassis_collection(self):
        data = self.get("/Chassis").json_data
        return _parse_members(data)

    def get_system_collection(self):
        data = self.get("/Systems").json_data
        return _parse_members(data)

    def get_manager_collection(self):
        data = self.get("/Managers").json_data
        return _parse_members(data)

    def get_account_collection(self):
        data = self.get("/AccountService/Accounts").json_data
        return _parse_members(data)

    def get_software_inventory_collection(self):
        data = self.get("/UpdateService/FirmwareInventory").json_data
        return _parse_members(data)

    def get_system(self, system_id):
        data = self.get("/Systems/{0}".format(system_id)).json_data
        return {"Id": data["Id"], "Model": data["Model"]}

    def get_manager(self, manager_id):
        data = self.get("/Managers/{0}".format(manager_id)).json_data
        return {
            "Id": data["Id"],
            "Name": data["Name"],
            "Description": data.get("Description", ""),
            "Links": {
                "ActiveSoftwareImage": data["Links"]["ActiveSoftwareImage"]["@odata.id"].split("/")[-1]
            }
        }

    def get_account(self, account_id):
        data = self.get("/AccountService/Accounts/{0}".format(account_id)).json_data
        return {
            "Id": data["Id"],
            "Name": data["Name"],
            "UserName": data["UserName"],
            "Description": data.get("Description", ""),
            "Enabled": data["Enabled"],
            "RoleId": data["RoleId"]
        }

    def get_software_inventory(self, software_id):
        data = self.get("/UpdateService/FirmwareInventory/{0}".format(software_id)).json_data
        return {
            "Id": data["Id"],
            "Name": data["Name"],
            "Description": data.get("Description", ""),
            "Status": data["Status"],
            "Updateable": data["Updateable"],
            "Version": data["Version"],
        }

    def create_account(self, account_id, password, role, enabled):
        data = {
            "UserName": account_id,
            "Password": password,
            "RoleId": role,
            "Enabled": enabled
        }
        self.post("/AccountService/Accounts", body=data)

    def update_account(self, account_id, password=None, role=None, enabled=None):
        data = {}
        if password:
            data["Password"] = password
        if role:
            data["RoleId"] = role
        if enabled is not None:
            data["Enabled"] = enabled
        if data:
            self.patch("/AccountService/Accounts/{0}".format(account_id), body=data)

    def delete_account(self, account_id):
        self.delete("/AccountService/Accounts/{0}".format(account_id))
