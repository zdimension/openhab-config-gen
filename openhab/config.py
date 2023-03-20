from dataclasses import dataclass, field
from typing import Any, Optional, Literal

from openhab.types import OHIcon, ValType, quantity_to_property, OHQuantity, OHTag


def quote(s: Any) -> str:
    """
    Adds double quotes around a string
    >>> quote("a")
    '"a"'
    """
    return f'"{s}"'


def quote_list(l: list[Any]) -> str:
    """
    Adds double quotes around each element of a list and joins them with commas
    >>> quote_list(["a", "b", "c"])
    '"a", "b", "c"'
    """
    return ", ".join(map(quote, l))


def quote_dict(d: dict[str, Any]) -> str:
    """
    Adds double quotes around value of a dict, join keys and values with '=' and join all of those with commas
    >>> quote_dict({"a": "b", "c": "d"})
    'a="b", c="d"'
    """
    return ", ".join(key + "=" + quote(val) for key, val in d.items())


@dataclass
class OHBridge:
    """
    openHAB Modbus binding Bridge
    """
    id: str
    """Internal ID for the `Bridge` object"""
    name: str
    """Display name"""
    params: dict[str, Any] = field(init=False)

    def __str__(self):
        return f'Bridge poller {self.id} "{self.name}" [ {quote_dict(self.params)} ]'


OHPollerType = Literal["coil", "discrete", "holding", "input"]


@dataclass
class OHPollerBridge(OHBridge):
    """
    openHAB Modbus poller object
    """
    start: int
    length: int
    type_: OHPollerType
    max_tries: int = field(default=1)

    def __post_init__(self):
        self.params = {
            "start": self.start,
            "length": self.length,
            "type": self.type_,
            "maxTries": self.max_tries
        }


@dataclass
class OHThing:
    """
    openHAB Modbus binding Thing
    """
    id: str
    """Internal ID for the `Thing` object"""
    name: str
    """Display name"""
    group: str
    """Group name"""
    address: int
    """Modbus register number"""
    type_: ValType
    """Value type"""
    transforms: list[str]
    """Transforms to be applied"""

    def __str__(self):
        params = {
            "readStart": self.address,
            "readValueType": self.type_.openhab_full()
        }
        if self.transforms:
            params["readTransform"] = "∩".join(self.transforms)
        return f'Thing data {self.id} "{self.name}" @ "{self.group}" [ {quote_dict(params)} ]'


@dataclass
class OHItem:
    """
    openHAB Item
    """
    id: str
    """Internal ID for the `Item` object, used for API access"""
    name: str
    """Display name"""
    icon: OHIcon
    """Icon"""
    group: str
    """Group name"""

    def type(self):
        raise NotImplementedError()

    def get_tags(self) -> list[OHTag]:
        raise NotImplementedError()

    def __str__(self):
        tag_list = "[" + quote_list(self.get_tags()) + "]"

        parts = [
            self.type(),
            f"{self.id}",
            f'"{self.name}"',
            f"<{self.icon}>" if self.icon else None,
            f"(gModbus,{self.group})",
            tag_list
        ]

        return " ".join(filter(None, parts))


@dataclass
class OHNumber(OHItem):
    """
    openHAB "Number" Item
    """
    bridge: OHBridge
    """The openHAB Modbus Bridge this Number belongs to."""
    gain_string: str
    """Gain string, to multiply by a factor and add a unit. Example: "0.1 °C" to multiply the raw value by 0.1 and mark it as °C."""
    location: str
    """Location, with format "A1" where A is a building identifier and 1 is a floor identifier."""
    prefix: str
    quantity: Optional[OHQuantity]
    format_string: str
    """Format string for display. Expects one format parameter, either float (%f) or integer (%d) with eventual specifiers."""

    def __post_init__(self):
        self.name = f"{self.name} [{self.format_string}]"

    def type(self):
        return f"Number:{self.quantity or 'Dimensionless'}"

    def get_tags(self) -> list[OHTag]:
        tags = ["Measurement"]

        if prop := quantity_to_property(self.quantity):
            tags.append(prop)

        return tags

    def binding_conf(self):
        return {
            "channel": (
                f"modbus:data:{self.prefix}:{self.bridge.id}:{self.id}:number",
                {
                    "profile": "modbus:gainOffset",
                    "gain": self.gain_string
                }),
            "influxdb": (self.id, {
                "location": self.location,
                "building": self.location[0],
                "floor": self.location[1]
            })
        }

    def __str__(self):
        binding = "{" + ", ".join(
            f"{key}={quote(val)} [{quote_dict(tags)}]"
            for key, (val, tags)
            in self.binding_conf().items()) + "}"

        return super().__str__() + " " + binding


@dataclass
class OHGroup(OHItem):
    """
    openHAB "Group" Item
    """
    tags: list[OHTag]

    def __init__(self, id: str, name: str, slave: "openhab.modbus.SlaveBase"):
        super().__init__(id, f"{name} ({slave.name})",
                         slave.icon,
                         "g" + slave.group)
        self.tags = slave.tags

    def type(self):
        return "Group"

    def get_tags(self) -> list[OHTag]:
        return self.tags
