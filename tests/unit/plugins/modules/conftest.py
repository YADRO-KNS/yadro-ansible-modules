from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible.module_utils import basic
from ansible_collections.yadro.obmc.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson


@pytest.fixture(autouse=True)
def module_mock(mocker):

    def exit_json(*args, **kwargs):
        if 'changed' not in kwargs:
            kwargs['changed'] = False
        raise AnsibleExitJson(kwargs)

    def fail_json(*args, **kwargs):
        kwargs['failed'] = True
        raise AnsibleFailJson(kwargs)

    return mocker.patch.multiple(basic.AnsibleModule, exit_json=exit_json, fail_json=fail_json)
