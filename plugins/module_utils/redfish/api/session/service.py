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
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.api.session.session import Session


class SessionService(RedfishAPIObject):

    @classmethod
    def select_version(cls, version):  # type: (str) -> Optional[ClassVar[SessionService]]
        if version == "#SessionService.v1_0_2.SessionService":
            return SessionService_v1_0_2

    def get_session_collection(self):  # type: () -> List[Session]
        raise NotImplementedError("Method not implemented")

    def get_session(self, session_id):  # type: (str) -> Optional[Session]
        raise NotImplementedError("Method not implemented")

    def delete_session(self, session_id):  # type: (str) -> None
        raise NotImplementedError("Method not implemented")


class SessionService_v1_0_2(SessionService):

    def __init__(self, *args, **kwargs):
        super(SessionService_v1_0_2, self).__init__(*args, **kwargs)

    def get_session_collection(self):  # type: () -> List[Session]
        sessions = []
        sessions_collection = self._client.get("{0}/Sessions".format(self._path)).json
        for member in sessions_collection["Members"]:
            session_data = self._client.get(member["@odata.id"]).json
            sessions.append(Session.from_json(self._client, session_data))
        return sessions

    def get_session(self, session_id):  # type: (str) -> Optional[Session]
        if not isinstance(session_id, str):
            raise TypeError("Session id must be string. Received: {0}".format(type(session_id)))

        session_path = "{0}/Sessions/{1}".format(self._path, session_id)
        try:
            session_data = self._client.get(session_path).json
        except RESTClientNotFoundError:
            return None
        return Session.from_json(self._client, session_data)

    def delete_session(self, session_id):  # type: (str) -> None
        if not isinstance(session_id, str):
            raise TypeError("Session id must be string. Received: {0}".format(type(session_id)))
        self._client.delete("{0}/Sessions/{1}".format(self._path, session_id))
        self.reload()
