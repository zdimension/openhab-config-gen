# openhab-config-gen

Automatically generate openHAB configuration files, InfluxDB alerts and ping checks from a list of Modbus-over-TCP equipments.

## Example

### Input

```py
files = {
    "sol": [
        ModbusMaster("192.168.2.12", "Y", {
            1: BlueLogInverter("Inverter Bldg A 110kW (O1)", "A4"),
            2: BlueLogInverter("Inverter Bldg B 60kW (O2)", "B4"),
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
    ],
    "h2": [
        ModbusMaster("192.168.2.31", "", {
            1: PowiDian("PowiDian H2", "P3"),
        }, 0)
    ],
}
```

### Output

sol.things:
```
Bridge modbus:tcp:SOL_Y1 "SOL_Y1: Inverter Bldg A 110kW (O1)" [ host="192.168.2.12", id="101" ] {
    Bridge poller SOL_Y1_General "SOL_Y1: General" [ start="40580", length="3", type="holding", maxTries="1" ] {
        Thing data sol_y1_temp "SOL_Y1: Temperature" @ "A4" [ readStart="40581", readValueType="float32" ]
    }
    Bridge poller SOL_Y1_Electrical "SOL_Y1: Electrical" [ start="41000", length="121", type="holding", maxTries="1" ] {
        Thing data sol_y1_p_ac "SOL_Y1: Power AC" @ "A4" [ readStart="41001", readValueType="float32" ]
        Thing data sol_y1_q_ac "SOL_Y1: Reactive power" @ "A4" [ readStart="41003", readValueType="float32" ]
        Thing data sol_y1_s_ac "SOL_Y1: Apparent power" @ "A4" [ readStart="41005", readValueType="float32" ]
        Thing data sol_y1_cos_phi "SOL_Y1: Power factor (cos phi)" @ "A4" [ readStart="41007", readValueType="float32" ]
        Thing data sol_y1_u_ac "SOL_Y1: Voltage AC" @ "A4" [ readStart="41009", readValueType="float32" ]
        ...
```

sol.items file:

```
Group gModbus (gInfluxDB)

Group gSolY1 "SOL_Y1 (Inverter Bldg A 110kW (O1))" <solarplant> (gModbus,gA4) ["Inverter"]
Number:Temperature sol_y1_temp "SOL_Y1: Temperature [%.1f °C]" <temperature> (gModbus,gSolY1) ["Measurement", "Temperature"] {channel="modbus:data:SOL_Y1:SOL_Y1_General:sol_y1_temp:number" [profile="modbus:gainOffset", gain="1.0 °C"], influxdb="sol_y1_temp" [location="A4", building="A", floor="4"]}
Number:Power sol_y1_p_ac "SOL_Y1: Power AC [%.1f W]" <energy> (gModbus,gSolY1) ["Measurement", "Power"] {channel="modbus:data:SOL_Y1:SOL_Y1_Electrical:sol_y1_p_ac:number" [profile="modbus:gainOffset", gain="1.0 W"], influxdb="sol_y1_p_ac" [location="A4", building="A", floor="4"]}
Number:Power sol_y1_q_ac "SOL_Y1: Reactive power [%.1f VAr]" <energy> (gModbus,gSolY1) ["Measurement", "Power"] {channel="modbus:data:SOL_Y1:SOL_Y1_Electrical:sol_y1_q_ac:number" [profile="modbus:gainOffset", gain="1.0 var"], influxdb="sol_y1_q_ac" [location="A4", building="A", floor="4"]}
...
```

Measure alert:
```flux
measures = [
    "sol_y1_temp": {
        crit: (r) => r.value < -25 or r.value > 60, 
        message: (r) => "Equipment `Inverter Bldg A 110kW (O1)` (${ r.location }) has value `temp` ${ if r._level == "crit" then "out of" else "in" } range [-25, 60]: ${ r.value }"
    },
    "sol_y2_temp": {
        crit: (r) => r.value < -25 or r.value > 60, 
        ...
    },
    ...
]

data = from(bucket: "demobucket")
|> ...

...

getData = (r) => dict.get(dict: measures, key: r._source_measurement, default: {
    crit: (r) => false, 
    message: (r) => (if r._level == "crit" then "Alert on field ${ r._field }" else "Field ${ r._field } is OK") + ", no message defined"
})
messageFn = (r) => getData(r).message(r)
...

option task = {name: "Python alerts task", every: 30s, offset: 0s}
```

Deadman alert:
```flux
measures = [
  "sol_y1_temp": "Inverter Bldg A 110kW (O1)",
  "sol_y2_temp": "Inverter Bldg B 60kW (O2)",
  ...
  "h2_1_t_ext": "PowiDian H2",
]

data = from(bucket: "demobucket")
|> ...

deadmanDuration = 30s

status = (dead) => if dead then "has not responded for ${deadmanDuration}" else "is responding"
messageFn = (r) => "Equipment `${ dict.get(dict: measures, key: r._source_measurement, default: r._source_measurement) }` (${ r.location }) ${ status(dead: r.dead) }"
...

option task = {name: "Global deadman task", every: 10s, offset: 0s}
```

Ping check script (+ Dockerfile):
```py
...

ips={'192.168.2.12': ['SOL_Y1', 'SOL_Y2', ...], ...}

...

def send_openhab(id: str, val: bool):
    ...
    url = f"{OH_ROOT}/rest/things/modbus:tcp:{id}/enable"
    (payload, message) = ("true", "Enabling") if val else ("false", "Disabling")
    ...
    requests.put(url, data=payload, headers=headers)

while True:
    good, bad = multi_ping(ips.keys(), timeout=0.2, retry=0)
    for ip in good:
        for id in ips[ip]:
            send_openhab(id, True)
    for ip in bad:
        for id in ips[ip]:
            send_openhab(id, False)
    time.sleep(5)
```

## Basic usage

In the main directory, run the following in a shell to install the required Python packages:

```bash
make pip
```

Then, run:

```bash
make all
```

It will:
- generate .items and .things files, in the [`conf`](conf/) directory
- generate .flux files, in the [`influxdb/generated`](influxdb/generated/) directory
- push those .flux files to InfluxDB, creating tasks
- create and start a Docker container for the ping check script

A full documentation will be published soon™ (the existing one is in French and contains internal details that need to be expunged before publication).

## Motivation

This project originated as an academic research project during my fifth year of engineering school, at [Polytech Nice](https://polytech.univ-cotedazur.fr/), under the supervision of Prof. [Stéphane Lavirotte](http://stephane.lavirotte.com/). The original goal was to aid the "domotization" of the SophiaTech campus, by providing a unified platform for the management of the various sensors and actuators, such as:
- solar panels
- common areas lighting
- hydrogen cell
- electric vehicle charging stations

The associated research poster (in French) can be found [here](poster.pdf). A short (2 min) presentation video (in French) can be found [here](https://www.youtube.com/watch?v=r3ncQc7NW-0).

The project was the work of a three-person team:
- [Tom Niget](https://github.com/zdimension)
- [Emmeline Vouriot](https://github.com/emmvou)
- [Julien Whitfield](https://github.com/JulienWhitfield)

## License

This project is licensed under the terms of the [MIT license](LICENSE).

Not required by the license, but still appreciated: if you use this project, please let me know! I'd love to hear about it.
