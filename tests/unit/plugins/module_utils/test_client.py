# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.0.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest
import json

from ansible_collections.yadro.obmc.plugins.module_utils.client import (
    build_url,
    RestClient,
    RestClientError,
)
from ansible_collections.yadro.obmc.tests.unit.compat.mock import MagicMock

MODULE_UTIL_PATH = "ansible_collections.yadro.obmc.plugins.module_utils."


class TestRestClinet:

    @pytest.fixture
    def response_mock(self):
        response_mock = MagicMock()
        response_mock.getcode.return_value = 200
        response_mock.headers = response_mock.getheaders.return_value = {"X-Auth-Token": "token"}
        response_mock.read.return_value = json.dumps({"json": "data"})
        return response_mock

    @pytest.fixture
    def request_args(self):
        default_args = {
            "url": "https://localhost:443/redfish/v1/path",
            "data": None,
            "method": None,
            "verify_certs": True,
            "use_proxy": True,
            "timeout": 30,
            "follow_redirects": "all",
            "headers": {},
            "force_basic_auth": True,
            "url_username": "username",
            "url_password": "password",
        }
        return default_args

    def test_build_url(self):
        expected = "https://localhost/path?key=value"
        result = build_url("https://localhost", "path", {"key": "value"})
        assert result == expected

    def test_hostname_with_protocol(self, rest_client_args):
        rest_client_args["hostname"] = "https://localhost"
        client = RestClient(**rest_client_args)
        assert client.base_url == "https://localhost:443/redfish/v1/"

    def test_hostname_without_protocol(self, rest_client):
        assert rest_client.base_url == "https://localhost:443/redfish/v1/"

    def test_request_params(self, mocker, rest_client, request_args):
        mock = mocker.patch(MODULE_UTIL_PATH + "client.open_url")
        response = rest_client.get("/path")
        request_args["method"] = "GET"
        mock.assert_called_with(**request_args)

    def test_request_params_with_token(self, mocker, rest_client, request_args):
        mock = mocker.patch(MODULE_UTIL_PATH + "client.open_url")
        headers = {"X-Auth-Token": "token"}
        response = rest_client.get("/path", headers=headers)
        request_args.pop("url_username")
        request_args.pop("url_password")
        request_args.update({
            "method": "GET",
            "headers": headers,
            "force_basic_auth": False,
        })
        mock.assert_called_with(**request_args)

    def test_request_params_with_extra_headers(self, mocker, rest_client, request_args):
        mock = mocker.patch(MODULE_UTIL_PATH + "client.open_url")
        headers = {"Extra": "Header"}
        response = rest_client.get("/path", headers=headers)
        request_args.update({
            "method": "GET",
            "headers": headers,
        })
        mock.assert_called_with(**request_args)

    def test_request_params_with_token_and_extra_headers(self, mocker, rest_client, request_args):
        mock = mocker.patch(MODULE_UTIL_PATH + "client.open_url")
        headers = {"X-Auth-Token": "token", "Extra": "Header"}
        response = rest_client.get("/path", headers=headers)
        request_args.pop("url_username")
        request_args.pop("url_password")
        request_args.update({
            "method": "GET",
            "headers": headers,
            "force_basic_auth": False,
        })
        mock.assert_called_with(**request_args)

    def test_success_get_request(self, mocker, rest_client, response_mock):
        mocker.patch(MODULE_UTIL_PATH + "client.open_url", return_value=response_mock)
        response = rest_client.get("/path")
        assert response.is_success
        assert response.status_code == 200
        assert response.json_data == {"json": "data"}

    def test_get_request_with_query(self, mocker, rest_client, request_args):
        mock = mocker.patch(MODULE_UTIL_PATH + "client.open_url")
        response = rest_client.get("/path", query_params={"query": "param"})
        request_args.update({"url": "https://localhost:443/redfish/v1/path?query=param", "method": "GET"})
        mock.assert_called_with(**request_args)

    def test_success_post_request(self, mocker, rest_client, response_mock):
        mocker.patch(MODULE_UTIL_PATH + "client.open_url", return_value=response_mock)
        response = rest_client.post("/path", body={"post": "data"})
        assert response.is_success
        assert response.status_code == 200
        assert response.json_data == {"json": "data"}

    def test_post_request_json_data(self, mocker, rest_client, request_args):
        mock = mocker.patch(MODULE_UTIL_PATH + "client.open_url")
        body = {"json": "data"}
        response = rest_client.post("/path", body=body)
        request_args.update({
            "method": "POST",
            "data":  json.dumps(body),
            "headers": {
                "Content-Type": "application/json",
            }
        })
        mock.assert_called_with(**request_args)

    def test_post_request_bytes_data(self, mocker, rest_client, request_args):
        mock = mocker.patch(MODULE_UTIL_PATH + "client.open_url")
        body = b"bytest data"
        response = rest_client.post("/path", body=body)
        request_args.update({
            "method": "POST",
            "data":  body,
            "headers": {
                "Content-Type": "application/octet-stream",
            }
        })
        mock.assert_called_with(**request_args)

    def test_post_request_unsupported_data(self, rest_client):
        with pytest.raises(RestClientError):
            rest_client.post("/path", body=("unsupported", "body"))

    def test_request_exceptions(self):
        # TODO check exceptions:
        # URLError, SSLValidationError, ConnectionError
        # HTTPError
        pass
