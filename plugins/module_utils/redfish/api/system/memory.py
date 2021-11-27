# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.0.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

try:
    from typing import Optional, ClassVar, Dict
except ImportError:
    # Satisfy Python 2 which doesn't have typing.
    Optional = ClassVar = Dict = None

from ansible_collections.yadro.obmc.plugins.module_utils.redfish.api.base import RedfishAPIObject


class Memory(RedfishAPIObject):

    @classmethod
    def select_version(cls, version):  # type: (str) -> Optional[ClassVar[Memory]]
        if version == "#Memory.v1_7_0.Memory":
            return Memory_v1_7_0

    def get_part_number(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_serial_number(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_device_type(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_status(self):  # type: () -> Dict
        raise NotImplementedError("Method not implemented")

    def get_manufacturer(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_device_locator(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_capacity_mib(self):  # type: () -> int
        raise NotImplementedError("Method not implemented")

    def get_operating_speed_mhz(self):  # type: () -> int
        raise NotImplementedError("Method not implemented")

    def get_data_with_bits(self):  # type: () -> int
        raise NotImplementedError("Method not implemented")

    def get_spare_device_count(self):  # type: () -> int
        raise NotImplementedError("Method not implemented")


class Memory_v1_7_0(Memory):

    def __init__(self, *args, **kwargs):
        super(Memory_v1_7_0, self).__init__(*args, **kwargs)

    def get_part_number(self):  # type: () -> str
        return self._get_field("PartNumber")

    def get_serial_number(self):  # type: () -> str
        return self._get_field("SerialNumber")

    def get_device_type(self):  # type: () -> str
        return self._get_field("MemoryDeviceType")

    def get_status(self):  # type: () -> Dict
        return self._get_field("Status")

    def get_manufacturer(self):  # type: () -> str
        return self._get_field("Manufacturer")

    def get_device_locator(self):  # type: () -> str
        return self._get_field("DeviceLocator")

    def get_capacity_mib(self):  # type: () -> int
        return self._get_field("CapacityMiB")

    def get_operating_speed_mhz(self):  # type: () -> int
        return self._get_field("OperatingSpeedMhz")

    def get_data_with_bits(self):  # type: () -> int
        return self._get_field("DataWidthBits")

    def get_spare_device_count(self):  # type: () -> int
        return self._get_field("SpareDeviceCount")
