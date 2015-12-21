#!/usr/bin/env python
import re
import os
import glob
import json
import struct
import socket
from collections import defaultdict

scriptname = os.path.basename(__file__)

ip2int = lambda ipstr: struct.unpack('!I', socket.inet_aton(ipstr))[0]
int2ip = lambda n: socket.inet_ntoa(struct.pack('!I', n))

lo_used = []
for hosts in ['/etc/hosts',] + glob.glob('/etc/hosts.d/*'):
    with open(hosts) as f:
        lo_used += [ip2int(ip) for ip in re.findall(r'127\.[0-9]+(?:\.[0-9]+){2}', f.read())]

def new_lo(s):
    return s + 1 if s + 1 not in lo_used else new_lo(s + 1)
    
def make_script(json_file, scriptname):
    tunnels_json = json.load(open(json_file))
    tunnel_sh = '#!/usr/bin/env bash\n# AUTO GENERATED from %(scriptname)s (source: %(json_file)s)\n\n' % vars()
    hosts_append = '# GENERATED FROM %(scriptname)s (source: %(json_file)s)\n' % vars()

    if "opts" in tunnels_json.keys():
        tunnel_sh += 'ssh %(opts)s \\\n' % tunnels_json
    else:
        tunnel_sh += 'ssh -M -S %s.socket -fnNT \\\n' % ''.join(json_file.split('.')[:-1]).replace('/tunnels/', '/root/')
        
    if "identity_file" in tunnels_json:
        tunnel_sh += "\t-i %(identity_file)s \\\n" % tunnels_json

    hosts = defaultdict(list)
    ordered = []
    for tunnel in tunnels_json["tunnels"]:
        host, port = tunnel.split(':')
        hosts[host].append(port)
        if host not in ordered:
            ordered.append(host)

    seed = ip2int('127.0.0.1')
    for tunnel in ordered:
        seed = new_lo(seed)
        lo_used.append(seed)
        lo = int2ip(seed)
        for port in hosts[tunnel]:
            tunnel_sh += "\t-L %(lo)s:%(port)s:%(tunnel)s:%(port)s \\\n" % vars()
        hosts_append += "%(lo)s\t%(tunnel)s\n" % vars()

    tunnel_sh += '\t%(user)s@%(jump_gateway)s\n' % tunnels_json
        
    return tunnel_sh, hosts_append


# Do the work
for json_file in glob.glob("/tunnels/*.json"):
    script, hosts = make_script(json_file, scriptname)
    fname = os.path.splitext(os.path.basename(json_file))[0]
    with open('/tunnels/%s.sh' % fname, 'w') as f:
        f.write(script)
    with open('/etc/hosts.d/%s.hosts' % fname, 'w') as f:
        f.write(hosts)
