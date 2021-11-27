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
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.api.system.pcie_function import PCIeFunction


class PCIeDevice(RedfishAPIObject):

    @classmethod
    def select_version(cls, version):  # type: (str) -> Optional[ClassVar[PCIeDevice]]
        if version == "#PCIeDevice.v1_4_0.PCIeDevice":
            return PCIeDevice_v1_4_0

    def get_address(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_model(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_manufacturer(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_function_collection(self):  # type: () -> List[PCIeFunction]
        raise NotImplementedError("Method not implemented")


class PCIeDevice_v1_4_0(PCIeDevice):

    def __init__(self, *args, **kwargs):
        super(PCIeDevice_v1_4_0, self).__init__(*args, **kwargs)

    def get_address(self):  # type: () -> str
        service = []
        bus = []
        device = []
        current = None
        for ch in self.get_id():
            if ch == "S":
                current = service
            elif ch == "B":
                current = bus
            elif ch == "D":
                current = device
            else:
                current.append(ch)
        return "{0}:{1}:{2}".format(''.join(service), ''.join(bus), ''.join(device))

    def get_model(self):  # type: () -> str
        return self._get_field("Model")

    def get_manufacturer(self):  # type: () -> str
        return self._get_field("Manufacturer")

    def get_function_collection(self):  # type: () -> List[PCIeFunction]
        functions = []
        functions_collection = self._client.get("{0}/PCIeFunctions".format(self._path)).json
        for member in functions_collection["Members"]:
            function_data = self._client.get(member["@odata.id"]).json
            functions.append(PCIeFunction.from_json(self._client, function_data))
        return functions
