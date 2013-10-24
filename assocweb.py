from flask import Flask
import cgi
import json
app = Flask(__name__)

@app.route("/")
def hello():
    return open('static/index.html').read()

@app.route("/stations.json")
def stations():
    return open('stations.html').read()

@app.route("/stations.html")
def stationshtml():
    out = []
    cols = ['ap', 'mac', 'tx', 'rx', 'power']
    out.append('<table class=table>')
    out.append('<tr>')
    for col in cols:
        out.append('<th>%s' % col)
    data = json.load(open('stations.json'))
    data.sort(key=lambda data:
              (data['mac'], data['ap']))
    for item in data:
        out.append('<tr>')
        for col in cols:
            out.append('<td>%s' % cgi.escape(str(item[col])))

    return '\n'.join(out)

if __name__ == "__main__":
    app.run(debug=1)
