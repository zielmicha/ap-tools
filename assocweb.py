from flask import Flask
import cgi
import json
app = Flask(__name__)

mac_table = {}
try:
    with open('/usr/share/wireshark/manuf') as f:
        for line in f:
            a = line.split()
            if len(a) < 2: continue
            mac_table[a[0]] = a[1]
except IOError as err:
    print 'failed to read DB', err

@app.route("/")
def hello():
    return open('static/index.html').read()

@app.route("/stations.json")
def stations():
    return open('stations.html').read()

def find_vendor(mac):
    for i in reversed(range(len(mac))):
        addr = mac_table.get(mac[:i])
        if addr:
            return addr

def pp_mac(mac):
    description = find_vendor(mac) or ''
    if description:
        description = ' (%s)' % description
    return mac + description

@app.route("/stations.html")
def stationshtml():
    out = []
    cols = ['ap', 'mac', 'tx', 'rx', 'power']
    out.append('<table class=table>')
    out.append('<tr>')
    for col in cols:
        out.append('<th>%s' % col)
    data = json.load(open('stations.json'))
    for item in data:
        item['mac'] = pp_mac(item['mac'])
    data.sort(key=lambda d:
              (d['mac'], d['ap']))
    for item in data:
        out.append('<tr>')
        for col in cols:
            out.append('<td>%s' % cgi.escape(str(item[col])))

    return '\n'.join(out)

if __name__ == "__main__":
    app.run(debug=1)
