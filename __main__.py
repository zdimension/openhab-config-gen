import sys
from os import path

sys.path.append(path.dirname(path.abspath(__file__)))  # noqa

from devices.bluelog import *
from devices.evlink import *
from devices.powidian import *
from gen_conf import gen_conf
from influxdb.config import gen_tasks
from openhab.modbus import *
from openhab.ping_check import gen_ping_check


files = {
    "sol": [
        ModbusMaster("192.168.2.12", "Y", {
            1: BlueLogInverter("Inverter Bldg A 110kW (O1)", "A4"),
            2: BlueLogInverter("Inverter Bldg B 60kW (O2)", "B4"),
            3: BlueLogInverter("Inverter Bldg C 90kW (O3)", "C3"),
            6: BlueLogInverter("Inverter Park 3 150kW (O6)", "P3"),
            9: BlueLogSensor("Weather sensor Park 6", "P3"),
        }),
        ModbusMaster("192.168.3.11", "Z", {
            8: BlueLogInverter("Inverter Bldg D 150kW", "D3"),
            9: BlueLogSensor("Weather sensor Bldg D", "D3"),
        }),
    ],
    "ev": [
        ModbusMaster("192.168.2.21", "", {
            1: EvlinkPro("Station P3 01", "P3"),
        }),
        ModbusMaster("192.168.2.22", "", {
            2: EvlinkPro("Station P3 02", "P3"),
        }),
        ModbusMaster("192.168.2.23", "", {
            3: EvlinkPro("Station P3 03", "P3"),
        }),
        ModbusMaster("192.168.2.24", "", {
            4: EvlinkPro("Station P3 04", "P3"),
        }),
    ],
    "h2": [
        ModbusMaster("192.168.2.31", "", {
            1: PowiDian("PowiDian H2", "P3"),
        }, 0)
    ],
}

ignore = set()  # configurations not yet used in openHAB

if __name__ == "__main__":
    args = set(sys.argv)

    for file, masters in files.items():
        gen_conf(file, masters, unused=file in ignore)

    gen_tasks(files, dry_run={"-t", "--no-tasks"} & args)

    gen_ping_check({f: m for f, m in files.items() if f not in ignore})