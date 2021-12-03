# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.0.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

try:
    from typing import Optional, ClassVar, List
except ImportError:
    # Satisfy Python 2 which doesn't have typing.
    Optional = ClassVar = List = None

from ansible_collections.yadro.obmc.plugins.module_utils.redfish.api.base import RedfishAPIObject
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.api.exceptions import RedfishFieldNotFoundError


class ManagerNetworkProtocol(RedfishAPIObject):

    @classmethod
    def select_version(cls, version):  # type: (str) -> Optional[ClassVar[ManagerNetworkProtocol]]
        if version == "#ManagerNetworkProtocol.v1_5_0.ManagerNetworkProtocol":
            return ManagerNetworkProtocol_v1_5_0

    def get_hostname(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_ntp_enabled(self):  # type: () -> bool
        raise NotImplementedError("Method not implemented")

    def get_ntp_servers(self):  # type: () -> List[str]
        raise NotImplementedError("Method not implemented")

    def set_hostname(self, hostname):  # type: (str) -> None
        raise NotImplementedError("Method not implemented")

    def set_ntp_enabled(self, enabled):  # type: (bool) -> None
        raise NotImplementedError("Method not implemented")

    def set_ntp_servers(self, ntp_servers):  # type: (List[str]) -> None
        raise NotImplementedError("Method not implemented")


class ManagerNetworkProtocol_v1_5_0(ManagerNetworkProtocol):

    def __init__(self, *args, **kwargs):
        super(ManagerNetworkProtocol_v1_5_0, self).__init__(*args, **kwargs)

    def get_hostname(self):  # type: () -> str
        return self._get_field("HostName")

    def get_ntp_enabled(self):  # type: () -> bool
        try:
            return self._data["NTP"]["ProtocolEnabled"]
        except KeyError:
            raise RedfishFieldNotFoundError("['NTP']['ProtocolEnabled']")

    def get_ntp_servers(self):  # type: () -> List[str]
        try:
            return self._data["NTP"]["NTPServers"]
        except KeyError:
            raise RedfishFieldNotFoundError("['NTP']['NTPServers']")

    def set_hostname(self, hostname):  # type: (str) -> None
        if not isinstance(hostname, str):
            raise TypeError("HostName must be string. Received: {0}".format(type(hostname)))
        self._client.patch(self._path, body={"HostName": hostname})
        self.reload()

    def set_ntp_enabled(self, enabled):  # type: (bool) -> None
        if not isinstance(enabled, bool):
            raise TypeError("Enabled must be boolean. Received: {0}".format(type(enabled)))
        self._client.patch(self._path, body={"NTP": {"ProtocolEnabled": enabled}})
        self.reload()

    def set_ntp_servers(self, ntp_servers):  # type: (List[str]) -> None
        if not isinstance(ntp_servers, list):
            raise TypeError("NTP servers must be list. Received: {0}".format(type(ntp_servers)))
        for server in ntp_servers:
            if not isinstance(server, str):
                raise TypeError("NTP server must be string. Received: {0}".format(type(server)))
        self._client.patch(self._path, body={"NTP": {"NTPServers": ntp_servers}})
        self.reload()
