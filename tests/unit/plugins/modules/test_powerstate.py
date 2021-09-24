from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest
import json

from plugins.modules import powerstate
from tests.unit.plugins.modules.utils import ModuleTestCase


class TestMain(ModuleTestCase):

    module = powerstate

    def test_simple(self):
        self.run_module_expect_exit_json({'hostname': '192.168.0.1', 'username': 'username', 'password': 'password', 'state': 'on'})

