# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.0.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

try:
    from typing import Optional, ClassVar, Dict, List
except ImportError:
    # Satisfy Python 2 which doesn't have typing.
    Optional = ClassVar = Dict = List = None

from ansible_collections.yadro.obmc.plugins.module_utils.redfish.api.base import RedfishAPIObject
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.api.system.processor import Processor
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.api.system.pcie_device import PCIeDevice
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.api.system.memory import Memory
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.api.system.bios import Bios


class System(RedfishAPIObject):

    @classmethod
    def select_version(cls, version):  # type: (str) -> Optional[ClassVar[System]]
        if version == "#ComputerSystem.v1_13_0.ComputerSystem":
            return System_v1_13_0

    def get_bios(self):  # type: () -> Bios
        raise NotImplementedError("Method not implemented")

    def get_model(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_part_number(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_serial_number(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_status(self):  # type: () -> Dict
        raise NotImplementedError("Method not implemented")

    def get_manufacturer(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_processor_collection(self):  # type: () -> List[Processor]
        raise NotImplementedError("Method not implemented")

    def get_pcie_device_collection(self):  # type: () -> List[PCIeDevice]
        raise NotImplementedError("Method not implemented")

    def get_memory_collection(self):  # type: () -> List[Memory]
        raise NotImplementedError("Method not implemented")

    def get_boot_source_override(self):  # type: () -> Dict
        raise NotImplementedError("Method not implemented")

    def set_boot_source_override(self, config):  # type: (Dict) -> None
        raise NotImplementedError("Method not implemented")

    def get_power_state(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def power_on_graceful(self):  # type: () -> None
        raise NotImplementedError("Method not implemented")

    def power_on_force(self):  # type: () -> None
        raise NotImplementedError("Method not implemented")

    def power_off_graceful(self):  # type: () -> None
        raise NotImplementedError("Method not implemented")

    def power_off_force(self):  # type: () -> None
        raise NotImplementedError("Method not implemented")

    def power_reset_graceful(self):  # type: () -> None
        raise NotImplementedError("Method not implemented")

    def power_reset_force(self):  # type: () -> None
        raise NotImplementedError("Method not implemented")


class System_v1_13_0(System):

    def __init__(self, *args, **kwargs):
        super(System_v1_13_0, self).__init__(*args, **kwargs)

    def get_bios(self):  # type: () -> Bios
        bios_data = self._client.get("{0}/Bios".format(self._path)).json
        return Bios.from_json(self._client, bios_data)

    def get_model(self):  # type: () -> str
        return self._get_field("Model")

    def get_part_number(self):  # type: () -> str
        return self._get_field("PartNumber")

    def get_serial_number(self):  # type: () -> str
        return self._get_field("SerialNumber")

    def get_status(self):  # type: () -> Dict
        return self._get_field("Status")

    def get_manufacturer(self):  # type: () -> str
        return self._get_field("Manufacturer")

    def get_processor_collection(self):  # type: () -> List[Processor]
        processors = []
        processors_collection = self._client.get("{0}/Processors".format(self._path)).json
        for member in processors_collection["Members"]:
            processor_data = self._client.get(member["@odata.id"]).json
            processors.append(Processor.from_json(self._client, processor_data))
        return processors

    def get_pcie_device_collection(self):  # type: () -> List[PCIeDevice]
        pcie_devices = []
        pcie_devices_collection = self._client.get("{0}/PCIeDevices".format(self._path)).json
        for member in pcie_devices_collection["Members"]:
            pcie_device_data = self._client.get(member["@odata.id"]).json
            pcie_devices.append(PCIeDevice.from_json(self._client, pcie_device_data))
        return pcie_devices

    def get_memory_collection(self):  # type: () -> List[Memory]
        memory = []
        memory_collection = self._client.get("{0}/Memory".format(self._path)).json
        for member in memory_collection["Members"]:
            memory_data = self._client.get(member["@odata.id"]).json
            memory.append(Memory.from_json(self._client, memory_data))
        return memory

    def get_boot_source_override(self):  # type: () -> Dict
        return self._get_field("Boot")

    def set_boot_source_override(self, config):  # type: (Dict) -> None
        if not isinstance(config, dict):
            raise TypeError("Configuration must be dictionary. Received: {0}".format(type(config)))

        known_keys = ["BootSourceOverrideEnabled", "BootSourceOverrideMode", "BootSourceOverrideTarget"]
        for k in config.keys():
            if k not in known_keys:
                raise ValueError("Unknown key: {0}".format(k))

        self._client.patch(self._path, body={"Boot": config})
        self.reload()

    def get_power_state(self):  # type: () -> str
        return self._get_field("PowerState")

    def power_on_graceful(self):  # type: () -> None
        self._client.post("{0}/Actions/ComputerSystem.Reset".format(self._path), body={
            "ResetType": "On",
        })

    def power_on_force(self):  # type: () -> None
        self._client.post("{0}/Actions/ComputerSystem.Reset".format(self._path), body={
            "ResetType": "ForceOn",
        })

    def power_off_graceful(self):  # type: () -> None
        self._client.post("{0}/Actions/ComputerSystem.Reset".format(self._path), body={
            "ResetType": "GracefulShutdown",
        })

    def power_off_force(self):  # type: () -> None
        self._client.post("{0}/Actions/ComputerSystem.Reset".format(self._path), body={
            "ResetType": "ForceOff",
        })

    def power_reset_graceful(self):  # type: () -> None
        self._client.post("{0}/Actions/ComputerSystem.Reset".format(self._path), body={
            "ResetType": "GracefulRestart",
        })

    def power_reset_force(self):  # type: () -> None
        self._client.post("{0}/Actions/ComputerSystem.Reset".format(self._path), body={
            "ResetType": "PowerCycle",
        })
