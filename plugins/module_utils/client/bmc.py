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
    if not isinstance(payload, schema["type"]):
        raise SchemaValidationException("Payload type is wrong: {0} != {1}".format(type(payload), schema["type"]))
    if "suboptions" in schema:
        extra_keys = set(payload.keys()).difference(schema["suboptions"].keys())
        if extra_keys:
            raise SchemaValidationException("Payload has extra keys: {0}".format(extra_keys))
        for option_name, option_schema in schema["suboptions"].items():
            if option_name in payload:
                validate_schema(option_schema, payload[option_name])
            elif "required" in option_schema and option_schema["required"]:
                raise SchemaValidationException("Payload required field missed: {0}".format(option_name))
    elif "elements" in schema:
        for element in payload:
            validate_schema(schema["elements"], element)
    return True


def parse_members(data):
    return [member["@odata.id"].split("/")[-1] for member in data["Members"]]


class OpenBmcRestClient(RestClient):

    manager_name = None
    system_name = None

    def __init__(self, *args, **kwargs):
        super(OpenBmcRestClient, self).__init__(*args, **kwargs)

    def get_system_collection(self):
        data = self.get("/Systems").json_data
        return parse_members(data)

    def get_system_by_id(self, system_id):
        data = self.get("/Systems/{0}".format(system_id)).json_data
        return {
            "Id": data["Id"],
            "Model": data["Model"],
        }

    def get_system(self):
        return self.get_system_by_id(self.system_name)

    def get_managers_collection(self):
        data = self.get("/Managers").json_data
        return parse_members(data)

    def get_manager(self):
        data = self.get("/Managers/{0}".format(self.manager_name)).json_data
        return {
            "Id": data["Id"],
            "Links": {
                "ActiveSoftwareImage": data["Links"]["ActiveSoftwareImage"]["@odata.id"].split("/")[-1]
            }
        }

    def get_software_inventory(self, software_id):
        data = self.get("/UpdateService/FirmwareInventory/{0}".format(software_id)).json_data
        return {
            "Id": data["Id"],
            "Status": data["Status"],
            "Updateable": data["Updateable"],
            "Version": data["Version"],
        }

    def get_account_collection(self):
        data = self.get("/AccountService/Accounts").json_data
        return parse_members(data)

    def get_account(self, username):
        data = self.get("/AccountService/Accounts/{0}".format(username)).json_data
        return {
            "Id": data["Id"],
            "UserName": data["UserName"],
            "Enabled": data["Enabled"],
            "RoleId": data["RoleId"],
        }

    def create_account(self, payload):
        schema = {
            "type": dict,
            "suboptions": {
                "UserName": {"type": str, "required": True},
                "Password": {"type": str, "required": True},
                "RoleId": {"type": str, "required": True},
                "Enabled": {"type": bool, "required": True},
            }
        }
        validate_schema(schema, payload)
        self.post("/AccountService/Accounts", body=payload)

    def update_account(self, username, payload):
        schema = {
            "type": dict,
            "suboptions": {
                "Password": {"type": str, "required": False},
                "RoleId": {"type": str, "required": False},
                "Enabled": {"type": bool, "required": False},
            }
        }
        validate_schema(schema, payload)
        self.patch("/AccountService/Accounts/{0}".format(username), body=payload)

    def delete_account(self, username):
        self.delete("/AccountService/Accounts/{0}".format(username))

    def create_session(self, payload):
        schema = {
            "type": dict,
            "suboptions": {
                "UserName": {"type": str, "required": True},
                "Password": {"type": str, "required": True},
            }
        }
        validate_schema(schema, payload)
        response = self.post("/SessionService/Sessions", body=payload)
        return {
            "id": response.json_data["Id"],
            "key": response.headers["X-Auth-Token"],
        }

    def delete_session(self, session_key):
        self.delete("/SessionService/Sessions/{0}".format(session_key))

    def get_network_protocol(self):
        return self.get("/Managers/{0}/NetworkProtocol".format(self.manager_name)).json_data

    def update_network_protocol(self, payload):
        schema = {
            "type": dict,
            "suboptions": {
                "NTP": {
                    "type": dict,
                    "required": False,
                    "suboptions": {
                        "NTPServers": {"type": list, "required": False},
                        "ProtocolEnabled": {"type": bool, "required": False},
                    }
                }
            }
        }
        validate_schema(schema, payload)
        self.patch("/Managers/{0}/NetworkProtocol".format(self.manager_name), body=payload)

    def get_ethernet_interface_collection(self):
        data = self.get("/Managers/{0}/EthernetInterfaces".format(self.manager_name)).json_data
        return parse_members(data)

    def get_ethernet_interface(self, interface_id):
        data = self.get("/Managers/{0}/EthernetInterfaces/{1}".format(self.manager_name, interface_id)).json_data
        return {
            "Id": data["Id"],
            "DHCPv4": data["DHCPv4"],
            "IPv4StaticAddresses": data["IPv4StaticAddresses"],
            "StaticNameServers": data["StaticNameServers"],
        }

    def update_ethernet_interface(self, interface_id, payload):
        schema = {
            "type": dict,
            "suboptions": {
                "DHCPv4": {
                    "type": dict,
                    "required": False,
                    "suboptions": {
                        "DHCPEnabled": {"type": bool, "required": False},
                        "UseDNSServers": {"type": bool, "required": False},
                        "UseDomainName": {"type": bool, "required": False},
                        "UseNTPServers": {"type": bool, "required": False},
                    }
                },
                "IPv4StaticAddresses": {
                    "type": list,
                    "required": False,
                    "elements": {
                        "type": dict,
                        "suboptions": {
                            "Address": {"type": str, "required": True},
                            "Gateway": {"type": str, "required": True},
                            "SubnetMask": {"type": str, "required": True},
                        }
                    }
                },
                "StaticNameServers": {
                    "type": list,
                    "required": False,
                    "elements": {"type": str}
                }
            }
        }
        validate_schema(schema, payload)
        self.patch("/Managers/{0}/EthernetInterfaces/{1}".format(self.manager_name, interface_id), body=payload)
