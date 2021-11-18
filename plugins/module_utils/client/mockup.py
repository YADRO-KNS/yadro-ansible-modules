# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.0.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import copy

from ansible_collections.yadro.obmc.plugins.module_utils.client.bmc import OpenBmcRestClient, validate_schema


class DMTFMockupRestClient(OpenBmcRestClient):

    manager_name = "BMC"
    system_name = "437XR1138R2"

    def __init__(self, *args, **kwargs):
        super(DMTFMockupRestClient, self).__init__(*args, **kwargs)

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

        mockup_payload = copy.deepcopy(payload)
        mockup_payload.update({
            "@odata.type": "#ManagerAccount.v1_8_0.ManagerAccount",
            "AccountTypes": [
                "Redfish"
            ],
            "Description": "User Account",
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
        })
        self.post("/AccountService/Accounts", body=mockup_payload)

    def update_ethernet_interface(self, interface_id, payload):
        schema = {
            "type": dict,
            "suboptions": {
                "HostName": {"type": str, "required": False},
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

        mockup_payload = copy.deepcopy(payload)
        # Simulating real BMC behaviour
        if "IPv4StaticAddresses" in mockup_payload.keys():
            if mockup_payload["IPv4StaticAddresses"]:
                if "DHCPv4" not in mockup_payload.keys():
                    mockup_payload["DHCPv4"] = {}
                mockup_payload["DHCPv4"].update({"DHCPEnabled": False})
                for conf in mockup_payload["IPv4StaticAddresses"]:
                    conf.update({"AddressOrigin": "Static"})

        if "DHCPv4" in mockup_payload.keys():
            if "DHCPEnabled" in mockup_payload["DHCPv4"] and mockup_payload["DHCPv4"]["DHCPEnabled"]:
                mockup_payload["IPv4StaticAddresses"] = []

        self.patch("/Managers/{0}/EthernetInterfaces/{1}".format(self.manager_name, interface_id), body=mockup_payload)

    def create_session(self, payload):
        schema = {
            "type": dict,
            "suboptions": {
                "UserName": {"type": str, "required": True},
                "Password": {"type": str, "required": True},
            }
        }
        validate_schema(schema, payload)
        return {
            "id": "1234567890ABCDEF",
            "key": "MockupSessionKey",
        }

    def delete_session(self, session_key):
        pass
