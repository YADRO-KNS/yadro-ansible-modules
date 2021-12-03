# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.0.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest
import json

from ansible_collections.yadro.obmc.tests.unit.compat.mock import MagicMock
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.client.response import HTTPClientResponse


class TestResponse:

    @pytest.fixture
    def http_response_mock(self):
        response_mock = MagicMock()
        response_mock.read.return_value = json.dumps({"json": "data"})
        response_mock.getcode.return_value = 200
        response_mock.headers = {"Content-Type": "application/json"}
        return response_mock

    @pytest.fixture
    def response(self, http_response_mock):
        return HTTPClientResponse(http_response_mock)

    def test_json_load(self, response):
        assert response.json == {"json": "data"}

    def test_json_load_error(self, http_response_mock):
        http_response_mock.read.return_value = "Invalid"
        response = HTTPClientResponse(http_response_mock)
        with pytest.raises(ValueError):
            response.json

    def test_headers(self, response):
        assert response.headers == {"Content-Type": "application/json"}

    def test_status_code(self, response):
        assert response.status_code == 200

    def test_is_success_case00(self, response):
        assert response.is_success

    def test_is_success_case01(self, http_response_mock):
        http_response_mock.getcode.return_value = 500
        response = HTTPClientResponse(http_response_mock)
        assert not response.is_success
