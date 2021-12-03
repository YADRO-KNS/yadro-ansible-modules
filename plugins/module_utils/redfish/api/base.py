# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.0.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

try:
    from typing import ClassVar, Optional, Dict
except ImportError:
    # Satisfy Python 2 which doesn't have typing.
    ClassVar = Optional = Dict = None

from ansible_collections.yadro.obmc.plugins.module_utils.redfish.client.rest import RESTClient
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.api.exceptions import (
    RedfishFieldNotFoundError,
    RedfishModelVersionError,
    RedfishModelLoadError,
)


class RedfishAPIObject:

    def __init__(self, client, path, data):  # type: (RESTClient, str, Dict) -> None
        self._client = client
        self._path = path.rstrip("/")
        self._data = data

    def _get_field(self, name):  # type: (str) -> Any
        try:
            return self._data[name]
        except KeyError:
            raise RedfishFieldNotFoundError(name)

    def reload(self):  # type: () -> None
        self._data = self._client.get(self._path).json

    def get_id(self):  # type: () -> str
        return self._get_field("Id")

    def get_name(self):  # type: () -> str
        return self._get_field("Name")

    @classmethod
    def from_json(cls, client, data):  # type: (RESTClient, Dict) -> RedfishAPIObject
        if not isinstance(client, RESTClient):
            raise TypeError("Client must be RESTClient object. Received: {0}".format(type(client)))
        if not isinstance(data, dict):
            raise TypeError("Data must be dictionary. Received: {0}".format(type(data)))

        if "@odata.id" not in data:
            raise RedfishModelLoadError("Cannot identify object id from data.")
        if "@odata.type" not in data:
            raise RedfishModelLoadError("Cannot identify object type from data.")
        # Manually created field. Exists only on mockup systems.
        # Responsible for additional functionality activating
        if "@odata.mockup" in data and data["@odata.mockup"]:
            version = "{0}.Mockup".format(data["@odata.type"])
        else:
            version = data["@odata.type"]
        impl = cls.select_version(version)
        if impl is None:
            raise RedfishModelVersionError(version)
        return impl(client, data["@odata.id"], data)

    @classmethod
    def select_version(cls, version):  # type: (str) -> Optional[ClassVar[RedfishAPIObject]]
        raise NotImplementedError("Method not implemented")

    def __repr__(self):  # type: () -> str
        return "{0}({1})".format(self.__class__.__name__, self._path)
