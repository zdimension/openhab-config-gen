import inspect
from dataclasses import dataclass, replace, field
from typing import Optional, ClassVar

from influxdb.types import Alert
from openhab.config import OHPollerType
from openhab.types import OHIcon, ValType, fix_unit_openhab, OHQuantity


@dataclass
class ModbusProp:
    address: int
    valtype: ValType
    icon: OHIcon
    id: str
    display_name: str
    quantity: OHQuantity
    """The unit of measurement for this property"""
    format: str
    """Format string for openHAB state view"""
    unit: str
    """Unit of measure (will be put after format string)"""

    def get_format_string(self) -> str:
        """
        Returns the format string for the given property.

        Example:
            - a property with unit `°C` and format `%.1f` will return `%.1f °C`
            - a property with no unit and format `%.2f` will return `%.2f`
        """
        return f"{self.format}" + (f" {self.unit}" if self.unit else "")

    def get_gain_string(self) -> str:
        """
        Returns the `gain` value for the given property. `UNIT_MAP` is used for units not directly supported by openHAB.

        Example:
            - a property with unit `°C` and scale `10` will return `0.1 °C`
            - a property with unit `rpm` and scale `1` will return `1 Hz`
        """
        return f"{1 / self.valtype.scale}" + (f" {fix_unit_openhab(self.unit)}" if self.unit else "")


@dataclass
class PropGroup:
    id: str
    """Identifier"""
    name: str
    """Display name"""
    props: list[ModbusProp]
    """List of properties in this group"""
    type_: OHPollerType = "holding"
    """Modbus function code"""
    offset: int = 1
    """Modbus address offset"""

    def __post_init__(self):
        self.props = [ModbusProp(*x) if type(x) == tuple else x
                      for x in self.props]


def seq(count, *templates):
    """
    Repeats one or more items a given number of times, formatting the ID and display name with the index.
    """
    props = [ModbusProp(*x) for x in templates]
    size = sum(p.valtype.size for p in props)
    for i in range(count):
        for prop in props:
            yield replace(prop,
                          address=prop.address + i * size,
                          id=prop.id % (i + 1),
                          display_name=prop.display_name % (i + 1),
                          )


def prefix(id="", name=""):
    if id:
        id = f"{id}_"
    if name:
        name = f"{name}"

    def items(*templates):
        props = [ModbusProp(*x) if type(x) == tuple else x for x in templates]
        for prop in props:
            yield replace(prop,
                          id=f"{id}{prop.id}",
                          display_name=f"{name}{prop.display_name}",
                          )

    return items


@dataclass
class SlaveGroup:
    """
    Modbus slave group
    """

    name: str
    slaves: list["SlaveBase"]
    # TODO: unsupported before 3.10 :(
    # so we have to make a custom __init__ for SlaveBase, otherwise it complains about fields in
    # SlaveBase not having default values while fields in SlaveGroup do
    # custom_id: Optional[str] = field(default=None, kw_only=True)
    # custom_name: Optional[str] = field(default=None, kw_only=True)
    custom_id: Optional[str] = None
    custom_name: Optional[str] = None


@dataclass(init=False)
class SlaveBase(SlaveGroup):
    """
    Base Modbus slave
    """

    group: str
    deadman: ClassVar[str] = None
    prefix: str = None
    alerts: ClassVar[list[Alert]] = []
    slaves: list["SlaveBase"] = field(init=False)
    offset: int = 0
    icon: ClassVar[OHIcon] = ""

    def __init__(self, name, group, custom_id=None, custom_name=None, offset=0):
        super().__init__(name, [self], custom_id, custom_name)
        self.group = group
        self.prefix = None  # noqa (the prefix is computed during configuration generation)
        self.offset = offset

    def get_class_hierarchy(self) -> tuple[type, ...]:
        """
        Returns the list of classes in the hierarchy of this device, starting with the base class right after SlaveBase.
        """
        return inspect.getmro(self.__class__)[-4::-1]

    def get_prop_groups(self) -> list[PropGroup]:
        """
        Returns a list of all property groups in this device, including those in parent classes.
        """
        return [cl.props for cl in inspect.getmro(self.__class__)[-4::-1]]

    def get_alerts(self) -> list[Alert]:
        return [alert for cl in inspect.getmro(self.__class__)[-4::-1] for alert
                in
                cl.alerts]


@dataclass
class ModbusMaster:
    """
    Modbus master
    """

    ip: str
    """IP address of the device"""
    prefix: str
    """Prefix for children items; prefix G and slave 4 will lead to a "PV_G4" prefix for all items"""
    slaves: dict[int, SlaveGroup]
    """List of slave devices to read"""
    slave_offset: int = 100
    """Offset to add to slave addresses"""
    custom_id: Optional[str] = None
    ignore: bool = False
    """Ignore this master for the openHAB configuration files"""


class AllowDuplicates:
    def __init__(self, iterable):
        self._iterable = iterable

    def items(self):
        return self._iterable
