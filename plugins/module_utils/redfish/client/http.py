# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.0.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

try:
    from typing import Dict
except ImportError:
    # Satisfy Python 2 which doesn't have typing.
    Dict = None

import json
from ansible.module_utils.urls import open_url
from ansible.module_utils.six.moves.urllib.parse import urlencode
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.client.exceptions import HTTPClientError
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.client.response import HTTPClientResponse
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.auth import AuthMethod, NoAuth, BasicAuth, SessionAuth


def build_url(base, path, query_params=None):  # type: (str, str, Dict) -> str
    url = "{0}/{1}".format(base.rstrip("/"), path.lstrip("/"))
    if query_params:
        url += "?" + urlencode(query_params)
    return url


class HTTPClient:

    def __init__(self, hostname, port, validate_certs, timeout, auth):
        # type: (str, int, bool, int, AuthMethod) -> None
        if "://" in hostname:
            self._protocol, self._hostname = hostname.split("://")
        else:
            self._protocol = "https"
            self._hostname = hostname

        self._port = port
        self._base_url = "{0}://{1}:{2}".format(self._protocol, self._hostname, self._port)

        self._auth = auth

        self.validate_certs = validate_certs
        self.timeout = timeout

    def make_request(self, path, method, query_params=None, body=None, headers=None):
        # type: (str, str, Dict, Dict, Dict) -> HTTPClientResponse
        self._make_request(path, method, query_params, body, headers)

    def _make_request(self, path, method, query_params, body, headers):
        # type: (str, str, Dict, Dict, Dict) -> HTTPClientResponse
        request_kwargs = {
            "follow_redirects": "all",
            "force_basic_auth": False,
            "headers": {},
            "method": method,
            "timeout": self.timeout,
            "use_proxy": True,
            "validate_certs": self.validate_certs,
        }

        if body:
            if isinstance(body, dict) or isinstance(body, list):
                request_kwargs["headers"]["Content-Type"] = "application/json"
                request_body = json.dumps(body)
            elif isinstance(body, bytes):
                request_kwargs["headers"]["Content-Type"] = "application/octet-stream"
                request_body = body
            else:
                raise HTTPClientError("Unsupported body type: {0}".format(type(body)))
        else:
            request_body = None

        if isinstance(self._auth, NoAuth):
            pass
        elif isinstance(self._auth, BasicAuth):
            request_kwargs["force_basic_auth"] = True
            request_kwargs["url_username"] = self._auth.username
            request_kwargs["url_password"] = self._auth.password
        elif isinstance(self._auth, SessionAuth):
            request_kwargs["headers"]["X-Auth-Token"] = self._auth.token
        else:
            raise HTTPClientError("Unsupported auth type: {0}".format(type(auth)))

        if headers:
            request_kwargs["headers"].update(headers)

        url = build_url(self._base_url, path, query_params=query_params)
        response = open_url(url=url, data=request_body, **request_kwargs)
        return HTTPClientResponse(response)
