# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.0.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.yadro.obmc.plugins.module_utils.client import RestClient


class UnsupporedSystemError(Exception):
    pass


def create_client(hostname, username, password, base_prefix="/redfish/v1/",
                  validate_certs=True, port=443, timeout=10):
    client = OpenBmcRestClient(hostname=hostname, username=username, password=password,
                               base_prefix=base_prefix, validate_certs=validate_certs,
                               port=port, timeout=timeout)

    systems = client.get_system_collection()
    if len(systems) != 1:
        raise UnsupporedSystemError("Operations with only one BMC system supported. Found: {0}"
                                    .format(len(systems)))

    supported_systems = {
        "VEGMAN S220 Server": VegmanBmcRestClient,
        "Mockup Server": DMTFMockupRestClient,
    }

    system_info = client.get_system(systems[0])
    try:
        client.__class__ = supported_systems[system_info["Model"]]
    except KeyError:
        raise UnsupporedSystemError("System unsupported: {0}. Known systems: {1}".format(
            system_info["Model"], supported_systems.keys()))
    return client


class OpenBmcRestClient(RestClient):

    def __init__(self, *args, **kwargs):
        super(OpenBmcRestClient, self).__init__(*args, **kwargs)

    def _parse_members(self, data):
        return [member["@odata.id"].split("/")[-1] for member in data["Members"]]

    def get_chassis_collection(self):
        data = self.get("/Chassis").json_data
        return self._parse_members(data)

    def get_system_collection(self):
        data = self.get("/Systems").json_data
        return self._parse_members(data)

    def get_system(self, system):
        data = self.get("/Systems/{0}".format(system)).json_data
        return {
            "Model": data["Model"],
        }

    def get_manager_collection(self):
        data = self.get("/Managers").json_data
        return self._parse_members(data)

    def _get_manager(self, manager):
        data = self.get("/Managers/{0}".format(manager)).json_data
        return {
            "Name": data["Name"],
            "Description": data.get("Description", ""),
            "Links": {}
        }, data

    def get_software_inventory_collection(self):
        data = self.get("/UpdateService/FirmwareInventory").json_data
        return self._parse_members(data)

    def _get_software_inventory(self, software):
        data = self.get("/UpdateService/FirmwareInventory/{0}".format(software)).json_data
        return {
            "Name": data["Name"],
            "Description": data.get("Description", ""),
            "Status": data["Status"],
            "Updateable": data["Updateable"],
            "Version": data["Version"],
        }, data


class VegmanBmcRestClient(OpenBmcRestClient):

    def __init__(self, *args, **kwargs):
        super(VegmanBmcRestClient, self).__init__(*args, **kwargs)

    def get_manager(self, manager):
        common_fields, data = self._get_manager(manager)
        common_fields["Links"]["ActiveSoftwareImage"] = \
            data["Links"]["ActiveSoftwareImage"]["@odata.id"].split("/")[-1]
        return common_fields

    def get_software_inventory(self, software):
        common_fields, data = self._get_software_inventory(software)
        return common_fields


class DMTFMockupRestClient(OpenBmcRestClient):

    def __init__(self, *args, **kwargs):
        super(DMTFMockupRestClient, self).__init__(*args, **kwargs)

    def get_manager(self, manager):
        common_fields, data = self._get_manager(manager)
        common_fields["Links"]["ActiveSoftwareImage"] = "BMC"
        return common_fields

    def get_software_inventory(self, software):
        common_fields, data = self._get_software_inventory(software)
        common_fields["Status"].update({
            "HealthRollup": "OK"
        })
        return common_fields
