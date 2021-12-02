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
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.client.exceptions import RESTClientNotFoundError
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.api.account.account import Account
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.api.account.role import Role


class AccountService(RedfishAPIObject):

    @classmethod
    def select_version(cls, version):  # type: (str) -> Optional[ClassVar[AccountService]]
        if version == "#AccountService.v1_5_0.AccountService":
            return AccountService_v1_5_0
        elif version == "#AccountService.v1_5_0.AccountService.Mockup":
            return AccountServiceMockup_v1_5_0

    def create_account(self, username, password, role_id, enabled):  # type: (str, str, str, bool) -> None
        raise NotImplemented("Method not implemented")

    def get_account_collection(self):  # type: () -> List[Account]
        raise NotImplemented("Method not implemented")

    def get_role_collection(self):  # type: () -> List[Role]
        raise NotImplemented("Method not implemented")

    def get_account(self, account_id):  # type: (str) -> Optional[Account]
        raise NotImplemented("Method not implemented")

    def get_role(self, role_id):  # type: (str) -> Optional[Role]
        raise NotImplemented("Method not implemented")

    def delete_account(self, account_id):  # type: (str) -> None
        raise NotImplemented("Method not implemented")


class AccountService_v1_5_0(AccountService):

    def __init__(self, *args, **kwargs):
        super(AccountService_v1_5_0, self).__init__(*args, **kwargs)

    def create_account(self, username, password, role_id, enabled):  # type: (str, str, str, bool) -> None
        if not isinstance(username, str):
            raise TypeError("Username must be string. Received: {0}".format(type(username)))
        if not isinstance(password, str):
            raise TypeError("Password must be string. Received: {0}".format(type(password)))
        if not isinstance(role_id, str):
            raise TypeError("Role id must be string. Received: {0}".format(type(role_id)))
        if not isinstance(enabled, bool):
            raise TypeError("Enabled must be boolean. Received: {0}".format(type(enabled)))

        self._client.post("{0}/Accounts".format(self._path), body={
            "UserName": username,
            "Password": password,
            "RoleId": role_id,
            "Enabled": enabled
        })

    def get_account_collection(self):  # type: () -> List[Account]
        accounts = []
        accounts_collection = self._client.get("{0}/Accounts".format(self._path)).json
        for member in accounts_collection["Members"]:
            account_data = self._client.get(member["@odata.id"]).json
            accounts.append(Account.from_json(self._client, account_data))
        return accounts

    def get_role_collection(self):  # type: () -> List[Role]
        roles = []
        roles_collection = self._client.get("{0}/Roles".format(self._path)).json
        for member in roles_collection["Members"]:
            role_data = self._client.get(member["@odata.id"]).json
            roles.append(Role.from_json(self._client, role_data))
        return roles

    def get_account(self, account_id):  # type: (str) -> Optional[Account]
        if not isinstance(account_id, str):
            raise TypeError("Account id must be string. Received: {0}".format(type(account_id)))

        account_path = "{0}/Accounts/{1}".format(self._path, account_id)
        try:
            account_data = self._client.get(account_path).json
        except RESTClientNotFoundError:
            return None
        return Account.from_json(self._client, account_data)

    def get_role(self, role_id):  # type: (str) -> Optional[Role]
        if not isinstance(role_id, str):
            raise TypeError("Role id must be string. Received: {0}".format(type(role_id)))

        role_path = "{0}/Roles/{1}".format(self._path, role_id)
        try:
            role_data = self._client.get(role_path).json
        except RESTClientNotFoundError:
            return None
        return Role.from_json(self._client, role_data)

    def delete_account(self, account_id):  # type: (str) -> None
        if not isinstance(account_id, str):
            raise TypeError("Account id must be string. Received: {0}".format(type(account_id)))
        self._client.delete("{0}/Accounts/{1}".format(self._path, account_id))


class AccountServiceMockup_v1_5_0(AccountService_v1_5_0):

    def __init__(self, *args, **kwargs):
        super(AccountServiceMockup_v1_5_0, self).__init__(*args, **kwargs)

    def create_account(self, username, password, role_id, enabled):  # type: (str, str, str, bool) -> None
        if not isinstance(username, str):
            raise TypeError("Username must be string. Received: {0}".format(type(username)))
        if not isinstance(password, str):
            raise TypeError("Password must be string. Received: {0}".format(type(password)))
        if not isinstance(role_id, str):
            raise TypeError("Role id must be string. Received: {0}".format(type(role_id)))
        if not isinstance(enabled, bool):
            raise TypeError("Enabled must be boolean. Received: {0}".format(type(enabled)))

        self._client.post("{0}/Accounts".format(self._path), body={
            "@odata.type": "#ManagerAccount.v1_4_0.ManagerAccount",
            "AccountTypes": [
                "Redfish"
            ],
            "Description": "User Account",
            "Id": username,
            "Enabled": enabled,
            "RoleId": role_id,
            "Links": {
                "Role": {
                    "@odata.id": "/redfish/v1/AccountService/Roles/{0}".format(role_id)
                }
            },
            "Locked": False,
            "Locked@Redfish.AllowableValues": [
                "false"
            ],
            "Name": "User Account",
            "Password": None,
            "PasswordChangeRequired": False,
        })
