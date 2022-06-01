# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.0.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

try:
    from typing import Optional, ClassVar, List, Dict, Any
except ImportError:
    # Satisfy Python 2 which doesn't have typing.
    Optional = ClassVar = List = Dict = Any = None

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
        raise NotImplementedError("Method not implemented")

    def config_ldap(self, service_type, **kwargs):
        # type: (str, ...) -> Dict[str, Any]
        """
        Keyword Arguments:
            uri (str): The address of the external LDAP service
            enabled (bool): An indication of whether this service is enabled
            bind_dn (str): DN of the user who will interact with
                the LDAP service
            password (str): Password of the user who will interact with the
                LDAP service
            base_dn (str): The base distinguished names to use to search
                an external LDAP service
            user_id_attribute (str): The attribute name that contains
                the LDAP username entry
            group_id_attribute (str): The attribute name that contains the
                groups for a user on the LDAP user entry.
            role_groups (list of dict): The mapping rules to convert
                the external account providers account information to the
                local role. The keys are 'name' and 'role'
        """
        raise NotImplementedError("Method not implemented")

    def get_ldap_config(self, service_type):
        # type: (str) -> Dict[str, Any]
        raise NotImplementedError("Method not implemented")

    def get_account_collection(self):  # type: () -> List[Account]
        raise NotImplementedError("Method not implemented")

    def get_role_collection(self):  # type: () -> List[Role]
        raise NotImplementedError("Method not implemented")

    def get_account(self, account_id):  # type: (str) -> Optional[Account]
        raise NotImplementedError("Method not implemented")

    def get_role(self, role_id):  # type: (str) -> Optional[Role]
        raise NotImplementedError("Method not implemented")

    def delete_account(self, account_id):  # type: (str) -> None
        raise NotImplementedError("Method not implemented")


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
        self.reload()

    def config_ldap(self, service_type, **kwargs):
        # type: (str, ...) -> Dict[str, Any]

        data = {}

        if 'uri' in kwargs:
            data['ServiceAddresses'] = [kwargs['uri']]

        if 'enabled' in kwargs:
            data['ServiceEnabled'] = kwargs['enabled']

        is_auth_update = 'bind_dn' in kwargs or 'password' in kwargs
        if is_auth_update:
            data['Authentication'] = {}

        if 'bind_dn' in kwargs:
            data['Authentication']['Username'] = kwargs['bind_dn']

        if 'password' in kwargs:
            data['Authentication']['Password'] = kwargs['password']

        search_settings = {}
        if 'base_dn' in kwargs:
            search_settings['BaseDistinguishedNames'] = [kwargs['base_dn']]

        if 'user_id_attribute' in kwargs:
            search_settings['UsernameAttribute'] = kwargs['user_id_attribute']

        if 'group_id_attribute' in kwargs:
            search_settings['GroupsAttribute'] = kwargs['group_id_attribute']

        if len(search_settings) > 0:
            data['LDAPService'] = {'SearchSettings': search_settings}

        if 'role_groups' in kwargs:
            data['RemoteRoleMapping'] = []

            role_groups = kwargs['role_groups']
            if not isinstance(role_groups, list):
                role_groups = [role_groups]

            for group in role_groups:
                group_data = None if group is None else {
                    'RemoteGroup': group['name'],
                    'LocalRole': group['role'],
                }
                data['RemoteRoleMapping'].append(group_data)

        # We have to know actual state of other services
        self.reload()

        ad_enabled = 'ActiveDirectory' in self._data \
                     and self._data['ActiveDirectory']['ServiceEnabled']

        ldap_enabled = 'LDAP' in self._data \
                       and self._data['LDAP']['ServiceEnabled']

        if service_type == 'LDAP' and ad_enabled:
            self._client.patch(
                self._path,
                body={'ActiveDirectory': {'ServiceEnabled': False}},
            )
        elif service_type == 'ActiveDirectory' and ldap_enabled:
            self._client.patch(
                self._path,
                body={'LDAP': {'ServiceEnabled': False}},
            )

        payload = {service_type: data}
        self._client.patch(self._path, payload)
        self.reload()

        return self.get_ldap_config(service_type)

    def get_ldap_config(self, service_type):
        # type: (str) -> Dict[str, Any]

        data = self._data[service_type]
        search_settings = data['LDAPService']['SearchSettings']

        role_groups = []
        for role in data['RemoteRoleMapping']:
            role_groups.append({
                'name': role['RemoteGroup'],
                'role': role['LocalRole'],
            })

        rv = {
            'uri': data['ServiceAddresses'][0],
            'enabled': data['ServiceEnabled'],
            'bind_dn': data['Authentication']['Username'],
            'password': data['Authentication']['Password'],
            'base_dn': search_settings['BaseDistinguishedNames'][0],
            'user_id_attribute': search_settings['UsernameAttribute'],
            'group_id_attribute': search_settings['GroupsAttribute'],
            'role_groups': role_groups,
        }

        return rv

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
        self.reload()


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
        self.reload()
