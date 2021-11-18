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
from ansible_collections.yadro.obmc.plugins.modules import bmc_network_interface
from ansible_collections.yadro.obmc.tests.unit.plugins.modules.utils import ModuleTestCase


class TestBmcNetworkInterface(ModuleTestCase):

    module = bmc_network_interface

    @pytest.fixture
    def module_args(self, module_default_args):
        module_args = module_default_args
        module_args.update({"name": "eth0"})
        return module_args

    def test_dhcp_enabled(self, mocker, module_args):
        module_args["dhcp_enabled"] = True

        client_mock = MagicMock()
        client_mock.get_ethernet_interface_collection.return_value = ["eth0"]
        client_mock.get_ethernet_interface.return_value = {"DHCPv4": {"DHCPEnabled": False}}
        mocker.patch("{0}.OpenBmcModule._create_client".format(self.module.__name__), return_value=client_mock)

        expected_json = {"msg": "Interface configuration updated.", "changed": True}
        result = self.run_module_expect_exit_json(module_args)

        client_mock.get_ethernet_interface_collection.assert_called_with()
        client_mock.get_ethernet_interface.assert_called_with("eth0")
        client_mock.update_ethernet_interface.assert_called_with("eth0", {"DHCPv4": {"DHCPEnabled": True}})
        assert result == expected_json
