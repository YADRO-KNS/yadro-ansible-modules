# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.0.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest
import json

from io import StringIO
from ansible.module_utils.urls import SSLValidationError, ConnectionError
from ansible.module_utils.six.moves.urllib.error import URLError, HTTPError
from ansible.module_utils.common.text.converters import to_text
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.auth import BasicAuth
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.client.rest import RESTClient
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.client.exceptions import (
    RESTClientRequestError,
    RESTClientNotFoundError,
    RESTClientConnectionError,
)


class TestRestClient:

    @pytest.fixture
    def default_client_kwargs(self):
        return {
            "hostname": "localhost",
            "port": 443,
            "validate_certs": True,
            "timeout": 30,
            "auth": BasicAuth("username", "password"),
        }

    @pytest.fixture
    def default_client(self, default_client_kwargs):
        return RESTClient(**default_client_kwargs)

    def test_client_response_passthrough(self, mocker, default_client):
        response = "Response"
        mock = mocker.patch("{0}.RESTClient._make_request".format(default_client.__module__), return_value=response)
        assert default_client.get("testpath") == response

    @pytest.mark.parametrize("exception", [URLError, SSLValidationError, ConnectionError])
    def test_client_connection_exceptions(self, mocker, default_client, exception):
        mock = mocker.patch("{0}.RESTClient._make_request".format(default_client.__module__))
        mock.side_effect = exception("Test")
        with pytest.raises(RESTClientConnectionError):
            default_client.get("/testpath")

    def test_client_http_exception(self, mocker, default_client):
        payload = to_text(json.dumps({"Error": "Message"}))
        mock = mocker.patch("{0}.RESTClient._make_request".format(default_client.__module__))
        mock.side_effect = HTTPError("localhost", 400, "Bad Request Error", {}, StringIO(payload))
        with pytest.raises(RESTClientRequestError):
            default_client.get("/testpath")

    def test_client_http_not_found_exception(self, mocker, default_client):
        payload = to_text(json.dumps({"Error": "Message"}))
        mock = mocker.patch("{0}.RESTClient._make_request".format(default_client.__module__))
        mock.side_effect = HTTPError("localhost", 404, "Bad Request Error", {}, StringIO(payload))
        with pytest.raises(RESTClientNotFoundError):
            default_client.get("/testpath")
