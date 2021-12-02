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
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.api.exceptions import RedfishFieldNotFoundError


class EthernetInterface(RedfishAPIObject):

    @classmethod
    def select_version(cls, version):  # type: (str) -> Optional[ClassVar[EthernetInterface]]
        if version == "#EthernetInterface.v1_4_1.EthernetInterface":
            return EthernetInterface_v1_4_1
        elif version == "#EthernetInterface.v1_4_1.EthernetInterface.Mockup":
            return EthernetInterfaceMockup_v1_4_1

    def get_dhcpv4_enabled(self):  # type: () -> bool
        raise NotImplementedError("Method not implemented")

    def get_static_nameservers(self):  # type: () -> List[str]
        raise NotImplementedError("Method not implemented")

    def get_static_ipv4_addresses(self):  # type: () -> List[Dict]
        raise NotImplementedError("Method not implemented")

    def set_dhcpv4_enabled(self, enabled):  # type: (bool) -> None
        raise NotImplementedError("Method not implemented")

    def set_ipv4_addresses(self, addresses):  # type: (List[Dict]) -> None
        raise NotImplementedError("Method not implemented")

    def set_static_nameservers(self, static_nameservers):  # type: (List[str]) -> None
        raise NotImplementedError("Method not implemented")


class EthernetInterface_v1_4_1(EthernetInterface):

    def __init__(self, *args, **kwargs):
        super(EthernetInterface_v1_4_1, self).__init__(*args, **kwargs)

    def get_dhcpv4_enabled(self):  # type: () -> bool
        try:
            return self._data["DHCPv4"]["DHCPEnabled"]
        except KeyError:
            raise RedfishFieldNotFoundError("['DHCPv4']['DHCPEnabled']")

    def get_static_nameservers(self):  # type: () -> List[str]
        return self._get_field("StaticNameServers")

    def get_static_ipv4_addresses(self):  # type: () -> List[Dict]
        addresses = self._get_field("IPv4StaticAddresses")
        for a in addresses:
            if "AddressOrigin" in a:
                a.pop("AddressOrigin")
        return addresses

    def set_dhcpv4_enabled(self, enabled):  # type: (bool) -> None
        if not isinstance(enabled, bool):
            raise TypeError("Enabled must be boolean. Received: {0}".format(type(enabled)))
        self._client.patch(self._path, body={"DHCPv4": {"DHCPEnabled": enabled}})

    def set_ipv4_addresses(self, addresses):  # type: (List[Dict]) -> None
        if not isinstance(addresses, list):
            raise TypeError("Addresses must be list. Received: {0}".format(type(addresses)))

        for conf in addresses:
            if not isinstance(conf, dict):
                raise TypeError("Address configuration must be a dictionary. Received: {0}".format(type(conf)))
            required_keys = ["Address", "Gateway", "SubnetMask"]
            for k in required_keys:
                if k not in conf or not isinstance(conf[k], str):
                    raise ValueError("Key missed or type invalid: {0}".format(k))
            if len(conf.keys()) > len(required_keys):
                raise ValueError("Address configuration has extra keys. Only {0} allowed and required".format(required_keys))

        self._client.patch(self._path, body={"IPv4StaticAddresses": addresses})

    def set_static_nameservers(self, static_nameservers):  # type: (List[str]) -> None
        if not isinstance(static_nameservers, list):
            raise TypeError("Static nameservers must be list. Received: {0}".format(type(addresses)))

        for server in static_nameservers:
            if not isinstance(server, str):
                raise TypeError("Nameserver must be string. Received: {0}".format(type(server)))

        self._client.patch(self._path, body={"StaticNameServers": static_nameservers})


class EthernetInterfaceMockup_v1_4_1(EthernetInterface_v1_4_1):

    def __init__(self, *args, **kwargs):
        super(EthernetInterfaceMockup_v1_4_1, self).__init__(*args, **kwargs)

    def set_ipv4_addresses(self, addresses):  # type: (List[Dict]) -> None
        super(EthernetInterfaceMockup_v1_4_1, self).set_ipv4_addresses(addresses)
        super(EthernetInterfaceMockup_v1_4_1, self).set_dhcpv4_enabled(False)

    def set_dhcpv4_enabled(self, enabled):  # type: (bool) -> None
        super(EthernetInterfaceMockup_v1_4_1, self).set_dhcpv4_enabled(enabled)
        if enabled:
            super(EthernetInterfaceMockup_v1_4_1, self).set_ipv4_addresses([])
