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
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.api.exceptions import RedfishFieldNotFoundError


class ThermalFan(RedfishAPIObject):

    @classmethod
    def select_version(cls, version):  # type: (str) -> Optional[ClassVar[ThermalFan]]
        if version == "#Thermal.v1_4_1.Fan":
            return ThermalFan_v1_4_1

    def get_id(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_part_number(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_model(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_connector(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_manufacturer(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_status(self):  # type: () -> Dict
        raise NotImplementedError("Method not implemented")


class ThermalFan_v1_4_1(ThermalFan):

    def __init__(self, *args, **kwargs):
        super(ThermalFan_v1_4_1, self).__init__(*args, **kwargs)

    def get_id(self):  # type: () -> str
        return self._get_field("@odata.id").split("/")[-1]

    def get_part_number(self):  # type: () -> str
        return self._get_field("PartNumber")

    def get_model(self):  # type: () -> str
        return self._get_field("Model")

    def get_connector(self):  # type: () -> str
        try:
            return self._data["Oem"]["Connector"]
        except KeyError:
            raise RedfishFieldNotFoundError("['Oem']['Connector']")

    def get_manufacturer(self):  # type: () -> str
        return self._get_field("Manufacturer")

    def get_status(self):  # type: () -> Dict
        return self._get_field("Status")
