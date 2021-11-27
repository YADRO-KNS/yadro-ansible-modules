# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.0.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

try:
    from typing import Optional, ClassVar
except ImportError:
    # Satisfy Python 2 which doesn't have typing.
    Optional = ClassVar = None

from ansible_collections.yadro.obmc.plugins.module_utils.redfish.api.base import RedfishAPIObject


class PCIeFunction(RedfishAPIObject):

    @classmethod
    def select_version(cls, version):  # type: (str) -> Optional[ClassVar[PCIeFunction]]
        if version == "#PCIeFunction.v1_2_0.PCIeFunction":
            return PCIeFunction_v1_2_0

    def get_device_class(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_class_code(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_revision_id(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_vendor_id(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_device_id(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_subsystem_vendor_id(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_subsystem_id(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")


class PCIeFunction_v1_2_0(PCIeFunction):

    def __init__(self, *args, **kwargs):
        super(PCIeFunction_v1_2_0, self).__init__(*args, **kwargs)

    def get_device_class(self):  # type: () -> str
        return self._get_field("DeviceClass")

    def get_class_code(self):  # type: () -> str
        return self._get_field("ClassCode")

    def get_revision_id(self):  # type: () -> str
        return self._get_field("RevisionId")

    def get_vendor_id(self):  # type: () -> str
        return self._get_field("VendorId")

    def get_device_id(self):  # type: () -> str
        return self._get_field("DeviceId")

    def get_subsystem_vendor_id(self):  # type: () -> str
        return self._get_field("SubsystemVendorId")

    def get_subsystem_id(self):  # type: () -> str
        return self._get_field("SubsystemId")
