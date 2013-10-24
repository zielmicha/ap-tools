import paramiko
import os
import multiprocessing
import sys
import pipes

ips = [ '192.168.0.%d' % i for i in xrange(33, 38) ]
password = open(os.path.expanduser('~/.wappassword')).read().strip()

def do_cmd(ip):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.connect(ip, username='root', password=password)
    stdin, stdout, stderr = client.exec_command('sh -c %s 2>&1 </dev/null'
                                                % pipes.quote(
                                                    ' '.join(pipes.quote(n) for n in sys.argv[2:])))
    for line in stdout:
        sys.stdout.write('[%s] %s' % (ip, line))
    client.close()
    return ip

def do_ips(func):
    pool = multiprocessing.Pool(len(ips))

    for i, ip in enumerate(pool.imap_unordered(func, ips)):
        print '%d/%d' % (i + 1, len(ips)), ip

    pool.terminate()

def shift():
    del sys.argv[1:2]

new_ips = []

while sys.argv[1] == '--ip':
    shift()
    new_ips.append(sys.argv[1])
    shift()

if new_ips:
    ips = new_ips

if sys.argv[1] == '--exec':
    do_ips(do_cmd)
else:
    print 'bad command', sys.argv[1]
