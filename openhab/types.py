from dataclasses import dataclass, replace
from typing import Optional

ModbusType = str


@dataclass
class ValType:
    openhab: ModbusType
    """Base openHAB Modbus data type"""
    size: int
    """Size in Modbus registers"""
    scale: float = 1
    """Scale factor (10 means that the value returned by the equipment is 10 times the actual, physical value)"""
    xform: str = None
    """JS Transform file to apply"""
    null: int = None
    """Value to consider as null/UNDEF"""
    swap: bool = False
    """Inverse endianness (swap register order for multi-register types)"""

    def __call__(self, **kwds) -> "ValType":
        """Override attributes"""
        return replace(self, **kwds)

    def openhab_full(self) -> ModbusType:
        """Return full openHAB type"""
        if self.swap:
            return f"{self.openhab}_swap"
        else:
            return self.openhab


# cf https://www.openhab.org/addons/bindings/modbus/#value-types-on-read-and-write
U16 = ValType("uint16", 1)
U16s = U16(swap=True)
U32 = ValType("uint32", 2)
U32s = U32(swap=True)
U64 = ValType("uint64", 4)
I16 = ValType("int16", 1)
I32 = ValType("int32", 2)
I32s = I32(swap=True)
I64 = ValType("int64", 4)
F32 = ValType("float32", 2)

OHIcon = str
OHQuantity = str
OHTag = str


# quantities, cf https://www.openhab.org/docs/concepts/units-of-measurement.html#list-of-units
TEMP = "Temperature"
POWER = "Power"
VOLTAGE = "ElectricPotential"
CURRENT = "ElectricCurrent"
FREQUENCY = "Frequency"
RESISTANCE = "ElectricResistance"
ANGLE = "Angle"
SPEED = "Speed"
LENGTH = "Length"
PRESSURE = "Pressure"
TIME = "Time"
LIGHT = "Intensity"
ENERGY = "Energy"
VOLUME = "Volume"
VOLUME_RATE = "VolumetricFlowRate"
CONDUCTIVITY = "ElectricConductivity"
AREAL_DENSITY = "ArealDensity"
ILLUMINANCE = "Illuminance"


def quantity_to_property(quantity: OHQuantity) -> Optional[OHTag]:
    """
    Returns the property name for the given quantity.

    If there is no property for the given quantity, returns None.
    """
    return {
        LIGHT: "Light",
        ILLUMINANCE: "Light",
        ENERGY: "Energy",
        FREQUENCY: "Frequency",
        CURRENT: "Current",
        PRESSURE: "Pressure",
        POWER: "Power",
        TEMP: "Temperature",
        VOLTAGE: "Voltage",
    }.get(quantity)


def fix_unit_openhab(unit: str) -> str:
    """Some real-world units are not supported out-of-the-box by openHAB.

    Sometimes, it's a problem of casing: VAr is commonly used, but openHAB expects var. A common accepted symbol for liter is L, but openHAB expects l.

    Other times, it's because the unit is equivalent to another and only differs by name: rpm is equivalent to Hz, since both are dimensionally equivalent
    to 1/s.
    """
    return {
        "VAr": "var",
        "VARh": "varh",
        "rpm": "Hz",
        "L": "l",
        "NL/h": "l/h"
    }.get(unit, unit)


# icons, cf https://www.openhab.org/docs/configuration/iconsets/classic/
I_TEMP = "temperature"
I_ENER = "energy"
