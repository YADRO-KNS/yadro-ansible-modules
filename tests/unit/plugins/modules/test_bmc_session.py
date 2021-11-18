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
from ansible_collections.yadro.obmc.tests.unit.plugins.modules.utils import ModuleTestCase
from ansible_collections.yadro.obmc.plugins.modules import bmc_session


class TestBmcSession(ModuleTestCase):

    module = bmc_session

    @pytest.fixture
    def module_args(self, module_default_args):
        return module_default_args