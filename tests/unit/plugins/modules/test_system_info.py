# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.0.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible_collections.yadro.obmc.plugins.modules import system_info
from ansible_collections.yadro.obmc.tests.unit.plugins.modules.utils import ModuleTestCase

MODULE_PATH = "ansible_collections.yadro.obmc.plugins.modules."


class TestSystemInfo(ModuleTestCase):

    module = system_info

    def test_correct_system_info(self, mocker, module_default_args):
        system_info = {
            "firmware": {
                "bios_version": "bios version",
                "bmc_version": "bmc version",
            }
        }
        expected_json = {
            "msg": "System information successfully read.",
            "changed": False,
            "system_info": system_info
        }
        mocker.patch(MODULE_PATH + "system_info.OpenBmcClient.get_bmc_system_info", return_value=system_info)
        result = self.run_module_expect_exit_json(module_default_args)
        assert result == expected_json
