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


class Account(RedfishAPIObject):

    @classmethod
    def select_version(cls, version):  # type: (str) -> Optional[ClassVar[Account]]
        if version == "#ManagerAccount.v1_4_0.ManagerAccount":
            return Account_v1_4_0

    def get_username(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def get_enabled(self):  # type: () -> bool
        raise NotImplementedError("Method not implemented")

    def get_locked(self):  # type: () -> bool
        raise NotImplementedError("Method not implemented")

    def get_role_id(self):  # type: () -> str
        raise NotImplementedError("Method not implemented")

    def set_password(self, password):  # type: (str) -> None
        raise NotImplementedError("Method not implemented")

    def set_role_id(self, role_id):  # type: (str) -> None
        raise NotImplementedError("Method not implemented")

    def set_enabled(self, enabled):  # type: (bool) -> None
        raise NotImplementedError("Method not implemented")


class Account_v1_4_0(Account):

    def __init__(self, *args, **kwargs):
        super(Account_v1_4_0, self).__init__(*args, **kwargs)

    def get_username(self):  # type: () -> str
        return self._get_field("UserName")

    def get_enabled(self):  # type: () -> bool
        return self._get_field("Enabled")

    def get_locked(self):  # type: () -> bool
        return self._get_field("Locked")

    def get_role_id(self):  # type: () -> str
        return self._get_field("RoleId")

    def set_password(self, password):  # type: (str) -> None
        if not isinstance(password, str):
            raise TypeError("Password must be string. Received: {0}".format(type(password)))
        self._client.patch(self._path, body={"Password": password})

    def set_role_id(self, role_id):  # type: (str) -> None
        if not isinstance(role_id, str):
            raise TypeError("Role id must be string. Received: {0}".format(type(role_id)))
        self._client.patch(self._path, body={"RoleId": role_id})
        self.reload()

    def set_enabled(self, enabled):  # type: (bool) -> None
        if not isinstance(enabled, bool):
            raise TypeError("Enabled must be boolean. Received: {0}".format(type(enabled)))
        self._client.patch(self._path, body={"Enabled": enabled})
        self.reload()
