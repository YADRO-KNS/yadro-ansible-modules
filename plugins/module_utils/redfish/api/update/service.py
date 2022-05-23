# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.0.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

try:
    from typing import Optional, ClassVar, List
except ImportError:
    # Satisfy Python 2 which doesn't have typing.
    Optional = ClassVar = List = None

from ansible_collections.yadro.obmc.plugins.module_utils.redfish.api.base import RedfishAPIObject
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.client.exceptions import RESTClientNotFoundError
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.api.update.software_inventory import SoftwareInventory


class UpdateService(RedfishAPIObject):

    @classmethod
    def select_version(cls, version):  # type: (str) -> Optional[ClassVar[UpdateService]]
        if version == "#UpdateService.v1_4_0.UpdateService":
            return UpdateService_v1_4_0

    def get_firmware_inventory_collection(self):  # type: () -> List[SoftwareInventory]
        raise NotImplementedError("Method not implemented")

    def get_firmware_inventory(self, inventory_id):  # type: (str) -> Optional[SoftwareInventory]
        raise NotImplementedError("Method not implemented")

    def upload_image(self, image):  # type: (bytes) -> None
        raise NotImplementedError("Method not implemented")

    def simple_update(self, image_uri):  # type: (str) -> None
        raise NotImplementedError("Method not implemented")


class UpdateService_v1_4_0(UpdateService):

    def __init__(self, *args, **kwargs):
        super(UpdateService_v1_4_0, self).__init__(*args, **kwargs)

    def get_firmware_inventory_collection(self):  # type: () -> List[SoftwareInventory]
        inventories = []
        inventories_collection = self._client.get("{0}/FirmwareInventory".format(self._path)).json
        for member in inventories_collection["Members"]:
            inventory_data = self._client.get(member["@odata.id"]).json
            inventories.append(SoftwareInventory.from_json(self._client, inventory_data))
        return inventories

    def get_firmware_inventory(self, inventory_id):  # type: (str) -> Optional[SoftwareInventory]
        if not isinstance(inventory_id, str):
            raise TypeError("Inventory id must be string. Received: {0}".format(type(inventory_id)))

        inventory_path = "{0}/FirmwareInventory/{1}".format(self._path, inventory_id)
        try:
            inventory_data = self._client.get(inventory_path).json
        except RESTClientNotFoundError:
            return None
        return SoftwareInventory.from_json(self._client, inventory_data)

    def simple_update(self, image_uri):  # type: (str) -> None
        self._client.post(
            self._path + '/Actions/UpdateService.SimpleUpdate',
            body={'ImageURI': image_uri},
        )

    def upload_image(self, image):  # type: (bytes) -> None
        self._client.post(self._path, body=image)
