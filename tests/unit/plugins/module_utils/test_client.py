# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Modules
# Version 1.0.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest
from ansible_collections.yadro.obmc.plugins.module_utils.client import RestClient
from ansible_collections.yadro.obmc.tests.unit.compat.mock import MagicMock

MODULE_UTIL_PATH = "ansible_collections.yadro.obmc.plugins.module_utils.client."

class TestRestClinet:

    @pytest.fixture
    def response_mock(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        return mock_response

    def test_invoke_request_with_session(self, mocker, response_mock):
        mocker.patch(MODULE_UTIL_PATH + 'requests.get', return_value=response_mock)
        params = {
            "base_url": "192.168.0.1",
            "username": "username",
            "password": "password",
        }

        client = RestClient(**params)
        response = client.get("/somepath")
        assert response.status_code == 200

