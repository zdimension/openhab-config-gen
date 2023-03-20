import re
from collections.abc import Iterator
from typing import TextIO, Union, AnyStr

from openhab.config import *
from openhab.modbus import *
from openhab.types import *
from pathlib import Path
import os

CONF_PATH = Path(os.path.dirname(__file__)) / "conf"


def gen_conf(file: str, masters: list[ModbusMaster], unused: bool):
    """
    Generates openHAB configuration files for a given list of Modbus masters

    :param file: The name of the file to generate
    :param masters: The list of Modbus masters to generate configuration for
    :param unused: Whether to append `.unused` to the generated files, so they're not read by openHAB
    """
    suffix = ""
    if unused:
        suffix = ".unused"

    things = open(CONF_PATH / "things" / f"{file}.things{suffix}", "w", encoding="utf-8", newline="\n")

    items = open(CONF_PATH / "items" / f"{file}.items{suffix}", "w", encoding="utf-8", newline="\n")
    items.write("Group gModbus (gInfluxDB)\n")
    items.write("\n")

    for logger in masters:
        prefix_l = logger.custom_id or f"{file.upper()}_{logger.prefix}"  # example: `SOL_Y`
        for id_s, slave_group in logger.slaves.items():
            prefix_s = slave_group.custom_id or f"{prefix_l}{id_s}"  # example: `SOL_Y3`
            slave_group.effective_id = prefix_s
            name_s = slave_group.custom_name or prefix_s
            name_bridge = f"{prefix_l}{id_s}: {slave_group.name}"  # example: `SOL_Y3: Inverter Bldg C 90kW (O3)`
            # example: `Bridge modbus:tcp:SOL_Y3 "SOL_Y3: Inverter Bldg C 90kW (O3)" [ host="192.168.2.12", id="103" ] {`
            with Block(things, f'Bridge modbus:tcp:{prefix_s} "{name_bridge}" [ host="{logger.ip}", id="{logger.slave_offset + id_s}" ]') as br:
                for slave in slave_group.slaves:
                    slave_name_s = slave.custom_name or name_s
                    slave_prefix_s = "" if slave_group.custom_id == "" else prefix_s
                    if slave.custom_id:
                        slave_prefix_s = "_".join(filter(None, (slave_prefix_s, slave.custom_id)))
                    slave.prefix = slave_prefix_s
                    group_s = f"g{slave_prefix_s.capitalize()}"  # example: gSOL_Y3
                    group_s = re.sub(r"_([a-z])", lambda m: m.group(1).upper(), group_s)  # example: gSolY3
                    group = OHGroup(id=group_s, name=f"{slave_prefix_s}", slave=slave)
                    # example: `Group gSolY3 "SOL_Y3 (Inverter Bldg C 90kW (O3))" <solarplant> (gModbus,gC3) ["Inverter"]`
                    items.write(f"{group}\n")
                    for group in slave.get_prop_groups():
                        for poller in split_props(group):
                            id_p = f"{slave_prefix_s}_{poller.id}"  # example: `SOL_Y3_General`

                            # TODO(zdimension): for some reason, if we want to query values starting at A, we need to start at A-1
                            # this is counterintuitive and should be investigated one day
                            # till then we're fetching one more register than we need to
                            # => this is not an inclusive-exclusive problem: if we use incorrect bounds, openHAB complains

                            bridge = OHPollerBridge(
                                id=id_p,
                                name=f"{slave_name_s}: {poller.name}",  # example: `SOL_Y3: General`
                                start=poller.start + slave.offset,
                                length=poller.length + group.offset,
                                type_=group.type_
                            )
                            # example: `Bridge poller SOL_Y3_General "SOL_Y3: General" [ start="40580", length="3", type="holding", maxTries="1" ] {`
                            with Block(br, bridge) as po:
                                for p in poller.props:
                                    display_name = f"{slave_name_s}: {p.display_name}"  # example: `SOL_Y3: Temperature`
                                    id_t = f"{slave_prefix_s.lower()}_{p.id}"  # example: `sol_y3_temp`

                                    transforms = []
                                    if p.valtype.xform:
                                        transforms.append(
                                            f"JS:{p.valtype.xform}.js")
                                    if p.valtype.null:
                                        transforms.append(
                                            f"JS:null.js?when={p.valtype.null}")  # example: `JS:null.js?when=32768`

                                    oh_thing = OHThing(
                                        id=id_t,
                                        name=display_name,
                                        group=slave.group,
                                        address=p.address + slave.offset + group.offset,
                                        type_=p.valtype,
                                        transforms=transforms
                                    )
                                    # example: `Thing data sol_y3_temp "SOL_Y3: Température" @ "C3" [ readStart="40581", readValueType="float32" ]`
                                    po.write(f"{oh_thing}\n")

                                    item = OHNumber(
                                        id=id_t,
                                        name=display_name,
                                        format_string=p.get_format_string(),
                                        quantity=p.quantity,
                                        icon=p.icon,
                                        group=group_s,
                                        prefix=prefix_s,
                                        bridge=bridge,
                                        gain_string=p.get_gain_string(),
                                        location=slave.group
                                    )
                                    # example: `Number:Temperature sol_y3_temp "SOL_Y3: Temperature [%.1f °C]" <temperature> (gModbus,
                                    # gPvT4) ["Measurement", "Temperature"] {channel="modbus:data:SOL_Y3:SOL_Y3_General:sol_y3_temp:number" [
                                    # profile="modbus:gainOffset", gain="1.0 °C"], influxdb="sol_y3_temp" [location="C3", building="C", floor="3"]}`
                                    items.write(f"{item}\n")
                    items.write("\n")


class Block:
    """
    Helper class for writing indented blocks.

    A block has a name. When entering the block, `name {` is written, and when exiting the block, `}` is written.
    """
    indent: int

    def __init__(self, file: Union[TextIO, "Block"], name):
        """
        :param file: the parent file or block. If a block, the indent will be increased by 1.
        :param name: the name of the block
        """
        self.file = file
        self.name = name
        self.indent = (file.indent + 1) if isinstance(file, Block) else 1

    def __enter__(self):
        self.file.write(f"{self.name} {{\n")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.write("}\n")

    def write(self, s: AnyStr):
        self.file.write(f"    {s}")


MAX_POLLER_LEN = 120
"""Maximum length of a Modbus poller (in reality, this is supposed to be around 125, but we round down to 120 to make sure it always works)"""


@dataclass
class SplitProps:
    id: str
    """Identifier"""
    name: str
    """Display name"""
    start: int
    """Start address"""
    length: int
    """Number of registers"""
    props: list[ModbusProp]
    """List of properties"""


def proplist_len(plist: list[ModbusProp], start: int, end: int) -> int:
    """
    Total size (in registers) of the property list from index start to index end. Accounts for space inbetween properties if present.

    -1 can be used as the end index to indicate the end of the list.
    """
    return plist[end].address - plist[start].address + plist[end].valtype.size


def split_props(group: PropGroup) -> Iterator[SplitProps]:
    """
    Split a group of properties into multiple groups of at most MAX_POLLER_LEN properties.
    """

    start = 0
    sub_id = 1

    # How the algorithm works:
    # 1. We start at the beginning of the list of properties
    # 2. We find the last property such as all properties up to it fit in a poller of length MAX_POLLER_LEN
    # 3. We yield a poller with the properties from the start to the last property
    # 4. We keep on going with the properties after the last property
    # In other words, we greedily try to fit as many properties as possible in a poller, and when it's full, we start a new one.
    while start < len(group.props):
        last = len(group.props) - 1
        while proplist_len(group.props, start, last) > MAX_POLLER_LEN:
            last -= 1
        real_props = group.props[start:last + 1]
        id_p_real = group.id
        name_real = group.name
        if start != 0:
            sub_id += 1
            id_p_real = f"{id_p_real}_{sub_id}"
            name_real = f"{name_real} (part {sub_id})"
        start = last + 1
        length = proplist_len(real_props, 0, -1)
        start_addr = real_props[0].address
        yield SplitProps(id_p_real, name_real, start_addr, length, real_props)
