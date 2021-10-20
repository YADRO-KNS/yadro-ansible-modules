# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.0.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import pytest

from ansible_collections.yadro.obmc.tests.unit.compat.mock import MagicMock
from ansible_collections.yadro.obmc.plugins.modules import bmc_firmware_info
from ansible_collections.yadro.obmc.tests.unit.plugins.modules.utils import ModuleTestCase


class TestBmcFirmwareInfo(ModuleTestCase):

    module = bmc_firmware_info

    def test_firmware_info_reading(self, mocker, module_args):
        firmware_id = "Image Id"
        firmware_info = {"Id": firmware_id, "Description": "Description"}
        client_mock = MagicMock()
        client_mock.get_manager.return_value = {"Links": {"ActiveSoftwareImage": firmware_id}}
        client_mock.get_software_inventory.return_value = firmware_info
        mocker.patch("{0}.create_client".format(self.module.__name__), return_value=client_mock)

        expected_json = {
            "msg": "Firmware information successfully read.",
            "changed": False,
            "firmware_info": firmware_info,
        }
        result = self.run_module_expect_exit_json(module_args)

        client_mock.get_manager.assert_called_with()
        client_mock.get_software_inventory.assert_called_with(firmware_id)
        assert result == expected_json
