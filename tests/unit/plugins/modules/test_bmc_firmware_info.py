# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.0.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import pytest

from io import StringIO
from ansible_collections.yadro.obmc.tests.unit.compat.mock import MagicMock
from ansible_collections.yadro.obmc.plugins.modules import bmc_firmware_info
from ansible_collections.yadro.obmc.tests.unit.plugins.modules.utils import ModuleTestCase
from ansible.module_utils.urls import ConnectionError, SSLValidationError
from ansible.module_utils.six.moves.urllib.error import URLError, HTTPError
from ansible.module_utils.common.text.converters import to_text

MODULE_PATH = "ansible_collections.yadro.obmc.plugins.modules."


class TestBmcFirmwareInfo(ModuleTestCase):

    module = bmc_firmware_info

    @pytest.fixture
    def client_mock(self):
        client_mock = MagicMock()
        client_mock.get_manager_collection.return_value = ["BMC"]
        client_mock.get_manager.return_value = {
            "Name": "BMC test manager",
            "Description": "",
            "Links": {
                "ActiveSoftwareImage": "Image name",
            }
        }
        client_mock.get_software_inventory.return_value = {
            "Name": "Image name",
            "Description": "Image description",
        }
        return client_mock

    def test_simple_success_case(self, mocker, client_mock, module_default_args):
        mocker.patch(MODULE_PATH + "bmc_firmware_info.create_client", return_value=client_mock)
        expected_json = {
            "msg": "Firmware information successfully read.",
            "changed": False,
            "firmware_info": {
                "Name": "Image name",
                "Description": "Image description",
            },
        }
        result = self.run_module_expect_exit_json(module_default_args)
        assert result == expected_json

    def test_http_error_passthrough(self, mocker, client_mock, module_default_args):
        error_message = {"Error": "message"}
        http_error = to_text(json.dumps(error_message))
        exception = HTTPError("localhost", 400, "Bad Request Error", {}, StringIO(http_error))
        client_mock.get_manager.side_effect = exception
        mocker.patch(MODULE_PATH + "bmc_firmware_info.create_client", return_value=client_mock)
        expected_json = {
            "msg": "Request finished with error.",
            "error_info": error_message,
            "failed": True,
        }
        result = self.run_module_expect_fail_json(module_default_args)
        assert result == expected_json

    def test_url_error_passthrough(self, mocker, client_mock, module_default_args):
        exception = URLError("URL error")
        client_mock.get_manager.side_effect = exception
        mocker.patch(MODULE_PATH + "bmc_firmware_info.create_client", return_value=client_mock)
        expected_json = {
            "msg": "Can't connect to server.",
            "error_info": str(exception),
            "failed": True,
        }
        result = self.run_module_expect_fail_json(module_default_args)
        assert result == expected_json

    @pytest.mark.parametrize("exception", [ConnectionError, SSLValidationError])
    def test_connection_errors_passthrough(self, mocker, client_mock, module_default_args, exception):
        expected_exc = exception("Test exception")
        client_mock.get_manager.side_effect = expected_exc
        mocker.patch(MODULE_PATH + "bmc_firmware_info.create_client", return_value=client_mock)
        expected_json = {
            "msg": "Can't connect to server.",
            "error_info": str(expected_exc),
            "failed": True,
        }
        result = self.run_module_expect_fail_json(module_default_args)
        assert result == expected_json
