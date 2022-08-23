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
import json
import traceback
import typing

import mgw_dc

from tesla.services.get_vehicle_data import handle_get_vehicle_data
from util import conf, get_logger, MQTTClient
from util.device_manager import DeviceManager

logger = get_logger(__name__.split(".", 1)[-1])

__all__ = ("Command",)

command_handlers = {
    conf.Senergy.service_get_vehicle_data: handle_get_vehicle_data,
}


class Command:
    def __init__(self, mqtt_client: MQTTClient, device_manager: DeviceManager):
        self.mqtt_client = mqtt_client
        self.device_manager = device_manager

    def execute_command(self, device_id: str, service: str, payload: typing.AnyStr, is_event: bool = False):
        logger.debug(device_id)
        command_id = None
        if not is_event:
            payload = json.loads(payload)
            command_id = payload["command_id"]
            if len(payload["data"]) == 0:
                payload = {}
            else:
                payload = json.loads(payload["data"])
        else:
            payload = {}
        if device_id not in self.device_manager.get_devices():
            logger.error("device unknown " + device_id)
            return
        device = self.device_manager.get_devices()[device_id]
        vehicle = device.get_vehicle()
        if not vehicle.tesla.authorized:
            vehicle.tesla.refresh_token(refresh_token=conf.Tesla.refreshtoken)
        try:
            if service not in command_handlers:
                vehicle.sync_wake_up()
                result = vehicle.command(service, **payload)
            else:
                result = command_handlers[service](self.device_manager, device, payload)
        except Exception as ex:
            logger.error("Command failed: {}".format(ex))
            logger.error(traceback.format_exc())
            if is_event:
                self.mqtt_client.publish("error/device/" + device_id, str(ex), 1)
            else:
                self.mqtt_client.publish("error/command/" + command_id, str(ex), 1)
            return
        if is_event:
            response = result
            topic = mgw_dc.com.gen_event_topic(device_id, service)
        else:
            response = {"command_id": command_id}
            if result is not None:
                response["data"] = json.dumps(result).replace("'", "\"")
            topic = mgw_dc.com.gen_response_topic(device_id, service)
        self.mqtt_client.publish(topic, json.dumps(response).replace("'", "\""), 2)
