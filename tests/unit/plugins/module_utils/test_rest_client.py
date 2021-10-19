# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.0.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest
import json

from ansible_collections.yadro.obmc.plugins.module_utils.client.rest import build_url, RestClient, RestClientError
from ansible_collections.yadro.obmc.tests.unit.compat.mock import MagicMock
from ansible.module_utils.urls import open_url, SSLValidationError, ConnectionError
from ansible.module_utils.six.moves.urllib.error import URLError, HTTPError

MODULE_UTIL_PATH = "ansible_collections.yadro.obmc.plugins.module_utils."


class TestRestClinet:

    @pytest.fixture
    def rest_client_kwargs(self):
        return {
            "hostname": "localhost",
            "username": "username",
            "password": "password",
            "base_prefix": "/redfish/v1/",
            "validate_certs": True,
            "port": 443,
            "timeout": 30,
        }

    @pytest.fixture
    def rest_client(self, rest_client_kwargs):
        return RestClient(**rest_client_kwargs)

    @pytest.fixture
    def open_url_expected_kwargs(self):
        default_args = {
            "url": "https://localhost:443/redfish/v1/testpath",
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
        return default_args

    @pytest.fixture
    def open_url_response_mock(self):
        response_mock = MagicMock()
        response_mock.read.return_value = json.dumps({"json": "data"})
        response_mock.getcode.return_value = 200
        response_mock.headers = {"Content-Type": "application/json"}
        return response_mock

    def test_build_url_with_query_args(self):
        expected = "https://localhost/path?key=value"
        result = build_url("https://localhost", "path", {"key": "value"})
        assert result == expected

    def test_base_url_with_hostname_protocol(self, rest_client_kwargs):
        rest_client_kwargs["hostname"] = "https://localhost"
        client = RestClient(**rest_client_kwargs)
        assert client.base_url == "https://localhost:443/redfish/v1/"

    def test_base_url_without_hostname_protocol(self, rest_client_kwargs):
        rest_client_kwargs["hostname"] = "localhost"
        client = RestClient(**rest_client_kwargs)
        assert client.base_url == "https://localhost:443/redfish/v1/"

    def test_open_url_params_with_get_request(self, mocker, rest_client, open_url_expected_kwargs):
        mock = mocker.patch(MODULE_UTIL_PATH + "client.rest.open_url")
        open_url_expected_kwargs["method"] = "GET"
        rest_client.get("/testpath")
        mock.assert_called_with(**open_url_expected_kwargs)

    def test_open_url_params_with_get_request_query(self, mocker, rest_client, open_url_expected_kwargs):
        mock = mocker.patch(MODULE_UTIL_PATH + "client.rest.open_url")
        open_url_expected_kwargs["method"] = "GET"
        open_url_expected_kwargs["url"] = "https://localhost:443/redfish/v1/testpath?key=value"
        rest_client.get("/testpath", query_params={"key": "value"})
        mock.assert_called_with(**open_url_expected_kwargs)

    def test_open_url_params_with_token(self, mocker, rest_client, open_url_expected_kwargs):
        mock = mocker.patch(MODULE_UTIL_PATH + "client.rest.open_url")
        headers = {"X-Auth-Token": "token"}
        open_url_expected_kwargs.pop("url_username")
        open_url_expected_kwargs.pop("url_password")
        open_url_expected_kwargs.update({
            "method": "GET",
            "headers": headers,
            "force_basic_auth": False,
        })
        rest_client.get("/testpath", headers=headers)
        mock.assert_called_with(**open_url_expected_kwargs)

    def test_open_url_params_with_extra_headers(self, mocker, rest_client, open_url_expected_kwargs):
        mock = mocker.patch(MODULE_UTIL_PATH + "client.rest.open_url")
        headers = {"Extra": "Header"}
        open_url_expected_kwargs.update({
            "method": "GET",
            "headers": headers,
        })
        rest_client.get("/testpath", headers=headers)
        mock.assert_called_with(**open_url_expected_kwargs)

    def test_open_url_params_with_token_and_extra_headers(self, mocker, rest_client, open_url_expected_kwargs):
        mock = mocker.patch(MODULE_UTIL_PATH + "client.rest.open_url")
        headers = {"X-Auth-Token": "token", "Extra": "Header"}
        open_url_expected_kwargs.pop("url_username")
        open_url_expected_kwargs.pop("url_password")
        open_url_expected_kwargs.update({
            "method": "GET",
            "headers": headers,
            "force_basic_auth": False,
        })
        rest_client.get("/testpath", headers=headers)
        mock.assert_called_with(**open_url_expected_kwargs)

    def test_open_url_params_with_post_json_data(self, mocker, rest_client, open_url_expected_kwargs):
        mock = mocker.patch(MODULE_UTIL_PATH + "client.rest.open_url")
        body = {"json": "data"}
        open_url_expected_kwargs.update({
            "method": "POST",
            "data": json.dumps(body),
            "headers": {
                "Content-Type": "application/json",
            }
        })
        rest_client.post("/testpath", body=body)
        mock.assert_called_with(**open_url_expected_kwargs)

    def test_open_url_params_with_post_bytes_data(self, mocker, rest_client, open_url_expected_kwargs):
        mock = mocker.patch(MODULE_UTIL_PATH + "client.rest.open_url")
        body = b"bytes data"
        open_url_expected_kwargs.update({
            "method": "POST",
            "data": body,
            "headers": {
                "Content-Type": "application/octet-stream",
            }
        })
        rest_client.post("/testpath", body=body)
        mock.assert_called_with(**open_url_expected_kwargs)

    def test_open_url_params_with_delete_request(self, mocker, rest_client, open_url_expected_kwargs):
        mock = mocker.patch(MODULE_UTIL_PATH + "client.rest.open_url")
        open_url_expected_kwargs["method"] = "DELETE"
        rest_client.delete("/testpath")
        mock.assert_called_with(**open_url_expected_kwargs)

    def test_open_url_params_with_patch_json_data(self, mocker, rest_client, open_url_expected_kwargs):
        mock = mocker.patch(MODULE_UTIL_PATH + "client.rest.open_url")
        body = {"json": "data"}
        open_url_expected_kwargs.update({
            "method": "PATCH",
            "data": json.dumps(body),
            "headers": {
                "Content-Type": "application/json",
            }
        })
        rest_client.patch("/testpath", body=body)
        mock.assert_called_with(**open_url_expected_kwargs)

    def test_client_fail_if_body_unsuppported(self, rest_client):
        with pytest.raises(RestClientError):
            rest_client.post("/testpath", body=("unsupported", "body"))

    def test_response_with_get_request(self, mocker, rest_client, open_url_response_mock):
        mocker.patch(MODULE_UTIL_PATH + "client.rest.open_url", return_value=open_url_response_mock)
        response = rest_client.get("/testpath")
        assert response.status_code == 200
        assert response.json_data == {"json": "data"}
        assert response.headers == {"Content-Type": "application/json"}

    def test_response_fail_with_get_request(self, mocker, rest_client, open_url_response_mock):
        open_url_response_mock.getcode.return_value = 500
        mocker.patch(MODULE_UTIL_PATH + "client.rest.open_url", return_value=open_url_response_mock)
        response = rest_client.get("/testpath")
        assert response.status_code == 500
        assert response.json_data == {"json": "data"}
        assert response.headers == {"Content-Type": "application/json"}

    def test_response_with_post_request(self, mocker, rest_client, open_url_response_mock):
        mocker.patch(MODULE_UTIL_PATH + "client.rest.open_url", return_value=open_url_response_mock)
        response = rest_client.post("/testpath", body={"key": "value"})
        assert response.status_code == 200
        assert response.json_data == {"json": "data"}
        assert response.headers == {"Content-Type": "application/json"}

    @pytest.mark.parametrize("exception", [URLError, SSLValidationError, ConnectionError])
    def test_client_connection_exceptions_passthrough(self, mocker, rest_client, open_url_response_mock, exception):
        mock = mocker.patch(MODULE_UTIL_PATH + "client.rest.open_url", return_value=open_url_response_mock)
        mock.side_effect = exception("Test Exception")
        with pytest.raises(exception):
            rest_client.get("/testpath")

    def test_client_http_exceptions_passthrough(self, mocker, rest_client, open_url_response_mock):
        mock = mocker.patch(MODULE_UTIL_PATH + "client.rest.open_url", return_value=open_url_response_mock)
        mock.side_effect = HTTPError("localhost", 400, "Bad Request Error", {}, None)
        with pytest.raises(HTTPError):
            rest_client.get("/testpath")
