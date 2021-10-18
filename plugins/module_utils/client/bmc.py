# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.0.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.yadro.obmc.plugins.module_utils.client.rest import RestClient


class SchemaValidationException(Exception):
    pass


def validate_schema(schema, payload):
    keys_diff = set(payload.keys()).difference(schema.keys())
    if keys_diff:
        raise SchemaValidationException("Payload extra keys found: {0}".format(keys_diff))

    for schema_key, schema_args in schema.items():
        if schema_key in payload.keys():
            if not isinstance(payload[schema_key], schema_args["type"]):
                raise SchemaValidationException(
                    "Payload key type invalid: {0} is not {1}".format(payload[schema_key], schema_args["type"])
                )
            if "suboptions" in schema_args.keys():
                validate_schema(schema_args["suboptions"], payload[schema_key])
        else:
            if schema_args["required"]:
                raise SchemaValidationException("Required key not found: {0}".format(schema_key))
    return True


def _parse_members(data):
    return [member["@odata.id"].split("/")[-1] for member in data["Members"]]


class OpenBmcRestClient(RestClient):

    def __init__(self, *args, **kwargs):
        super(OpenBmcRestClient, self).__init__(*args, **kwargs)

    def get_chassis_collection(self):
        data = self.get("/Chassis").json_data
        return _parse_members(data)

    def get_manager_collection(self):
        data = self.get("/Managers").json_data
        return _parse_members(data)

    def get_manager(self, manager_id):
        data = self.get("/Managers/{0}".format(manager_id)).json_data
        return {
            "Id": data["Id"],
            "Name": data["Name"],
            "Links": {
                "ActiveSoftwareImage": data["Links"]["ActiveSoftwareImage"]["@odata.id"].split("/")[-1]
            }
        }

    def get_system_collection(self):
        data = self.get("/Systems").json_data
        return _parse_members(data)

    def get_system(self, system_id):
        data = self.get("/Systems/{0}".format(system_id)).json_data
        return {
            "Id": data["Id"],
            "Model": data["Model"],
        }

    def get_software_inventory_collection(self):
        data = self.get("/UpdateService/FirmwareInventory").json_data
        return _parse_members(data)

    def get_software_inventory(self, software_id):
        data = self.get("/UpdateService/FirmwareInventory/{0}".format(software_id)).json_data
        return {
            "Id": data["Id"],
            "Name": data["Name"],
            "Status": data["Status"],
            "Updateable": data["Updateable"],
            "Version": data["Version"],
        }

    def get_account_collection(self):
        data = self.get("/AccountService/Accounts").json_data
        return _parse_members(data)

    def get_account(self, username):
        data = self.get("/AccountService/Accounts/{0}".format(username)).json_data
        return {
            "Id": data["Id"],
            "Name": data["Name"],
            "UserName": data["UserName"],
            "Enabled": data["Enabled"],
            "RoleId": data["RoleId"],
        }

    def create_account(self, payload):
        schema = {
            "UserName": {"required": True, "type": str},
            "Password": {"required": True, "type": str},
            "RoleId": {"required": True, "type": str},
            "Enabled": {"required": False, "type": bool},
        }
        validate_schema(schema, payload)
        self.post("/AccountService/Accounts", body=payload)

    def update_account(self, payload):
        schema = {
            "UserName": {"required": True, "type": str},
            "Password": {"required": False, "type": str},
            "RoleId": {"required": False, "type": str},
            "Enabled": {"required": False, "type": bool},
        }
        validate_schema(schema, payload)
        self.patch("/AccountService/Accounts/{0}".format(payload["UserName"]), body=payload)

    def delete_account(self, username):
        self.delete("/AccountService/Accounts/{0}".format(username))

    def get_network_protocol(self, manager_id):
        data = self.get("/Managers/{0}/NetworkProtocol".format(manager_id)).json_data
        return {
            "Id": data["Id"],
            "Name": data["Name"],
            "NTP": data["NTP"],
        }

    def update_network_protocol(self, manager_id, payload):
        schema = {
            "NTP": {
                "required": False,
                "type": dict,
                "suboptions": {
                    "NTPServers": {"required": False, "type": list},
                    "ProtocolEnabled": {"required": False, "type": bool},
                }
            },
        }
        validate_schema(schema, payload)
        self.patch("/Managers/{0}/NetworkProtocol".format(manager_id), body=payload)
