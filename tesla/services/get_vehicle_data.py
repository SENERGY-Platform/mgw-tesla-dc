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
import traceback
import typing
import teslapy

from util import TeslaVehicle, DeviceManager, get_logger
from mgw_dc.dm import device_state

logger = get_logger(__name__.split(".", 1)[-1])


def handle_get_vehicle_data(manager: DeviceManager, device: TeslaVehicle, *args, **kwargs) -> typing.Dict:
    vehicle = device.get_vehicle()
    try:
        vehicle.sync_wake_up(timeout=25)
    except teslapy.VehicleError as e:
        logger.error(traceback.format_exc())
        device.state = device_state.online if vehicle.available() else device_state.offline
        manager.handle_existing_device(device)
        raise e
    device.state = device_state.online if vehicle.available() else device_state.offline
    manager.handle_existing_device(device)
    data = vehicle.get_vehicle_data()
    return data

