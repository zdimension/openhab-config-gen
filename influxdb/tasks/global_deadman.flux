import "influxdata/influxdb/monitor"
import "influxdata/influxdb/schema"
import "experimental"
import "dict"

measures = [{% for masters in files.values() %}
    {% for master in masters %}
        {% for group in master.slaves.values() %}
            {% for slave in group.slaves %}
                {% if slave.deadman != None %}
                    "{{slave.prefix.lower()}}_{{ slave.deadman }}": "{{ slave.name }}",
                {% else %}
                    // no monitoring for `{{ slave.name }}` ({{ slave.__class__.__name__ }})
                {% endif %}
            {% endfor %}
        {% endfor %}
    {% endfor %}
{% endfor %}]

data = from(bucket: "demobucket")
|> range(start: -60s)
|> filter(fn: (r) => dict.get(dict: measures, key: r._measurement, default: "") != "")
|> filter(fn: (r) => r._field == "value")

check = { _check_id: "{{ check_id() }}", 
  _check_name: "Global deadman",
  _type: "deadman",
  tags: {deadman: "deadman"}}

deadmanDuration = 30s // TODO(zdimension): granularity by equipment type

status = (dead) => if dead then "has not responded for ${deadmanDuration}" else "is responding"
messageFn = (r) => "Equipment `${ dict.get(dict: measures, key: r._source_measurement, default: r._source_measurement) }` (${ r.location }) ${ status(dead: r.dead) }"
crit = (r) => r.dead

data
|> schema.fieldsAsCols()
|> monitor.deadman(t: experimental.subDuration(from: now(), d: deadmanDuration))
|> monitor.check(data: check, messageFn: messageFn, crit: crit)

option task = {name: "Global deadman task", every: 10s, offset: 0s}