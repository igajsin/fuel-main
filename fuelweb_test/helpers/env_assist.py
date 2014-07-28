#    Copyright 2013 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

# TODO
# возможно имеет смысл засунуть url для libvirt в json
# а url для ssh брать из него же
# восстановление сетей libvirt кажется не нужно
# если не пригодится, удалю из кода

import libvirt
import json
import os


def set_env(ip):
    "export POOL_PUBLIC=‘172.16.0.0/24:24’"
    os.environ['POOL_PUBLIC'] = ip


def restore_snpsht(conn, domain, snapname):
    """restore domain from snapshot snapname"""
    d = conn.lookupByName(domain)
    s = d.snapshotLookupByName(snapname)
    d.revertToSnapshot(s)


def start_net(conn, name):
    "start predefined network"
    print "start_net: conn is {} and name is {}".format(conn, name)
    if not name == "":
        net = conn.networkLookupByName(name)
        if not net.isActive():
            net.create()


def build_iface(url, br, iface, ip, vlan):
    os.system("ssh {} sudo vconfig rem {}.{}".format(url, iface, vlan))
    os.system("ssh {} sudo vconfig add {} {}".format(url, iface, vlan))
    os.system("ssh {} sudo ip l set {} down".format(url, br))
    os.system("ssh {} sudo brctl delbr {}".format(url, br))
    os.system("ssh {} sudo brctl addbr {}".format(url, br))
    os.system("ssh {} sudo brctl addif {} {}.{}".format(url, br, iface, vlan))
    os.system("ssh {} sudo ip a a {} dev {}".format(url, ip, br))


def restore_env(name, fl):
    return json.load(open(fl, "r"))[name]


def restore(conn, env):
    """Get list of domains and snapshots of them
    restore domains to shanpshots, also start networks
    """
    if len(env['networks']) > 0:
        for n in env['networks']:
            start_net(conn, n['network'])
            build_iface(n['host'], n['bridge'], n['iface'], n['ip'], n['vlan'])
    if len(env['snapshots']) > 0:
        for d, s in env['snapshots']:
            restore_snpsht(conn, d, s)


def connect(url):
    "Connect to libvirt"
    try:
        c = libvirt.open(url)
    except:
        print 'Failed to connect to {}'.format(url)
        return None
    return c


def make_env(name, url="qemu:///system", fl="env.json"):
    "Restore envronment name, described in fl"
    conn = connect(url)
    wrk = restore_env(name, fl)
    restore(conn, wrk)
    return 0
