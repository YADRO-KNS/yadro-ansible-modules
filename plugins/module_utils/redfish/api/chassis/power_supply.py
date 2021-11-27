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


class PowerSupply(RedfishAPIObject):

    @classmethod
    def select_version(cls, version):  # type: (str) -> Optional[ClassVar[PowerSupply]]
        # PowerSupplies does not have version in BMC
        return PowerSupplyDefault

    def get_id(self):  # type: () -> int
        raise NotImplementedError("Method not implemented")

    def get_serial_number(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_model(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_manufacturer(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_status(self):  # type: () -> Dict
        raise NotImplementedError("Method not implemented")

    def get_product_version(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_firmware_version(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")


class PowerSupplyDefault(PowerSupply):

    def __init__(self, *args, **kwargs):
        super(PowerSupplyDefault, self).__init__(*args, **kwargs)

    def get_id(self):  # type: () -> int
        return self._get_field("@odata.id").split("/")[-1]

    def get_serial_number(self):  # type: () -> str
        return self._get_field("SerialNumber")

    def get_model(self):  # type: () -> str
        return self._get_field("Model")

    def get_manufacturer(self):  # type: () -> str
        return self._get_field("Manufacturer")

    def get_status(self):  # type: () -> Dict
        return self._get_field("Status")

    def get_product_version(self):  # type: () -> str
        try:
            return self._data["Oem"]["PmbusMfrRevision"]
        except KeyError:
            raise RedfishFieldNotFoundError("['Oem']['PmbusMfrRevision']")

    def get_firmware_version(self):  # type: () -> str
        try:
            return self._data["Oem"]["PmbusMfrRevision"]
        except KeyError:
            raise RedfishFieldNotFoundError("['Oem']['CrpsMfrFWRevision']")
