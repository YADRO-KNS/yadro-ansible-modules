# YADRO OpenBmc Ansible Collection

[![pipeline status](https://gitlab.spb.yadro.com/galaxy/obmc/badges/master/pipeline.svg)](https://gitlab.spb.yadro.com/galaxy/obmc/-/commits/master)
[![coverage report](https://gitlab.spb.yadro.com/galaxy/obmc/badges/master/coverage.svg)](https://gitlab.spb.yadro.com/galaxy/obmc/-/commits/master)

## Documentation

https://galaxy.pages.spb.yadro.com/obmc/

## Modules tree

```yml
yadro:
  obmc:
    bmc:
      - yadro.obmc.bmc_account
      - yadro.obmc.bmc_ntp
      - yadro.obmc.bmc_reset
      - yadro.obmc.bmc_reset_to_defaults
      network:
        interface:
          - yadro.obmc.bmc_network_interface
      firmware:
        - yadro.obmc.bmc_firmware_info
        - yadro.obmc.bmc_firmware
    bios:
      - yadro.obmc.bios_reset_to_defaults
      firmware:
        - yadro.obmc.bios_firmware_info
        - yadro.obmc.bios_firmware
    system:
      - yadro.obmc.system_info
      power:
        - yadro.obmc.system_power_state
      thermal:
        - yadro.obmc.system_thermal_info
      boot:
        - yadro.obmc.system_boot_info
```
