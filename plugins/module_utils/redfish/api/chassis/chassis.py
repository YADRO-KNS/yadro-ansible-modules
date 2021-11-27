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
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.api.chassis.thermal import Thermal
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.api.chassis.power import Power


class Chassis(RedfishAPIObject):

    @classmethod
    def select_version(cls, version):  # type: (str) -> Optional[ClassVar[Chassis]]
        if version == "#Chassis.v1_14_0.Chassis":
            return Chassis_v1_14_0

    def get_model(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_manufacturer(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_chassis_type(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_power_state(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_status(self):  # type: () -> Dict
        raise NotImplementedError("Method not implemented")

    def get_serial_number(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_part_number(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_thermal(self):  # type: () -> Thermal
        raise NotImplementedError("Method not implemented")

    def get_power(self):  # type: () -> Power
        raise NotImplementedError("Method not implemented")


class Chassis_v1_14_0(Chassis):

    def __init__(self, *args, **kwargs):
        super(Chassis_v1_14_0, self).__init__(*args, **kwargs)

    def get_model(self):  # type: () -> str
        return self._get_field("Model")

    def get_manufacturer(self):  # type: () -> str
        return self._get_field("Manufacturer")

    def get_chassis_type(self):  # type: () -> str
        return self._get_field("ChassisType")

    def get_power_state(self):  # type: () -> str
        return self._get_field("PowerState")

    def get_status(self):  # type: () -> Dict
        return self._get_field("Status")

    def get_serial_number(self):  # type: () -> str
        return self._get_field("SerialNumber")

    def get_part_number(self):  # type: () -> str
        return self._get_field("PartNumber")

    def get_thermal(self):  # type: () -> Thermal
        thermal_data = self._client.get("{0}/Thermal".format(self._path)).json
        return Thermal.from_json(self._client, thermal_data)

    def get_power(self):  # type: () -> Power
        power_data = self._client.get("{0}/Power".format(self._path)).json
        return Power.from_json(self._client, power_data)
