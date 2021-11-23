#!/usr/bin/python
# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.0.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


DOCUMENTATION = r"""
---
module: system_info
short_description: Return system information.
version_added: "1.0.0"
description:
  - This module supports check mode.
author: "Radmir Safin (@radmirsafin)"
extends_documentation_fragment:
  - yadro.obmc.connection_options
"""

RETURN = r"""
---
msg:
  type: str
  returned: always
  description: Operation status message.
error_info:
  type: str
  returned: on error
  description: Error details if raised.
system_info:
  type: dict
  returned: on success
  description: System information.
"""

EXAMPLES = r"""
---
- name: Get firmware information
  yadro.obmc.system_info:
    connection:
      hostname: "localhost"
      username: "username"
      password: "password"
  register: system_info
"""


from ansible_collections.yadro.obmc.plugins.module_utils.obmc_module import OpenBmcModule


class OpenBmcSystemInfoModule(OpenBmcModule):

    def __init__(self):
        super(OpenBmcSystemInfoModule, self).__init__(supports_check_mode=True)

    def _run(self):
        system_info = self.client.get_system()

        system_info["Memory"] = {}
        for memory_id in self.client.get_memory_collection():
            system_info["Memory"][memory_id] = self.client.get_memory(memory_id)

        system_info["Processors"] = {}
        for processor_id in self.client.get_processors_collection():
            system_info["Processors"][processor_id] = self.client.get_processor(processor_id)

        self.exit_json(msg="System information successfully read.", system_info=system_info)


def main():
    OpenBmcSystemInfoModule().run()


if __name__ == "__main__":
    main()
