from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import pytest

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes


def set_module_args(args):
    if '_ansible_remote_tmp' not in args:
        args['_ansible_remote_tmp'] = '/tmp'
    if '_ansible_keep_remote_files' not in args:
        args['_ansible_keep_remote_files'] = False

    args = json.dumps({'ANSIBLE_MODULE_ARGS': args})
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
