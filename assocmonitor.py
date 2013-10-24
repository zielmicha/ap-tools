import paramiko
import os
import threading
import collections
import traceback
import time
import json
import Queue
import sys

PROBE_TIME = 3
SSH_TIMEOUT = 5
STATION_WAIT = 100

clients = Queue.Queue(0)

ips = [ '192.168.0.%d' % i for i in range(33, 38) + [44, 45] ]
password = open(os.path.expanduser('~/.wappassword')).read().strip()

Client = collections.namedtuple('Client',
                                'mac power time rx tx')

class Monitor:
    def __init__(self, ip):
        self.ip = ip
        self.client = None

    def connect(self):
        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.client.connect(self.ip, username='root', password=password,
                            timeout=SSH_TIMEOUT)

    def read_assoclist(self):
        stdin, stdout, stderr = self.client.exec_command('iwinfo wlan0 assoclist')

        def parse_speed_line(l):
            s = l.strip().split()
            assert s[0] in ('RX:', 'TX:')
            return float(s[1])

        iterator = iter(stdout)
        output = []
        for line in iterator:
            if line == 'No station connected\n':
                return []
            s = line.split()
            if not s:
                continue
            mac = s[0]
            power = int(0 if s[1] == 'unknown' else s[1])
            time = int(s[-3])
            rx = parse_speed_line(iterator.next())
            tx = parse_speed_line(iterator.next())
            output.append(Client(mac=mac,
                                 power=power,
                                 rx=rx,
                                 tx=tx,
                                 time=time / 1000.))
        return output

    def reconnect_wrapper(self, func):
        time = 1
        while True:
            try:
                if not self.client:
                    self.connect()
                return func()
            except Exception:
                traceback.print_exc()
                self.reconnect(sleep=time)
                time *= 2

    def reconnect(self, sleep=1):
        print >>sys.stderr, 'reconnecting in', sleep
        time.sleep(1)
        self.connect()

    def loop(self):
        while True:
            result = self.reconnect_wrapper(self.read_assoclist)
            for item in result:
                data = dict(item.__dict__,
                            ap=self.ip,
                            time=time.time() - item.time)
                clients.put(data)
            time.sleep(PROBE_TIME)

def dump_state(stations):
    data = json.dumps([s
                       for s in stations
                       if time.time() - s['time'] < STATION_WAIT])

    with open('stations.json', 'w') as f:
        f.write(data)

def main():
    for ip in ips:
        t = threading.Thread(target=Monitor(ip).loop)
        t.setDaemon(True)
        t.start()

    state = {}

    while True:
        item = clients.get()
        key = item['ap'], item['mac']
        if item['time'] > state.get(key, {}).get('time', 0):
            state[key] = item
        print json.dumps(item)
        dump_state(state.values())

if __name__ == '__main__':
    main()
