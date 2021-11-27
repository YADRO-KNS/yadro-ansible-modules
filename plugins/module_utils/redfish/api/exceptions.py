# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.0.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.yadro.obmc.plugins.module_utils.redfish.exceptions import RedfishError


class RedfishAPIError(RedfishError):
    pass


class RedfishFieldNotFoundError(RedfishAPIError):

    def __init__(self, name):  # type: (str) -> None
        self.name = name

    def __str__(self):  # type: () -> str
        return "Field not found: {0}".format(self.name)


class RedfishModelLoadError(RedfishAPIError):
    pass


class RedfishModelVersionError(RedfishAPIError):

    def __init__(self, version):  # type: (str) -> None
        self.version = version

    def __str__(self):  # type: () -> str
        return "Redfish object unsupported: {0}".format(self.version)
