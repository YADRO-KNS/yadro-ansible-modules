# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.0.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible_collections.yadro.obmc.plugins.module_utils.client import RestClient


@pytest.fixture
def rest_client_args():
    default_args = {
        "hostname": "localhost",
        "username": "username",
        "password": "password",
        "base_prefix": "/redfish/v1/",
        "validate_certs": True,
        "port": 443,
        "timeout": 30,
    }
    return default_args


@pytest.fixture
def rest_client(rest_client_args):
    return RestClient(**rest_client_args)
