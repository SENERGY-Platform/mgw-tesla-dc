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

import random
import sys
import time
import typing

from .config import *
from .logger import *
from .mqtt import *
from .router import *
from .device import *
from .device_manager import *
from .events import *

from mgw_dc.dm import Device

__all__ = (
    config.__all__,
    logger.__all__,
    mqtt.__all__,
    router.__all__,
    device.__all__,
    device_manager.__all__,
    events.__all__
)


def handle_sigterm(signo, stack_frame):
    print("\ngot signal '{}' - exiting ...\n".format(signo))
    sys.exit(0)


def delay_start(min: int, max: int):
    delay = random.randint(min, max)
    print("delaying start for {}s".format(delay))
    time.sleep(delay)


def diff(known: dict, unknown: dict):
    known_set = set(known)
    unknown_set = set(unknown)
    missing = known_set - unknown_set
    new = unknown_set - known_set
    intersection = known_set & unknown_set
    return new, missing, intersection


def to_dict(items: typing.List[Device]):
    _dict = dict()
    for item in items:
        _dict[item.id] = item
    return _dict
