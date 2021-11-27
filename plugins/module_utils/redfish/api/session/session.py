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


class Session(RedfishAPIObject):

    @classmethod
    def select_version(cls, version):  # type: (str) -> Optional[ClassVar[Session]]
        if version == "#Session.v1_3_0.Session":
            return Session_v1_3_0

    def get_username(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_token(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")


class Session_v1_3_0(Session):

    def __init__(self, *args, **kwargs):
        super(Session_v1_3_0, self).__init__(*args, **kwargs)

    def get_username(self):  # type: () -> str
        return self._get_field("UserName")

    def get_token(self):  # type: () -> str
        return self._get_field("Token")
