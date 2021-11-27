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


class Processor(RedfishAPIObject):

    @classmethod
    def select_version(cls, version):  # type: (str) -> Optional[ClassVar[Processor]]
        if version == "#Processor.v1_9_0.Processor":
            return Processor_v1_9_0

    def get_model(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_socket(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_instruction_set(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_manufacturer(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_architecture(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_type(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_total_cores(self):  # type: () -> int
        raise NotImplementedError("Method not implemented")

    def get_status(self):  # type: () -> Dict
        raise NotImplementedError("Method not implemented")


class Processor_v1_9_0(Processor):

    def __init__(self, *args, **kwargs):
        super(Processor_v1_9_0, self).__init__(*args, **kwargs)

    def get_model(self):  # type: () -> str
        return self._get_field("Model")

    def get_socket(self):  # type: () -> str
        return self._get_field("Socket")

    def get_instruction_set(self):  # type: () -> str
        return self._get_field("InstructionSet")

    def get_manufacturer(self):  # type: () -> str
        return self._get_field("Manufacturer")

    def get_architecture(self):  # type: () -> str
        return self._get_field("ProcessorArchitecture")

    def get_type(self):  # type: () -> str
        return self._get_field("ProcessorType")

    def get_total_cores(self):  # type: () -> int
        return self._get_field("TotalCores")

    def get_status(self):  # type: () -> Dict
        return self._get_field("Status")
