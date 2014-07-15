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

import libvirt
import json


def restore_snpsht(conn, domain, snapname):
    """restore domain from snapshot snapname"""
    d = conn.lookupByName(domain)
    s = d.snapshotLookupByName(snapname)
    d.revertToSnapshot(s)


def restore_env(name, fl):
    return json.load(open(fl, "r"))[name]


def restore(conn, env):
    """Get list of domains and snapshots of them
    restore domains to shanpshots
    """
    for d, s in env:
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
