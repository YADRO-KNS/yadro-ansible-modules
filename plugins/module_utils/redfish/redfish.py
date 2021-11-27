# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.0.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

try:
    from typing import Optional
except ImportError:
    # Satisfy Python 2 which doesn't have typing.
    Optional = None

from ansible_collections.yadro.obmc.plugins.module_utils.redfish.auth import AuthMethod, NoAuth, BasicAuth, SessionAuth
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.client.rest import RESTClient
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.api.session.session import Session
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.api.session.service import SessionService
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.api.account.service import AccountService
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.api.update.service import UpdateService
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.api.manager.manager import Manager
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.api.system.system import System
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.api.chassis.chassis import Chassis
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.client.exceptions import RESTClientNotFoundError


class RedfishAPI:

    def __init__(self, hostname, base_prefix="/redfish/v1", port=443, validate_certs=True, timeout=30, auth=NoAuth()):
        # type: (str, str, int, bool, int, AuthMethod) -> None
        self._client = RESTClient(
            auth=auth,
            hostname=hostname,
            port=port,
            validate_certs=validate_certs,
            timeout=timeout
        )
        self._base_prefix = base_prefix

    def create_session(self, username, password):  # type: (str, str) -> Session
        if not isinstance(username, str):
            raise TypeError("Username must be string. Received: {0}".format(type(username)))
        if not isinstance(password, str):
            raise TypeError("Password must be string. Received: {0}".format(type(password)))

        sessions_path = "{0}/SessionService/Sessions".format(self._base_prefix)
        response = self._client.post(sessions_path, body={
            "UserName": username,
            "Password": password,
        })
        session_data = response.json
        session_data["Token"] = response.headers["X-Auth-Token"]
        return Session.from_json(self._client, session_data)

    def get_session_service(self):  # type: () -> SessionService
        session_service_path = "{0}/SessionService".format(self._base_prefix)
        session_service_data = self._client.get(session_service_path).json
        return SessionService.from_json(self._client, session_service_data)

    def get_account_service(self):  # type: () -> AccountService
        account_service_path = "{0}/AccountService".format(self._base_prefix)
        account_service_data = self._client.get(account_service_path).json
        return AccountService.from_json(self._client, account_service_data)

    def get_update_service(self):  # type: () -> UpdateService
        update_service_path = "{0}/UpdateService".format(self._base_prefix)
        update_service_data = self._client.get(update_service_path).json
        return UpdateService.from_json(self._client, update_service_data)

    def get_manager_collection(self):  # type: () -> List[Manager]
        managers = []
        managers_collection = self._client.get("{0}/Managers".format(self._base_prefix)).json
        for member in managers_collection["Members"]:
            manager_data = self._client.get(member["@odata.id"]).json
            managers.append(Manager.from_json(self._client, manager_data))
        return managers

    def get_manager(self, manager_id):  # type: () -> Optional[Manager]
        if not isinstance(manager_id, str):
            raise TypeError("Manager id must be string. Received: {0}".format(type(manager_id)))

        manager_path = "{0}/Managers/{1}".format(self._base_prefix, manager_id)
        try:
            manager_data = self._client.get(manager_path).json
        except RESTClientNotFoundError:
            return None
        return Manager.from_json(self._client, manager_data)

    def get_system_collection(self):  # type: () -> List[System]
        systems = []
        systems_collection = self._client.get("{0}/Systems".format(self._base_prefix)).json
        for member in systems_collection["Members"]:
            system_data = self._client.get(member["@odata.id"]).json
            systems.append(System.from_json(self._client, system_data))
        return systems

    def get_system(self, system_id):  # type: () -> Optional[System]
        if not isinstance(system_id, str):
            raise TypeError("System id must be string. Received: {0}".format(type(system_id)))

        system_path = "{0}/Systems/{1}".format(self._base_prefix, system_id)
        try:
            system_data = self._client.get(system_path).json
        except RESTClientNotFoundError:
            return None
        return System.from_json(self._client, system_data)

    def get_chassis_collection(self):  # type: () -> List[Chassis]
        chassis = []
        chassis_collection = self._client.get("{0}/Chassis".format(self._base_prefix)).json
        for member in chassis_collection["Members"]:
            chassis_data = self._client.get(member["@odata.id"]).json
            chassis.append(Chassis.from_json(self._client, chassis_data))
        return chassis

    def get_chassis(self, chassis_id):  # type: () -> Optional[Chassis]
        if not isinstance(chassis_id, str):
            raise TypeError("Chassis id must be string. Received: {0}".format(type(chassis_id)))

        chassis_path = "{0}/Chassis/{1}".format(self._base_prefix, chassis_id)
        try:
            chassis_data = self._client.get(chassis_path).json
        except RESTClientNotFoundError:
            return None
        return Chassis.from_json(self._client, chassis_data)
