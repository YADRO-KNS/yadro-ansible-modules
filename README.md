# YADRO OpenBmc Ansible Collection

[![pipeline status](***REMOVED***)](***REMOVED***)
[![coverage report](***REMOVED***)](***REMOVED***)

## Documentation

### Requirements and terms of reference
***REMOVED***

### Description of modules and parameters
***REMOVED***

## Modules tree

```yml
yadro:
  obmc:
    bmc:
      - yadro.obmc.bmc_session_create
      - yadro.obmc.bmc_account
      - yadro.obmc.bmc_time
      - yadro.obmc.bmc_reset
      - yadro.obmc.bmc_reset_to_defaults
      network:
        interface:
          - yadro.obmc.bmc_network_interface
      firmware:
        - yadro.obmc.bmc_firmware
        - yadro.obmc.bmc_firmware_info
    bios:
      - yadro.obmc.bios_reset_to_defaults
      firmware:
        - yadro.obmc.bios_firmware
        - yadro.obmc.bios_firmware_info
      configuration:
        - yadro.obmc.bios_configuration
    system:
      - yadro.obmc.system_info
      power:
        - yadro.obmc.system_power_state
      boot:
        - yadro.obmc.system_boot_info
```
