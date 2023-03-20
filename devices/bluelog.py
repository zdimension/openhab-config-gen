from influxdb.types import *
from openhab.modbus import *
from openhab.types import *


class BlueLogBase(SlaveBase):
    """
    Base object exposed by a BlueLog logger
    """

    props: ClassVar = PropGroup("General", "General", [
        (40580, F32, I_TEMP, "temp", "Temperature", TEMP, "%.1f", "°C"),
    ])
    deadman: ClassVar = "temp"


class BlueLogInverter(BlueLogBase):
    """
    Electrical inverter
    """

    icon: ClassVar = "solarplant"
    tags: ClassVar = ["Inverter"]
    props: ClassVar = PropGroup("Electrical", "Electrical", [
        (41000, F32, I_ENER, "p_ac", "Power AC", POWER, "%.1f", "W"),
        (41002, F32, I_ENER, "q_ac", "Reactive power", POWER, "%.1f", "VAr"),
        (41004, F32, I_ENER, "s_ac", "Apparent power", POWER, "%.1f", "VA"),
        (41006, F32, I_ENER, "cos_phi", "Power factor (cos phi)", None, "%.2f", None),
        (41008, F32, I_ENER, "u_ac", "Voltage AC", VOLTAGE, "%.1f", "V"),
        (41010, F32, I_ENER, "i_ac", "Current AC", CURRENT, "%.1f", "A"),
        (41012, F32, I_ENER, "f_ac", "Grid frequency", FREQUENCY, "%.1f", "Hz"),
        (41014, F32, I_ENER, "r_iso", "Insulation resistance", RESISTANCE, "%.1f", "Ohm"),
        *seq(3, (41016, F32, I_ENER, "p_ac%d", "Power AC phase %d", POWER, "%.1f", "W")),
        *seq(3, (41022, F32, I_ENER, "q_ac%d", "Reactive power phase %d", POWER, "%.1f", "VAr")),
        *seq(3, (41028, F32, I_ENER, "s_ac%d", "Apparent power phase %d", POWER, "%.1f", "VA")),
        *seq(3, (41034, F32, I_ENER, "cos_phi%d", "Power factor (cos phi) phase %d", None, "%.2f", None)),
        *seq(3, (41040, F32, I_ENER, "u_ac%d", "Voltage AC phase %d", VOLTAGE, "%.1f", "V")),
        (41046, F32, I_ENER, "u_ac_l1l2", "Phase voltage L1L2", VOLTAGE, "%.1f", "V"),
        (41048, F32, I_ENER, "u_ac_l2l3", "Phase voltage L2L3", VOLTAGE, "%.1f", "V"),
        (41050, F32, I_ENER, "u_ac_l3l1", "Phase voltage L3L1", VOLTAGE, "%.1f", "V"),
        *seq(3, (41052, F32, I_ENER, "i_ac%d", "Current AC phase %d", CURRENT, "%.1f", "A")),
        *seq(3, (41058, F32, I_ENER, "f_ac%d", "Grid frequency phase %d", FREQUENCY, "%.1f", "Hz")),
        (41064, F32, I_ENER, "e_day", "Energy generated per day", POWER, "%.1f", "Wh"),
        (41066, F32, I_ENER, "e_total", "Energy total", POWER, "%.1f", "kWh"),
        (41068, F32, I_ENER, "ot_ac_total", "Total operating hours", TIME, "%.1f", "h"),
        (41070, F32, I_ENER, "ft_ac_total", "Total feed-in hours", TIME, "%.1f", "h"),
        (41072, F32, I_ENER, "u_dc_pe", "Voltage DC positive pole to earth", VOLTAGE, "%.1f", "V"),
        (41074, F32, I_ENER, "u_dc_ne", "Voltage DC negative pole to earth", VOLTAGE, "%.1f", "V"),
        (41076, F32, I_ENER, "p_ac_set_abs", "Absolute active power setpoint", POWER, "%.1f", "W"),
        (41078, F32, I_ENER, "p_ac_set_rel", "Relative active power setpoint", None, "%.1f", "%"),
        (41080, F32, I_ENER, "p_dc", "Power DC", POWER, "%.1f", "W"),
        (41082, F32, I_ENER, "u_dc", "Voltage DC", VOLTAGE, "%.1f", "V"),
        (41084, F32, I_ENER, "i_dc", "Current DC total", CURRENT, "%.1f", "A"),
        *seq(12,
             (41100, F32, I_ENER, "p_dc%d", "Power DC MPPT %d", POWER, "%.1f", "W"),
             (41102, F32, I_ENER, "u_dc%d", "Voltage DC MPPT %d", VOLTAGE, "%.1f", "V"),
             (41104, F32, I_ENER, "i_dc%d", "Current DC MPPT %d", CURRENT, "%.1f", "A"),
             ),
        (41800, F32, I_ENER, "r_ac", "Grid impedance", RESISTANCE, "%.1f", "Ohm"),
    ])
    alerts: ClassVar = [
        RangeAlert("temp", -25, 60)
    ]


class BlueLogSensor(BlueLogBase):
    """
    Sensor
    """

    tags: ClassVar = ["Sensor"]
    props: ClassVar = PropGroup("Sensor", "Capteur", [
        (42000, F32, "wind", "e_w_d", "Wind direction", ANGLE, "%.1f", "°"),
        (42002, F32, "wind", "e_w_s", "Wind speed", SPEED, "%.1f", "m/s"),
        (42004, F32, "climate", "e_alt1", "Altitude", LENGTH, "%.1f", "m"),
        (42006, F32, "rain", "e_precipitation", "Precipitation type", None, "%.1f", ""),
        (42008, F32, "rain", "e_rf_abs1", "Precipitation quantity absolute", LENGTH, "%.1f", "mm"),
        (42010, F32, "rain", "e_rf_i1", "Precipitation intensity", SPEED, "%.1f", "mm/h"),
        (42012, F32, "rain", "e_ah_abs1", "Humidity absolute 1", AREAL_DENSITY, "%.1f", "g/m²"),
        (42014, F32, "rain", "e_ah_rel1", "Humidity relative", None, "%.1f", "%"),
        (42016, F32, "pressure", "e_ap_abs1", "Air pressure absolute", PRESSURE, "%.1f", "hPa"),
        (42018, F32, "pressure", "e_ap_rel1", "Air pressure relative", PRESSURE, "%.1f", "hPa"),
        (42020, F32, "pressure", "e_ip_abs", "Internal air pressure", PRESSURE, "%.1f", "hPa"),
        (42022, F32, "humidity", "e_ih_rel", "Internal relative humidity", None, "%.1f", "%"),
        (42024, F32, "fan", "e_f_s", "Fan speed", SPEED, "%.1f", "rpm"),
        (42030, F32, "sun", "sun_h", "Sunshine duration", TIME, "%.1f", "h"),
        (42032, F32, "niveau", "e_tilt", "Sensor tilt", ANGLE, "%.1f", "°"),
        (42034, F32, "sun", "e_srad", "Global irradiation energy", LIGHT, "%.1f", "Wh/m²"),
        (42036, F32, "sun", "srad", "Irradiance", LIGHT, "%.1f", "W/m²"),
        *seq(5, (42038, F32, "sun", "srad%d", "Irradiance %d", LIGHT, "%.1f", "W/m²")),
        (42048, F32, I_TEMP, "t", "Temperature", TEMP, "%.1f", "°C"),
        *seq(20, (42050, F32, I_TEMP, "t%d", "Temperature %d", TEMP, "%.1f", "°C")),
        *seq(2, (42090, F32, I_ENER, "i_sc%d", "Short circuit current %d", CURRENT, "%.1f", "A")),
        (42094, F32, "solarplant", "sli_raw", "Soiling loss raw", None, "%.1f", "%"),
        (42096, F32, "solarplant", "sli", "Soiling loss", None, "%.1f", "%"),
        *seq(2, (42098, F32, "solarplant", "sli%d", "Soiling loss %d", None, "%.1f", "%")),
        (42102, F32, "rain", "e_rf_dif", "Differential precipitation", LENGTH, "%.1f", "mm"),
        *seq(5, (42104, F32, "rain", "e_rf_dif%d", "Differential precipitation %d", LENGTH, "%.1f", "mm")),
        (42114, F32, "wind", "e_w_s_max", "Maximum wind speed", SPEED, "%.1f", "m/s"),
        *seq(5, (42116, F32, "wind", "e_w_s%d_max", "Maximum wind speed %d", SPEED, "%.1f", "m/s")),
        *seq(5, (42126, F32, "wind", "e_w_s%d", "Wind speed %d", SPEED, "%.1f", "m/s")),
        *seq(5, (42136, F32, "wind", "e_w_d%d", "Wind direction %d", ANGLE, "%.1f", "°")),
        (42146, F32, "sun", "illuminance", "Illuminance", ILLUMINANCE, "%.1f", "lx"),
        (42150, F32, "snow", "e_snow_depth", "Snow depth", LENGTH, "%.1f", "m"),
        *seq(4, (42152, F32, "snow", "snow_load%d", "Snow load %d", AREAL_DENSITY, "%.1f", "g/m²")),
        (42170, F32, "water", "water_depth", "Water depth", LENGTH, "%.1f", "m"),
        *seq(9, (42180, F32, "solarplant", "sr%d", "Soiling ratio %d", None, "%.1f", "%")),
    ])
    alerts: ClassVar = [
        RangeAlert("temp", -35, 80)
    ]
