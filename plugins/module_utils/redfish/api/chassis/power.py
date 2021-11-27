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
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.api.chassis.power_supply import PowerSupply


class Power(RedfishAPIObject):

    @classmethod
    def select_version(cls, version):  # type: (str) -> Optional[ClassVar[Power]]
        if version == "#Power.v1_5_2.Power":
            return Power_v1_5_2

    def get_power_supply_collection(self):  # type: () -> List[PowerSupply]
        raise NotImplementedError("Method not implemented")


class Power_v1_5_2(Power):

    def __init__(self, *args, **kwargs):
        super(Power_v1_5_2, self).__init__(*args, **kwargs)

    def get_power_supply_collection(self):  # type: () -> List[PowerSupply]
        supplies = []
        supplies_collection = self._get_field("PowerSupplies")
        for supply_data in supplies_collection:
            supply_data["@odata.type"] = "Unknown"
            supplies.append(PowerSupply.from_json(self._client, supply_data))
        return supplies
