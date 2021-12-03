# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.0.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest
import json

from ansible.module_utils.urls import open_url, SSLValidationError, ConnectionError
from ansible.module_utils.six.moves.urllib.error import URLError, HTTPError
from ansible_collections.yadro.obmc.tests.unit.compat.mock import MagicMock
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.auth import AuthMethod, BasicAuth, SessionAuth, NoAuth
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.client.http import HTTPClient, build_url
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.client.response import HTTPClientResponse
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.client.exceptions import HTTPClientError


class TestHttpClient:

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
        return HTTPClient(**default_client_kwargs)

    @pytest.fixture
    def open_url_kwargs(self):
        return {
            "url": "https://localhost:443/testpath",
            "data": None,
            "method": None,
            "validate_certs": True,
            "use_proxy": True,
            "timeout": 30,
            "follow_redirects": "all",
            "headers": {},
            "force_basic_auth": True,
            "url_username": "username",
            "url_password": "password",
        }

    @pytest.fixture
    def open_url_response_mock(self):
        response_mock = MagicMock()
        response_mock.read.return_value = json.dumps({"json": "data"})
        response_mock.getcode.return_value = 200
        response_mock.headers = {"Content-Type": "application/json"}
        return response_mock

    def test_build_url(self):
        expected = "https://localhost/path"
        result = build_url("https://localhost", "path")
        assert result == expected

    def test_build_url_with_query_args(self):
        expected = "https://localhost/path?key=value"
        result = build_url("https://localhost", "path", {"key": "value"})
        assert result == expected

    def test_base_url(self, default_client_kwargs):
        client = HTTPClient(**default_client_kwargs)
        assert client.get_base_url() == "https://localhost:443"

    def test_base_url_with_protocol(self, default_client_kwargs):
        default_client_kwargs["hostname"] = "http://localhost"
        client = HTTPClient(**default_client_kwargs)
        assert client.get_base_url() == "http://localhost:443"

    def test_open_url_params_with_get_request(self, mocker, default_client, open_url_kwargs):
        mock = mocker.patch("{0}.open_url".format(default_client.__module__))
        open_url_kwargs["method"] = "GET"
        default_client.get("/testpath")
        mock.assert_called_with(**open_url_kwargs)

    def test_open_url_params_with_get_request_and_query_args(self, mocker, default_client, open_url_kwargs):
        mock = mocker.patch("{0}.open_url".format(default_client.__module__))
        open_url_kwargs["url"] = "https://localhost:443/testpath?key=value"
        open_url_kwargs["method"] = "GET"
        default_client.get("/testpath", query_params={"key": "value"})
        mock.assert_called_with(**open_url_kwargs)

    def test_open_url_params_with_no_auth(self, mocker, default_client_kwargs, open_url_kwargs):
        default_client_kwargs["auth"] = NoAuth()
        client = HTTPClient(**default_client_kwargs)
        mock = mocker.patch("{0}.open_url".format(client.__module__))
        open_url_kwargs["force_basic_auth"] = False
        open_url_kwargs.pop("url_username")
        open_url_kwargs.pop("url_password")
        open_url_kwargs.update({
            "method": "GET",
            "headers": {},
        })
        client.get("/testpath")
        mock.assert_called_with(**open_url_kwargs)

    def test_client_fail_if_auth_unsupported(self, mocker, default_client_kwargs):
        default_client_kwargs["auth"] = AuthMethod()
        client = HTTPClient(**default_client_kwargs)
        with pytest.raises(HTTPClientError):
            client.get("/testpath")

    def test_open_url_params_with_session_auth(self, mocker, default_client_kwargs, open_url_kwargs):
        default_client_kwargs["auth"] = SessionAuth("Token")
        client = HTTPClient(**default_client_kwargs)
        mock = mocker.patch("{0}.open_url".format(client.__module__))

        open_url_kwargs["force_basic_auth"] = False
        open_url_kwargs.pop("url_username")
        open_url_kwargs.pop("url_password")
        open_url_kwargs.update({
            "method": "GET",
            "headers": {"X-Auth-Token": "Token"},
        })
        client.get("/testpath")
        mock.assert_called_with(**open_url_kwargs)

    def test_open_url_params_with_extra_headers(self, mocker, default_client, open_url_kwargs):
        mock = mocker.patch("{0}.open_url".format(default_client.__module__))
        headers = {"Extra": "Header"}
        open_url_kwargs.update({
            "method": "GET",
            "headers": headers,
        })
        default_client.get("/testpath", headers=headers)
        mock.assert_called_with(**open_url_kwargs)

    def test_open_url_params_with_session_and_extra_headers(self, mocker, default_client_kwargs, open_url_kwargs):
        default_client_kwargs["auth"] = SessionAuth("Token")
        client = HTTPClient(**default_client_kwargs)
        mock = mocker.patch("{0}.open_url".format(client.__module__))

        open_url_kwargs["force_basic_auth"] = False
        open_url_kwargs.pop("url_username")
        open_url_kwargs.pop("url_password")
        extra_headers = {"Extra": "Header"}
        expected_headers = {"X-Auth-Token": "Token"}
        expected_headers.update(extra_headers)
        open_url_kwargs.update({
            "method": "GET",
            "headers": expected_headers,
        })
        client.get("/testpath", headers=extra_headers)
        mock.assert_called_with(**open_url_kwargs)

    def test_open_url_params_with_post_json_data(self, mocker, default_client, open_url_kwargs):
        mock = mocker.patch("{0}.open_url".format(default_client.__module__))
        body = {"json": "data"}
        open_url_kwargs.update({
            "method": "POST",
            "data": json.dumps(body),
            "headers": {
                "Content-Type": "application/json",
            }
        })
        default_client.post("/testpath", body=body)
        mock.assert_called_with(**open_url_kwargs)

    def test_open_url_params_with_post_bytes_data(self, mocker, default_client, open_url_kwargs):
        mock = mocker.patch("{0}.open_url".format(default_client.__module__))
        body = b"bytes data"
        open_url_kwargs.update({
            "method": "POST",
            "data": body,
            "headers": {
                "Content-Type": "application/octet-stream",
            }
        })
        default_client.post("/testpath", body=body)
        mock.assert_called_with(**open_url_kwargs)

    def test_client_fail_if_body_unsuppported(self, default_client):
        with pytest.raises(HTTPClientError):
            default_client.post("/testpath", body=("unsupported", "body"))

    def test_open_url_params_with_delete_request(self, mocker, default_client, open_url_kwargs):
        mock = mocker.patch("{0}.open_url".format(default_client.__module__))
        open_url_kwargs["method"] = "DELETE"
        default_client.delete("/testpath")
        mock.assert_called_with(**open_url_kwargs)

    def test_open_url_params_with_patch_json_data(self, mocker, default_client, open_url_kwargs):
        mock = mocker.patch("{0}.open_url".format(default_client.__module__))
        body = {"json": "data"}
        open_url_kwargs.update({
            "method": "PATCH",
            "data": json.dumps(body),
            "headers": {
                "Content-Type": "application/json",
            }
        })
        default_client.patch("/testpath", body=body)
        mock.assert_called_with(**open_url_kwargs)

    def test_response_with_get_request(self, mocker, default_client, open_url_response_mock):
        mocker.patch("{0}.open_url".format(default_client.__module__), return_value=open_url_response_mock)
        response = default_client.get("/testpath")

        assert isinstance(response, HTTPClientResponse)
        assert response.status_code == 200
        assert response.json == {"json": "data"}
        assert response.headers == {"Content-Type": "application/json"}

    def test_response_fail_with_get_request(self, mocker, default_client, open_url_response_mock):
        open_url_response_mock.getcode.return_value = 500
        mocker.patch("{0}.open_url".format(default_client.__module__), return_value=open_url_response_mock)
        response = default_client.get("/testpath")

        assert isinstance(response, HTTPClientResponse)
        assert response.status_code == 500
        assert response.json == {"json": "data"}
        assert response.headers == {"Content-Type": "application/json"}

    def test_response_with_post_request(self, mocker, default_client, open_url_response_mock):
        mocker.patch("{0}.open_url".format(default_client.__module__), return_value=open_url_response_mock)
        response = default_client.post("/testpath", body={"key": "value"})

        assert isinstance(response, HTTPClientResponse)
        assert response.status_code == 200
        assert response.json == {"json": "data"}
        assert response.headers == {"Content-Type": "application/json"}

    @pytest.mark.parametrize("exception", [URLError, SSLValidationError, ConnectionError])
    def test_client_connection_exceptions_passthrough(self, mocker, default_client, open_url_response_mock, exception):
        mock = mocker.patch("{0}.open_url".format(default_client.__module__), return_value=open_url_response_mock)
        mock.side_effect = exception("Test Exception")
        with pytest.raises(exception):
            default_client.get("/testpath")

    def test_client_http_exception_passthrough(self, mocker, default_client, open_url_response_mock):
        mock = mocker.patch("{0}.open_url".format(default_client.__module__), return_value=open_url_response_mock)
        mock.side_effect = HTTPError("localhost", 400, "Bad Request Error", {}, None)
        with pytest.raises(HTTPError):
            default_client.get("/testpath")
