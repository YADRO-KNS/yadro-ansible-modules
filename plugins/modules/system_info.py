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
error:
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
- name: Get system information
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
        manager = self.redfish.get_manager("bmc")
        manager_graphical_console = manager.get_graphical_console()
        manager_serial_console = manager.get_serial_console()

        chassis_collection = self.redfish.get_chassis_collection()
        chassis_server = None
        for chassis in chassis_collection:
            if chassis.get_chassis_type() == "RackMount":
                chassis_server = chassis
                break
        if chassis_server is None:
            self.fail_json(
                msg="Cannot read system information.",
                error="Cannot found chassis with RackMount type.",
                changed=False
            )

        system = self.redfish.get_system("system")
        processor_collection = system.get_processor_collection()
        memory_collection = system.get_memory_collection()
        pcie_devices = system.get_pcie_device_collection()

        system_info = {
            "BMC": {
                "Id": manager.get_id(),
                "Name": manager.get_name(),
                "FirmwareVersion": manager.get_firmware_version(),
                "ServiceEntryPointUUID": manager.get_service_entry_point_uuid(),
                "UUID": manager.get_uuid(),
                "PowerState": manager.get_power_state(),
                "Status": manager.get_status(),
                "GraphicalConsole": {
                    "ConnectTypesSupported": manager_graphical_console["ConnectTypesSupported"],
                    "MaxConcurrentSessions": manager_graphical_console["MaxConcurrentSessions"],
                    "ServiceEnabled": manager_graphical_console["ServiceEnabled"],
                } if manager_graphical_console else None,
                "SerialConsole": {
                    "ConnectTypesSupported": manager_serial_console["ConnectTypesSupported"],
                    "MaxConcurrentSessions": manager_serial_console["MaxConcurrentSessions"],
                    "ServiceEnabled": manager_serial_console["ServiceEnabled"],
                } if manager_serial_console else None,
            },
            "Chassis": [
                {
                    "Id": chassis.get_id(),
                    "Name": chassis.get_name(),
                    "Model": chassis.get_model(),
                    "Manufacturer": chassis.get_manufacturer(),
                    "ChassisType": chassis.get_chassis_type(),
                    "PowerState": chassis.get_power_state(),
                    "Status": chassis.get_status(),
                    "SerialNumber": chassis.get_serial_number(),
                    "PartNumber": chassis.get_part_number(),
                } for chassis in chassis_collection
            ],
            "Processors": [
                {
                    "Id": processor.get_id(),
                    "Name": processor.get_name(),
                    "Model": processor.get_model(),
                    "Socket": processor.get_socket(),
                    "InstructionSet": processor.get_instruction_set(),
                    "Manufacturer": processor.get_manufacturer(),
                    "Architecture": processor.get_architecture(),
                    "Type": processor.get_type(),
                    "TotalCores": processor.get_total_cores(),
                    "Status": processor.get_status(),
                } for processor in processor_collection
            ],
            "DIMM": [
                {
                    "Id": memory.get_id(),
                    "Name": memory.get_name(),
                    "PartNumber": memory.get_part_number(),
                    "SerialNumber": memory.get_serial_number(),
                    "DeviceType": memory.get_device_type(),
                    "Status": memory.get_status(),
                    "Manufacturer": memory.get_manufacturer(),
                    "DeviceLocator": memory.get_device_locator(),
                    "CapacityMiB": memory.get_capacity_mib(),
                    "OperatingSpeedMhz": memory.get_operating_speed_mhz(),
                    "DataWidthBits": memory.get_data_with_bits(),
                    "SpareDeviceCount": memory.get_spare_device_count(),
                } for memory in memory_collection
            ],
            "PCIeDevices": [
                {
                    "Id": device.get_id(),
                    "Address": device.get_address(),
                    "Model": device.get_model(),
                    "Manufacturer": device.get_manufacturer(),
                    "Functions": [
                        {
                            "Id": func.get_id(),
                            "Name": func.get_name(),
                            "DeviceClass": func.get_device_class(),
                            "ClassCode": func.get_class_code(),
                            "RevisionId": func.get_revision_id(),
                            "VendorId": func.get_vendor_id(),
                            "DeviceId": func.get_device_id(),
                            "SubsystemVendorId": func.get_subsystem_vendor_id(),
                            "SubsystemId": func.get_subsystem_id(),
                        } for func in device.get_function_collection()
                    ]
                } for device in pcie_devices
            ],
            "Fans": [
                {
                    "Id": fan.get_id(),
                    "Name": fan.get_name(),
                    "PartNumber": fan.get_part_number(),
                    "Model": fan.get_model(),
                    "Connector": fan.get_connector(),
                    "Manufacturer": fan.get_manufacturer(),
                    "Status": fan.get_status(),
                } for fan in chassis_server.get_thermal().get_fan_collection()
            ],
            "PowerSupplies": [
                {
                    "Id": supply.get_id(),
                    "Name": supply.get_name(),
                    "SerialNumber": supply.get_serial_number(),
                    "Model": supply.get_model(),
                    "Manufacturer": supply.get_manufacturer(),
                    "Status": supply.get_status(),
                    "ProductVersion": supply.get_product_version(),
                    "FirmwareVersion": supply.get_firmware_version(),
                } for supply in chassis_server.get_power().get_power_supply_collection()
            ],
        }
        self.exit_json(msg="Operation successful.", system_info=system_info)


def main():
    OpenBmcSystemInfoModule().run()


if __name__ == "__main__":
    main()
