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


class SoftwareInventory(RedfishAPIObject):

    @classmethod
    def select_version(cls, version):  # type: (str) -> Optional[ClassVar[SoftwareInventory]]
        if version == "#SoftwareInventory.v1_1_0.SoftwareInventory":
            return SoftwareInventory_v1_1_0

    def get_description(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_updateable(self):  # type: () -> bool
        raise NotImplementedError("Method not implemented")

    def get_version(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_status(self):  # type: () -> Dict
        raise NotImplementedError("Method not implemented")


class SoftwareInventory_v1_1_0(SoftwareInventory):

    def __init__(self, *args, **kwargs):
        super(SoftwareInventory_v1_1_0, self).__init__(*args, **kwargs)

    def get_description(self):  # type: () -> str
        return self._get_field("Description")

    def get_updateable(self):  # type: () -> bool
        return self._get_field("Updateable")

    def get_version(self):  # type: () -> str
        return self._get_field("Version")

    def get_status(self):  # type: () -> Dict
        return self._get_field("Status")
