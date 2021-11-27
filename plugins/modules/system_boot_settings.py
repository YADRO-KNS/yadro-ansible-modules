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
module: system_boot_settings
short_description: Setup Host OS boot settings.
version_added: "1.0.0"
description:
  - This module supports check mode.
author: "Radmir Safin (@radmirsafin)"
extends_documentation_fragment:
  - yadro.obmc.connection_options
options:
  override_enabled:
    required: True
    type: str
    choices: [Disabled, Once, Continuous]
    description: 
     - The state of the boot source override feature. 
     - This property shall contain C(Once) for a one-time boot override, and C(Continuous) for a 
     - remain-active-until-cancelled override. If set to C(Once), the value is reset to C(Disabled) after the 
     - I(override_target) actions have completed successfully. Changes to this property do not alter the BIOS 
     - persistent boot order configuration.
  override_mode:
    type: str
    choices: [Legacy, UEFI]
    description:
      - The BIOS boot mode to use when the system boots from the I(override_target) boot source.
      - Option required if override enabled.
  override_target:
    type: str
    choices: [Pxe, Hdd, Cd, Diags, BiosSetup, Usb]
    description:
      - This property shall contain the source to boot the system from, overriding the normal boot order.
      - C(Pxe) indicates to PXE boot from the primary NIC
      - C(Cd), C(Usb), and C(Hdd) indicate to boot from their devices respectively.
      - C(BiosSetup) indicates to boot into the native BIOS screen setup.
      - C(Diags) indicate to boot from the local utilities or diags partitions.
      - Changes to this property do not alter the BIOS persistent boot order configuration.
      - Option required if override enabled.
"""

RETURN = r"""
---
msg:
  type: str
  returned: always
  description: Operation status message.
error:
  type: str
  returned: on error
  description: Error details if raised.
"""

EXAMPLES = r"""
---
- name: Setup once boot fron USB
  yadro.obmc.system_boot_settings:
    connection:
      hostname: "localhost"
      username: "username"
      password: "password"
    override_enabled: Once
    override_mode: Legacy
    override_target: Usb

- name: Setup persistent boot from HDD
  yadro.obmc.system_boot_settings:
    connection:
      hostname: "localhost"
      username: "username"
      password: "password"
    override_enabled: Continuous
    override_mode: UEFI
    override_target: Hdd

- name: Disable boot overrides and reset to defaults
  yadro.obmc.system_boot_settings:
    connection:
      hostname: "localhost"
      username: "username"
      password: "password"
    override_enabled: Disabled
"""


from functools import partial
from ansible_collections.yadro.obmc.plugins.module_utils.obmc_module import OpenBmcModule


class OpenBmcBootSettingsModule(OpenBmcModule):

    def __init__(self):
        argument_spec = {
            "override_enabled": {
                "type": "str",
                "required": True,
                "choices": ["Disabled", "Once", "Continuous"]
            },
            "override_mode": {
                "type": "str",
                "choices": ["Legacy", "UEFI"]
            },
            "override_target": {
                "type": "str",
                "choices": ["Pxe", "Hdd", "Cd", "Diags", "BiosSetup", "Usb"]
            },
        }

        required_if = [
            ["override_enabled", "Once", ["override_mode", "override_target"]],
            ["override_enabled", "Continuous", ["override_mode", "override_target"]],
        ]

        super(OpenBmcBootSettingsModule, self).__init__(
            argument_spec=argument_spec,
            required_if=required_if,
            supports_check_mode=True,
        )

    def _run(self):
        if self.params["override_enabled"] == "Disabled":
            if self.params["override_mode"] or self.params["override_target"]:
                self.fail_json(
                    msg="Cannot setup boot settings.",
                    error="override_enabled is set to 'Disabled'. Other parameters must not present.",
                    changed=False,
                )

        system = self.redfish.get_system("system")
        boot_settings = system.get_boot_source_override()

        payload = {}
        if self.params["override_enabled"] != boot_settings["BootSourceOverrideEnabled"]:
            payload["BootSourceOverrideEnabled"] = self.params["override_enabled"]

        if self.params["override_mode"] and self.params["override_mode"] != boot_settings["BootSourceOverrideMode"]:
            payload["BootSourceOverrideMode"] = self.params["override_mode"]

        if self.params["override_target"] and self.params["override_target"] != boot_settings["BootSourceOverrideTarget"]:
            payload["BootSourceOverrideTarget"] = self.params["override_target"]

        if payload:
            if not self.check_mode:
                system.set_boot_source_override(payload)
            self.exit_json(msg="Operation successful.", changed=True)
        else:
            self.exit_json(msg="No changes required.", changed=False)


def main():
    OpenBmcBootSettingsModule().run()


if __name__ == "__main__":
    main()
