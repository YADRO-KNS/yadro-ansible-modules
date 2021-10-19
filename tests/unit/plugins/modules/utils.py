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
from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes
from ansible.module_utils.urls import ConnectionError, SSLValidationError
from ansible.module_utils.six.moves.urllib.error import URLError, HTTPError
from ansible.module_utils.common.text.converters import to_text


def set_module_args(args):
    if "_ansible_remote_tmp" not in args:
        args["_ansible_remote_tmp"] = "/tmp"
    if "_ansible_keep_remote_files" not in args:
        args["_ansible_keep_remote_files"] = False

    args = json.dumps({"ANSIBLE_MODULE_ARGS": args})
    basic._ANSIBLE_ARGS = to_bytes(args)


class AnsibleExitJson(Exception):
    pass


class AnsibleFailJson(Exception):
    pass


class ModuleTestCase:

    module = None

    def run_module_expect_exit_json(self, module_args):
        set_module_args(module_args)
        with pytest.raises(AnsibleExitJson) as e:
            self.module.main()
        return e.value.args[0]

    def run_module_expect_fail_json(self, module_args):
        set_module_args(module_args)
        with pytest.raises(AnsibleFailJson) as e:
            self.module.main()
        return e.value.args[0]

    def test_http_error_passthrough(self, mocker, module_args):
        error_message = {"Error": "Message"}
        http_error = to_text(json.dumps(error_message))
        exception = HTTPError("localhost", 400, "Bad Request Error", {}, StringIO(http_error))
        mocker.patch("{0}.create_client".format(self.module.__name__), side_effect=exception)
        expected_json = {
            "msg": "Request finished with error.",
            "error_info": error_message,
            "failed": True,
        }
        result = self.run_module_expect_fail_json(module_args)
        assert result == expected_json

    @pytest.mark.parametrize("exception", [ConnectionError, SSLValidationError, URLError])
    def test_connection_errors_passthrough(self, mocker, module_args, exception):
        expected_exception = exception("Exception")
        mocker.patch("{0}.create_client".format(self.module.__name__), side_effect=expected_exception)
        expected_json = {
            "msg": "Can't connect to server.",
            "error_info": str(expected_exception),
            "failed": True,
        }
        result = self.run_module_expect_fail_json(module_args)
        assert result == expected_json
