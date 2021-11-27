# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.0.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

try:
    from typing import Optional, ClassVar, List, Dict
except ImportError:
    # Satisfy Python 2 which doesn't have typing.
    Optional = ClassVar = List = Dict = None

from ansible_collections.yadro.obmc.plugins.module_utils.redfish.api.base import RedfishAPIObject
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.client.exceptions import RESTClientNotFoundError
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.api.manager.network_protocol import ManagerNetworkProtocol
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.api.manager.ethernet_interface import EthernetInterface


class Manager(RedfishAPIObject):

    @classmethod
    def select_version(cls, version):  # type: (str) -> Optional[ClassVar[Manager]]
        if version == "#Manager.v1_9_0.Manager":
            return Manager_v1_9_0

    def get_firmware_version(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_service_entry_point_uuid(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_uuid(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_power_state(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_status(self):  # type: () -> Dict
        raise NotImplementedError("Method not implemented")

    def get_graphical_console(self):  # type: () -> Dict
        raise NotImplementedError("Method not implemented")

    def get_serial_console(self):  # type: () -> Dict
        raise NotImplementedError("Method not implemented")

    def get_network_protocol(self):  # type: () -> ManagerNetworkProtocol
        raise NotImplementedError("Method not implemented")

    def get_ethernet_interface_collection(self):  # type: () -> List[EthernetInterface]
        raise NotImplementedError("Method not implemented")

    def get_ethernet_interface(self, interface_id):  # type: () -> Optional[EthernetInterface]
        raise NotImplementedError("Method not implemented")

    def reset_graceful(self):  # type: () -> None
        raise NotImplementedError("Method not implemented")

    def reset_force(self):  # type: () -> None
        raise NotImplementedError("Method not implemented")


class Manager_v1_9_0(Manager):

    def __init__(self, *args, **kwargs):
        super(Manager_v1_9_0, self).__init__(*args, **kwargs)

    def get_firmware_version(self):  # type: () -> str
        return self._get_field("FirmwareVersion")

    def get_service_entry_point_uuid(self):  # type: () -> str
        return self._get_field("ServiceEntryPointUUID")

    def get_uuid(self):  # type: () -> str
        return self._get_field("UUID")

    def get_power_state(self):  # type: () -> str
        return self._get_field("PowerState")

    def get_status(self):  # type: () -> Dict
        return self._get_field("Status")

    def get_graphical_console(self):  # type: () -> Dict
        return self._get_field("GraphicalConsole")

    def get_serial_console(self):  # type: () -> Dict
        return self._get_field("SerialConsole")

    def get_network_protocol(self):  # type: () -> ManagerNetworkProtocol
        network_protocol_data = self._client.get("{0}/NetworkProtocol".format(self._path)).json
        return ManagerNetworkProtocol.from_json(self._client, network_protocol_data)

    def get_ethernet_interface_collection(self):  # type: () -> List[EthernetInterface]
        interfaces = []
        interface_collection = self._client.get("{0}/EthernetInterfaces".format(self._path)).json
        for member in interface_collection["Members"]:
            interface_data = self._client.get(member["@odata.id"]).json
            interfaces.append(EthernetInterface.from_json(self._client, interface_data))
        return interfaces

    def get_ethernet_interface(self, interface_id):  # type: () -> Optional[EthernetInterface]
        if not isinstance(interface_id, str):
            raise TypeError("Interface id must be string. Received: {0}".format(type(interface_id)))

        interface_path = "{0}/EthernetInterfaces/{1}".format(self._path, interface_id)
        try:
            interface_data = self._client.get(interface_path).json
        except RESTClientNotFoundError:
            return None
        return EthernetInterface.from_json(self._client, interface_data)

    def reset_graceful(self): # type: () -> None
        self._client.post("{0}/Actions/Manager.Reset".format(self._path), body={
            "ResetType": "GracefulRestart",
        })

    def reset_force(self): # type: () -> None
        self._client.post("{0}/Actions/Manager.Reset".format(self._path), body={
            "ResetType": "ForceRestart",
        })
