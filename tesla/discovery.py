"""
   Copyright 2022 InfAI (CC SES)

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
import threading
import time
from typing import Dict

import teslapy
from mgw_dc.dm import device_state

from util import get_logger, conf, diff, TeslaVehicle

__all__ = ("Discovery",)

from util.device_manager import DeviceManager

logger = get_logger(__name__.split(".", 1)[-1])


class Discovery(threading.Thread):
    def __init__(self, device_manager: DeviceManager):
        super().__init__(name="discovery", daemon=True)
        self._device_manager = device_manager
        self.tesla = teslapy.Tesla(conf.Tesla.email, cache_file="./.cache/cache.json")

    def get_tesla_devices(self) -> Dict[str, TeslaVehicle]:
        logger.info("Starting scan")
        devices: Dict[str, TeslaVehicle] = {}

        if not self.tesla.authorized:
            self.tesla.refresh_token(refresh_token=conf.Tesla.refreshtoken)
        vehicles = self.tesla.vehicle_list()

        for v in vehicles:
            logger.info("Discovered '" + v["display_name"] + "' with ID " + str(v["id"]))
            id = conf.Discovery.device_id_prefix + str(v["id"])
            decoded_vin = v.decode_vin()

            attributes = [
                {"key": "manufacturer", "value": decoded_vin["manufacturer"]},
                {"key": "tesla/vehicle_id", "value": str(v["vehicle_id"])},
                {"key": "motor-vehicle/vin", "value": v["vin"]},
                {"key": "motor-vehicle/make", "value": decoded_vin["make"]},
                {"key": "tesla/body_type", "value": decoded_vin["body_type"]},
                {"key": "tesla/belt_system", "value": decoded_vin["belt_system"]},
                {"key": "tesla/battery_type", "value": decoded_vin["battery_type"]},
                {"key": "tesla/drive_unit", "value": decoded_vin["drive_unit"]},
                {"key": "production_year", "value": decoded_vin["year"]},
                {"key": "tesla/plant_code", "value": decoded_vin["plant_code"]},
                {"key": "tesla/option_codes", "value": v["option_codes"]},
                {"key": "tesla/color", "value": str(v["color"])},
                {"key": "tesla/in_service", "value": str(v["in_service"])},
                {"key": "tesla/calendar_enabled", "value": str(v["calendar_enabled"])},
                {"key": "tesla/api_version", "value": str(v["api_version"])},
            ]
            devices[id] = TeslaVehicle(id=id, name=v["display_name"], type=conf.Senergy.dt_tesla_vehicle,
                                       state=device_state.online if v.available() else device_state.offline,
                                       vehicle=v, attributes=attributes)

        logger.info("Discovered " + str(len(devices)) + " vehicles")
        return devices

    def _refresh_devices(self):
        try:
            teslas = self.get_tesla_devices()
            stored_devices = self._device_manager.get_devices()

            new_devices, missing_devices, existing_devices = diff(stored_devices, teslas)
            if new_devices:
                for device_id in new_devices:
                    self._device_manager.handle_new_device(teslas[device_id])
            if missing_devices:
                for device_id in missing_devices:
                    self._device_manager.handle_missing_device(stored_devices[device_id])
            if existing_devices:
                for device_id in existing_devices:
                    self._device_manager.handle_existing_device(stored_devices[device_id])
            self._device_manager.set_devices(devices=teslas)
        except Exception as ex:
            logger.error("refreshing devices failed - {}".format(ex))

    def run(self) -> None:
        logger.info("starting {} ...".format(self.name))
        self._refresh_devices()
        last_discovery = time.time()
        while True:
            if time.time() - last_discovery > conf.Discovery.scan_delay:
                last_discovery = time.time()
                self._refresh_devices()
            time.sleep(conf.Discovery.scan_delay / 100)  # at most 1 % too late
