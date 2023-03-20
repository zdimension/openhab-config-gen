import "influxdata/influxdb/monitor"
import "influxdata/influxdb/schema"
import "experimental"
import "dict"

{% set measures = namespace (names = []) %}
measures = [{% for masters in files.values() %}
    {% for master in masters %}
        {% for group in master.slaves.values() %}
            {% for slave in group.slaves %}
                {% for alert in slave.get_alerts() %}
                    {% set name = slave.prefix.lower() ~ "_" ~ alert.field %}
                    {{ measures.names.append(name) or "" }}
                    "{{name}}": {
                        crit: (r) => {{ alert.flux() }}, 
                        message: (r) => "Equipment `{{ slave.name }}` (${ r.location }) {{ alert.message() }}"
                    },
                {% endfor %}
            {% endfor %}
        {% endfor %}
    {% endfor %}
{% endfor %}]

data = from(bucket: "demobucket")
|> range(start: -60s)
|> filter(fn: (r) => contains(value: r._measurement, set: [{{ measures.names | map("quote") | join(", ") }}]))
|> filter(fn: (r) => r._field == "value")
|> last()

check = { _check_id: "{{ check_id() }}", 
  _check_name: "Python alerts",
  _type: "deadman",
  tags: {deadman: "deadman"}}

deadmanDuration = 30s

getData = (r) => dict.get(dict: measures, key: r._source_measurement, default: {
    crit: (r) => false, 
    message: (r) => (if r._level == "crit" then "Alert on field ${ r._field }" else "Field ${ r._field } is OK") + ", no message defined"
})
messageFn = (r) => getData(r).message(r)
crit = (r) => getData(r).crit(r)

data
|> schema.fieldsAsCols()
|> monitor.check(data: check, messageFn: messageFn, crit: crit)

option task = {name: "Python alerts task", every: 30s, offset: 0s}