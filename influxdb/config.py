import os
import re

import influxdb_client
from utils.env import get_env
from influxdb_client import TaskCreateRequest

from openhab.modbus import ModbusMaster

org = get_env("INFLUX_ORG")
token = get_env("INFLUX_TOKEN")
url = get_env("INFLUX_URL")

id_count = 0


def check_id():
    """
    Returns a new ID for an InfluxDB check

    The generated IDs are in the form 55555555xxxxxxxx where the second part is a hexadecimal counter starting at 1
    """
    global id_count
    id_count += 1
    return f"55555555{id_count:08x}"


def gen_tasks(files: dict[str, list[ModbusMaster]], dry_run=False):
    if not dry_run:
        client = influxdb_client.InfluxDBClient(url=url, token=token, org=org, debug=False)

        labels_api = client.labels_api()
        lbl = [l for l in labels_api.find_labels() if l.name == "generated"]
        if len(lbl) == 0:
            label = labels_api.create_label("generated", org)
        else:
            label = lbl[0]

        tasks_api = client.tasks_api()
        existing = [t for t in tasks_api.find_tasks(type="basic") if label in t.labels]
        for task in existing:
            tasks_api.delete_task(task.id)

    from jinja2 import environment

    jinja_env = environment.Environment()
    jinja_env.globals["check_id"] = check_id

    def surround_by_quote(x):
        return f'"{x}"'

    jinja_env.filters["quote"] = surround_by_quote

    jinja_env.globals["files"] = files

    from pathlib import Path
    task_dir = Path(os.path.dirname(__file__)) / "tasks"
    gen_dir = Path(os.path.dirname(__file__)) / "generated"
    for file in os.listdir(task_dir):
        if file.endswith(".flux"):
            path = task_dir / file
            # jinja2 the code
            with open(path, "r", encoding="utf-8") as f:
                # render the template
                flux = jinja_env.from_string(f.read()).render()
            flux = re.sub(r"\n\s*\n", "\n", flux)

            with open((gen_dir / file), "w", encoding="utf-8") as f:
                f.write(flux)

            if dry_run:
                continue

            # create the task
            task_request = TaskCreateRequest(flux=flux, org_id=org, status="active")
            task = tasks_api.create_task(task_create_request=task_request)

            tasks_api.add_label(label.id, task.id)
