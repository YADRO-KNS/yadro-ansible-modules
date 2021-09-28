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
    OpenBmcClient,
)
from ansible_collections.yadro.obmc.tests.unit.compat.mock import MagicMock

MODULE_UTIL_PATH = "ansible_collections.yadro.obmc.plugins.module_utils."


class TestRestClinet:

    @pytest.fixture
    def mock_response(self):
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response.headers = mock_response.getheaders.return_value = {"X-Auth-Token": "token"}
        mock_response.read.return_value = json.dumps({"key": "value"})
        return mock_response

    def test_build_url(self):
        assert "https://localhost/path?key=value" == build_url("https://localhost", "path", {"key": "value"})

    def test_hostname_with_protocol(self):
        client_kwargs = {
            "hostname": "https://localhost",
            "username": "username",
            "password": "password",
        }
        with pytest.raises(RestClientError):
            client = RestClient(**client_kwargs)

    def test_request_params(self, mocker):
        mock = mocker.patch(MODULE_UTIL_PATH + "client.open_url")

        client_kwargs = {
            "hostname": "localhost",
            "username": "username",
            "password": "password",
            "base_prefix": "/redfish/v1/",
            "verify_certs": True,
            "port": 443,
            "timeout": 30,
        }
        client = RestClient(**client_kwargs)
        response = client.get("/path")

        expected_request_kwargs = {
            "url": "https://localhost:443/redfish/v1/path",
            "data": None,
            "method": "GET",
            "verify_certs": True,
            "use_proxy": True,
            "timeout": 30,
            "follow_redirects": "all",
            "headers": {},
            "force_basic_auth": True,
            "url_username": "username",
            "url_password": "password",
        }
        mock.assert_called_with(**expected_request_kwargs)

    def test_request_params_with_token(self, mocker):
        mock = mocker.patch(MODULE_UTIL_PATH + "client.open_url")

        client_kwargs = {
            "hostname": "localhost",
            "username": "username",
            "password": "password",
            "base_prefix": "/redfish/v1/",
            "verify_certs": True,
            "port": 443,
            "timeout": 30,
        }
        client = RestClient(**client_kwargs)
        response = client.get("/path", headers={"X-Auth-Token": "token"})

        expected_request_kwargs = {
            "url": "https://localhost:443/redfish/v1/path",
            "data": None,
            "method": "GET",
            "verify_certs": True,
            "use_proxy": True,
            "timeout": 30,
            "follow_redirects": "all",
            "headers": {"X-Auth-Token": "token"},
            "force_basic_auth": False,
        }
        mock.assert_called_with(**expected_request_kwargs)

    def test_request_params_with_extra_headers(self, mocker):
        mock = mocker.patch(MODULE_UTIL_PATH + "client.open_url")

        client_kwargs = {
            "hostname": "localhost",
            "username": "username",
            "password": "password",
            "base_prefix": "/redfish/v1/",
            "verify_certs": True,
            "port": 443,
            "timeout": 30,
        }
        client = RestClient(**client_kwargs)
        response = client.get("/path", headers={"Header name": "Header value"})

        expected_request_kwargs = {
            "url": "https://localhost:443/redfish/v1/path",
            "data": None,
            "method": "GET",
            "verify_certs": True,
            "use_proxy": True,
            "timeout": 30,
            "follow_redirects": "all",
            "headers": {"Header name": "Header value"},
            "force_basic_auth": True,
            "url_username": "username",
            "url_password": "password",
        }
        mock.assert_called_with(**expected_request_kwargs)

    def test_request_params_with_token_and_extra_headers(self, mocker):
        mock = mocker.patch(MODULE_UTIL_PATH + "client.open_url")

        client_kwargs = {
            "hostname": "localhost",
            "username": "username",
            "password": "password",
            "base_prefix": "/redfish/v1/",
            "verify_certs": True,
            "port": 443,
            "timeout": 30,
        }
        client = RestClient(**client_kwargs)
        response = client.get("/path", headers={
            "X-Auth-Token": "token",
            "Extra header": "Extra value"
        })

        expected_request_kwargs = {
            "url": "https://localhost:443/redfish/v1/path",
            "data": None,
            "method": "GET",
            "verify_certs": True,
            "use_proxy": True,
            "timeout": 30,
            "follow_redirects": "all",
            "headers": {
                "X-Auth-Token": "token",
                "Extra header": "Extra value"
            },
            "force_basic_auth": False,
        }

        mock.assert_called_with(**expected_request_kwargs)

    def test_get_request(self, mocker, mock_response):
        mocker.patch(MODULE_UTIL_PATH + "client.open_url", return_value=mock_response)

        client_kwargs = {
            "hostname": "localhost",
            "username": "username",
            "password": "password",
        }
        client = RestClient(**client_kwargs)
        response = client.get("/path")

        assert response.is_success
        assert response.status_code == 200
        assert response.json_data == {"key": "value"}

    def test_get_request_with_query(self, mocker):
        mock = mocker.patch(MODULE_UTIL_PATH + "client.open_url")

        client_kwargs = {
            "hostname": "localhost",
            "username": "username",
            "password": "password",
            "base_prefix": "/redfish/v1/",
            "verify_certs": True,
            "port": 443,
            "timeout": 30,
        }
        client = RestClient(**client_kwargs)
        response = client.get("/path", query_params={"key": "value"})

        expected_request_kwargs = {
            "url": "https://localhost:443/redfish/v1/path?key=value",
            "data": None,
            "method": "GET",
            "verify_certs": True,
            "use_proxy": True,
            "timeout": 30,
            "follow_redirects": "all",
            "headers": {},
            "force_basic_auth": True,
            "url_username": "username",
            "url_password": "password",
        }
        mock.assert_called_with(**expected_request_kwargs)

    def test_post_request(self, mocker, mock_response):
        mocker.patch(MODULE_UTIL_PATH + "client.open_url", return_value=mock_response)

        client_kwargs = {
            "hostname": "localhost",
            "username": "username",
            "password": "password",
        }
        client = RestClient(**client_kwargs)
        response = client.post("/path", body={"post": "data"})

        assert response.is_success
        assert response.status_code == 200
        assert response.json_data == {"key": "value"}

    def test_post_request_json_data(self, mocker):
        mock = mocker.patch(MODULE_UTIL_PATH + "client.open_url")

        client_kwargs = {
            "hostname": "localhost",
            "username": "username",
            "password": "password",
            "base_prefix": "/redfish/v1/",
            "verify_certs": True,
            "port": 443,
            "timeout": 30,
        }
        client = RestClient(**client_kwargs)
        response = client.post("/path", body={"json": "data"})

        expected_request_kwargs = {
            "url": "https://localhost:443/redfish/v1/path",
            "data": json.dumps({"json": "data"}),
            "method": "POST",
            "verify_certs": True,
            "use_proxy": True,
            "timeout": 30,
            "follow_redirects": "all",
            "headers": {
                "Content-Type": "application/json",
            },
            "force_basic_auth": True,
            "url_username": "username",
            "url_password": "password",
        }
        mock.assert_called_with(**expected_request_kwargs)

    def test_post_request_bytes_data(self, mocker):
        mock = mocker.patch(MODULE_UTIL_PATH + "client.open_url")

        client_kwargs = {
            "hostname": "localhost",
            "username": "username",
            "password": "password",
            "base_prefix": "/redfish/v1/",
            "verify_certs": True,
            "port": 443,
            "timeout": 30,
        }
        client = RestClient(**client_kwargs)
        response = client.post("/path", body=b"bytes data")

        expected_request_kwargs = {
            "url": "https://localhost:443/redfish/v1/path",
            "data": b"bytes data",
            "method": "POST",
            "verify_certs": True,
            "use_proxy": True,
            "timeout": 30,
            "follow_redirects": "all",
            "headers": {
                "Content-Type": "application/octet-stream",
            },
            "force_basic_auth": True,
            "url_username": "username",
            "url_password": "password",
        }
        mock.assert_called_with(**expected_request_kwargs)

    def test_post_request_unsupported_data(self):
        client_kwargs = {
            "hostname": "localhost",
            "username": "username",
            "password": "password",
        }
        client = RestClient(**client_kwargs)
        with pytest.raises(RestClientError):
            client.post("/path", body=("unsupported", "body"))

    def test_request_exceptions(self):
        # TODO check exceptions:
        # URLError, SSLValidationError, ConnectionError
        # HTTPError
        pass


class TestOpenBmcClient:

    @pytest.fixture
    def mock_response(self):
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response.read.return_value = json.dumps({"Version": "version"})
        return mock_response

    def test_system_info(self, mocker, mock_response):
        mocker.patch(MODULE_UTIL_PATH + "client.open_url", return_value=mock_response)

        client_kwargs = {
            "hostname": "localhost",
            "username": "username",
            "password": "password",
        }
        client = OpenBmcClient(**client_kwargs)
        info = client.get_bmc_system_info()

        expected_info = {
            "firmware": {
                "bios_version": "version",
                "bmc_version": "version",
            }
        }
        assert info == expected_info

    def test_rest_client_exceptions_passthrough(self):
        # TODO check exceptions received from RestClient
        pass
