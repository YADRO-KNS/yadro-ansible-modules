# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.0.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible.module_utils import basic
from ansible_collections.yadro.obmc.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson


@pytest.fixture(autouse=True)
def mock_module(mocker):

    def exit_json(*args, **kwargs):
        if "changed" not in kwargs:
            kwargs["changed"] = False
        raise AnsibleExitJson(kwargs)

    def fail_json(*args, **kwargs):
        kwargs["failed"] = True
        raise AnsibleFailJson(kwargs)

    return mocker.patch.multiple(basic.AnsibleModule, exit_json=exit_json, fail_json=fail_json)


@pytest.fixture
def module_default_args():
    default_args = {"hostname": "localhost", "username": "username", "password": "password"}
    return default_args
