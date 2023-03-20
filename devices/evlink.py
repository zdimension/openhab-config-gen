from openhab.modbus import *
from openhab.types import *


class EvlinkPro(SlaveBase):
    """
    Schneider Electric EVLink Pro AC charger
    """

    icon: ClassVar = "poweroutlet_eu"
    tags: ClassVar = ["PowerOutlet"]
    props: ClassVar = PropGroup("EVLinkPro", "EVLink Pro", [
        (1, U16, I_ENER, "ev_state", "Status of the vehicle", None, "%d", None),
        (150, U16, I_ENER, "ocpp_status", "OCPP charging station status", None, "%d", None),
        (1150, U16, I_ENER, "ev_presence", "Presence of the vehicle", None, "%d", None),
        *seq(3, (2999, F32, I_ENER, "i%d", "Current on phase %d", CURRENT, "%.1f", "A")),
        (3009, F32, I_ENER, "i_avg", "Average current", CURRENT, "%.1f", "A"),
        *seq(3, (3027, F32, I_ENER, "u%d", "Voltage on phase %d", VOLTAGE, "%.1f", "V")),
        (3035, F32, I_ENER, "u_avg", "Average voltage", VOLTAGE, "%.1f", "V"),
        *seq(3, (3053, F32, I_ENER, "p%d", "Active power on phase %d", POWER, "%.1f", "W")),
        (3059, F32, I_ENER, "p_tot", "Total active power", POWER, "%.1f", "W"),
        (3075, F32, I_ENER, "s_tot", "Total apparent power", POWER, "%.1f", "VA"),
        (3083, F32, I_ENER, "pf", "Power factor", None, "%.2f", None),
        (3109, F32, I_ENER, "f", "Frequency", FREQUENCY, "%.1f", "Hz"),
        (3203, I64, I_ENER, "e_tot", "Total active energy counter", ENERGY, "%d", "Wh"),
        (3219, I64, I_ENER, "e_react_tot", "Total reactive energy counter", ENERGY, "%d", "VARh"),
        (4003, U16, I_ENER, "setpoint", "Remote energy management setpoint", CURRENT, "%d", "A"),
        (4004, U16, I_ENER, "setpoint_degraded_mono", "Remote energy management degraded setpoint (monophase)", CURRENT, "%d", "A"),
        (4005, U16, I_ENER, "setpoint_degraded_tri", "Remote energy management degraded setpoint (three-phase)", CURRENT, "%d", "A"),
        (4006, U16, I_ENER, "contactor_charging_time", "Current charging time (duration since contactor closed)", TIME, "%d", "s"),
        (4008, U16, I_ENER, "session_charging_time", "Current session charging time (duration since transaction started)", TIME, "%d", "s"),
        (4011, U32, I_ENER, "session_energy", "Consumed energy during current session", ENERGY, "%d", "Wh"),
    ])
    deadman: ClassVar = "ev_state"
