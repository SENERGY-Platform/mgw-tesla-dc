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

__all__ = ("conf",)

import simple_env_var


@simple_env_var.configuration
class Conf:
    @simple_env_var.section
    class MsgBroker:
        host = "localhost"
        port = 1883

    @simple_env_var.section
    class Logger:
        level = "debug"
        enable_mqtt = False

    @simple_env_var.section
    class Client:
        clean_session = False
        keep_alive = 30
        id = "tesla-dc"

    @simple_env_var.section
    class Discovery:
        scan_delay = 60 * 60 * 24
        device_id_prefix = "tesla-"

    @simple_env_var.section
    class StartDelay:
        enabled = False
        min = 5
        max = 20

    @simple_env_var.section
    class Senergy:
        dt_tesla_vehicle = "urn:infai:ses:device-type:71a52d54-aab8-43e8-9b64-3889b08e0eb9"
        events_get_vehicle_data_seconds = 60 * 60
        service_get_vehicle_data = "get_vehicle_data"

    @simple_env_var.section
    class Tesla:
        email = "elon@tesla.com"
        refreshToken = ""

conf = Conf()
