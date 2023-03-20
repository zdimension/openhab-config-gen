from openhab.modbus import *
from openhab.types import *


class PowiDian(SlaveBase):
    """
    PowiDian H2

    (French names and descriptions since this is a French brand)
    """

    icon: ClassVar = "battery"
    tags: ClassVar = ["Battery"]
    props: ClassVar = PropGroup("PowiDian", "PowiDian H2", [
        (1010, U16(null=65535, scale=100), I_ENER, "cap_tot", "Capacité totale de stockage", ENERGY, "%.1f", "kWh"),
        (1011, U16(null=65535, scale=100), I_ENER, "cap_util", "Capacité utile de stockage", ENERGY, "%.1f", "kWh"),
        (1012, U16(null=65535, scale=1), I_ENER, "level", "Niveau du stockage H2", None, "%.1f", "%"),
        (1013, U16(null=65535, scale=1), I_ENER, "press", "Pression du stockage H2", PRESSURE, "%.1f", "bar"),
        (1014, U16(null=65535, scale=100), I_ENER, "ener", "Énergie disponible de l'unité H2", ENERGY, "%.1f", "kWh"),
        (1020, I16(null=-32768, scale=100), I_ENER, "pwr_act_ac", "Puissance active côté AC de l'unité H2", POWER, "%.1f", "W"),
        (1030, U16(null=65535, scale=10), I_ENER, "el_rate_h2", "Électrolyseurs Débit H2", VOLUME_RATE, "%.1f", "NL/h"),
        (1041, I16(null=-32768, scale=10), I_ENER, "el1_volt", "Électrolyseur 1 : Stack Tension", VOLTAGE, "%.1f", "V"),
        (1042, I16(null=-32768, scale=10), I_ENER, "el1_curr", "Électrolyseur 1 : Stack Intensité", CURRENT, "%.1f", "A"),
        (1051, I16(null=-32768, scale=10), I_ENER, "el2_volt", "Électrolyseur 2 : Stack Tension", VOLTAGE, "%.1f", "V"),
        (1052, I16(null=-32768, scale=10), I_ENER, "el2_curr", "Électrolyseur 2 : Stack Intensité", CURRENT, "%.1f", "A"),
        (1060, I16(null=-32768, scale=10), I_ENER, "dryer_press", "Dryer : Sortie : Pression", PRESSURE, "%.1f", "bar"),
        (1070, I16(null=-32768, scale=1), I_ENER, "water_cond", "Réservoir d'eau : Conductivité", CONDUCTIVITY, "%.1f", "µS/cm"),
        (1071, U16(null=32768, scale=10), I_ENER, "water_vol", "Réservoir d'eau : Volume d'eau disponible", VOLUME, "%.1f", "L"),
        (1080, U16(null=65535, scale=100), I_ENER, "pwr_prod", "Puissance de production d'électricité (en sortie de PAC DC)", POWER, "%.1f", "kW"),
        (1091, U16(null=65535, scale=10), I_ENER, "pac1_volt", "PAC 1 : Tension", VOLTAGE, "%.1f", "V"),
        (1092, U16(null=65535, scale=10), I_ENER, "pac1_curr", "PAC 1 : Intensité", CURRENT, "%.1f", "A"),
        (1101, U16(null=65535, scale=10), I_ENER, "pac2_volt", "PAC 2 : Tension", VOLTAGE, "%.1f", "V"),
        (1102, U16(null=65535, scale=10), I_ENER, "pac2_curr", "PAC 2 : Intensité", CURRENT, "%.1f", "A"),
        (1110, I16(null=-32768, scale=10), I_TEMP, "t_int", "Température intérieure", TEMP, "%.1f", "°C"),
        (1111, I16(null=-32768, scale=10), I_TEMP, "t_ext", "Température extérieure", TEMP, "%.1f", "°C"),
        (1140, U16(null=65535, scale=1), I_ENER, "batt_soc", "Batteries SOC", None, "%.1f", "%"),
        (1141, I16(null=-32768, scale=10), I_ENER, "batt_curr", "Batteries Intensité", CURRENT, "%.1f", "A"),
        (1142, U16(null=65535, scale=10), I_ENER, "batt_volt", "Batteries Tension", VOLTAGE, "%.1f", "V"),
        (1143, I16(null=-32768, scale=10), I_TEMP, "batt_temp", "Batteries Température", TEMP, "%.1f", "°C"),
        (1144, U16(null=65535, scale=1), I_ENER, "batt_soh", "Batterie SOH", None, "%.1f", "%"),
        (1150, I32(null=-2147418113, scale=1), I_ENER, "bluelog_pwr", "Bluelog puissance disponible", POWER, "%.1f", "W"),
        (1151, U16(null=65535, scale=1), I_ENER, "bluelog_irr", "Bluelog irradiation", LIGHT, "%.1f", "W/m²"),
    ], "input", 0)
    deadman: ClassVar = "t_ext"
