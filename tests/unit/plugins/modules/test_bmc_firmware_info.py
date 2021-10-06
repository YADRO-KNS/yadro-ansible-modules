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

MODULE_PATH = "ansible_collections.yadro.obmc.plugins.modules."


class TestBmcFirmwareInfo(ModuleTestCase):

    module = bmc_firmware_info

    def test_success_case(self, mocker, module_default_args):
        firmware_info = {"Version": "v1.2.3"}
        expected_json = {
            "msg": "Firmware information successfully read.",
            "changed": False,
            "firmware_info": firmware_info
        }
        mocker.patch(MODULE_PATH + "bmc_firmware_info.OpenBmcRestClient.get_bmc_firmware_info", return_value=firmware_info)
        result = self.run_module_expect_exit_json(module_default_args)
        assert result == expected_json
