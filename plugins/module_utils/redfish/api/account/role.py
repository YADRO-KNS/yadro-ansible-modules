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


class Role(RedfishAPIObject):

    @classmethod
    def select_version(cls, version):  # type: (str) -> Optional[ClassVar[Role]]
        if version == "#Role.v1_2_2.Role":
            return Role_v1_2_2


class Role_v1_2_2(Role):

    def __init__(self, *args, **kwargs):
        super(Role_v1_2_2, self).__init__(*args, **kwargs)
