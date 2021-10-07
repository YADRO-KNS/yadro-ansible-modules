# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.0.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible_collections.yadro.obmc.plugins.modules import bmc_firmware_info
from ansible_collections.yadro.obmc.tests.unit.plugins.modules.utils import ModuleTestCase
from ansible.module_utils.urls import ConnectionError, SSLValidationError
from ansible.module_utils.six.moves.urllib.error import URLError, HTTPError

MODULE_PATH = "ansible_collections.yadro.obmc.plugins.modules."


class TestBmcFirmwareInfo(ModuleTestCase):

    module = bmc_firmware_info

    @pytest.fixture
    def default_firmware_info(self):
        firmware_info = {
            "Description": "BMC image",
            "Status": {
                "Health": "OK",
                "HealthRollup": "OK",
                "State": "Enabled"
            },
            "Updateable": True,
            "Version": "v1.0"
        }
        return firmware_info

    @pytest.fixture
    def bmc_firmware_info_mock(self, mocker):
        return mocker.patch(MODULE_PATH + "bmc_firmware_info.OpenBmcRestClient.get_bmc_firmware_info")

    def test_http_error(self, bmc_firmware_info_mock, default_firmware_info, module_default_args):
        bmc_firmware_info_mock.return_value = default_firmware_info
        exception = HTTPError("localhost", 400, "Bad Request Error", {}, None)
        bmc_firmware_info_mock.side_effect = exception
        expected_json = {
            "msg": "Request finished with error.",
            "error_info": str(exception),
            "failed": True,
        }
        result = self.run_module_expect_fail_json(module_default_args)
        assert result == expected_json

    def test_url_error(self, bmc_firmware_info_mock, default_firmware_info, module_default_args):
        bmc_firmware_info_mock.return_value = default_firmware_info
        exception = URLError("URL error")
        bmc_firmware_info_mock.side_effect = exception
        expected_json = {
            "msg": "Can't connect to server.",
            "error_info": str(exception),
            "failed": True,
            "unreachable": True,
        }
        result = self.run_module_expect_fail_json(module_default_args)
        assert result == expected_json

    @pytest.mark.parametrize("exception", [ConnectionError, SSLValidationError])
    def test_connection_errors(self, bmc_firmware_info_mock, default_firmware_info, module_default_args, exception):
        bmc_firmware_info_mock.return_value = default_firmware_info
        exception = exception("URL error")
        bmc_firmware_info_mock.side_effect = exception
        expected_json = {
            "msg": "Can't read firmware information.",
            "error_info": str(exception),
            "failed": True,
        }
        result = self.run_module_expect_fail_json(module_default_args)
        assert result == expected_json

    def test_success_case(self, bmc_firmware_info_mock, default_firmware_info, module_default_args):
        bmc_firmware_info_mock.return_value = default_firmware_info
        expected_json = {
            "msg": "Firmware information successfully read.",
            "changed": False,
            "firmware_info": default_firmware_info,
        }
        result = self.run_module_expect_exit_json(module_default_args)
        assert result == expected_json
