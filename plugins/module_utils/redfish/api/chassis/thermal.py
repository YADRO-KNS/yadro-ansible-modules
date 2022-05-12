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
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.api.chassis.thermal_fan import ThermalFan


class Thermal(RedfishAPIObject):

    @classmethod
    def select_version(cls, version):  # type: (str) -> Optional[ClassVar[Thermal]]
        if version == "#Thermal.v1_4_0.Thermal":
            return Thermal_v1_4_0

    def get_fan_collection(self):  # type: () -> List[ThermalFan]
        raise NotImplementedError("Method not implemented")


class Thermal_v1_4_0(Thermal):

    def __init__(self, *args, **kwargs):
        super(Thermal_v1_4_0, self).__init__(*args, **kwargs)

    def get_fan_collection(self):  # type: () -> List[ThermalFan]
        fans = []
        fans_collection = self._get_field("Fans")
        for fan_data in fans_collection:
            fans.append(ThermalFan.from_json(self._client, fan_data))
        return fans
