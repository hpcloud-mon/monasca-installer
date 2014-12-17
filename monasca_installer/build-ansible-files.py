#!/usr/bin/env python

# Copyright (c) 2014 Hewlett-Packard Development Company, L.P.
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
"""Configuration Processor for Monasca Ansible Installer"""

from __future__ import print_function

import argparse
import os
import random
import string
import sys
import yaml


def generate_password():
    '''Generate a reasonably randomized password'''
    length = 24
    chars = string.ascii_letters + string.digits + '-_.~'
    random.seed = (os.urandom(1024))
    return ''.join(random.choice(chars) for i in range(length))


class AnsibleConfigGen(object):
    '''Read a site config and use it to build Ansible host and group files'''

    def __init__(self, config_file):
        self.config_file = config_file

    def run(self):
        '''Read config input from the command line and build Ansible files'''

        try:
            with open(self.config_file, 'r') as config_yaml:
                config = yaml.safe_load(config_yaml)
        except IOError as e:
            print("Unable to open file {}, {}".format(self.config_file, e))
            return

        # Extract sections out of the config, to be written to other files
        hosts = config.pop('hosts')
        master_config = config.pop('master_config')
        workers_config = config.pop('workers_config')

        # Initialize the various required host list variables
        for key in ['kafka_hosts', 'zookeeper_hosts']:
            config[key] = ""
        config['zookeeper_servers'] = {}
        config['wsrep_cluster_hosts'] = []
        workers_config['influxdb']['seed_servers'] = []

        # Build required host lists out of 'hosts'
        for host in hosts:
            # Append to lists
            config['kafka_hosts'] = "{},{}:{}".format(config['kafka_hosts'],
                                                      host['internal_ip'],
                                                      config['kafka_client_port'])
            config['zookeeper_hosts'] = "{},{}:{}".format(config['zookeeper_hosts'],
                                                          host['internal_ip'],
                                                          config['zookeeper_client_port'])

            config['zookeeper_servers'][host['internal_ip']] = host['kafka_id']
            config['wsrep_cluster_hosts'].append(host['internal_ip'])
            workers_config['influxdb']['seed_servers'].append(host['internal_ip'])

        # Remove leading commas in the text string lists
        for key in ['kafka_hosts', 'zookeeper_hosts']:
            config[key] = config[key].lstrip(',')

        # Remove kafka_client_port and zookeeper_client_port; no longer needed
        for entry in ['kafka_client_port', 'zookeeper_client_port']:
            del config[entry]

        # Use the first host as nimbus_host
        config['nimbus_host'] = hosts[0]['internal_ip']

        # Build the files in group_vars/
        self.save_group(config, 'monasca')
        self.save_group(master_config, "monasca_master")
        self.save_group(workers_config, "monasca_workers")

        # Build the files in host_vars/
        for host in hosts:
            self.save_hostvar(host)

        # Write hosts to the 'hosts' file.  First host is the master.
        hosts_data = {}
        hosts_data['monasca_master'] = hosts[0]['hostname']
        hosts_data['monasca_workers'] = "\n".join(h['hostname']
                                                  for h in hosts[1:])
        hosts_data['monasca:children'] = "monasca_master\nmonasca_workers"
        self.save_hosts(hosts_data)

    def write_yaml(self, filename, data):
        '''Create parent directory if needed, and write out YAML to a file'''
        # Create the parent directory
        try:
            os.mkdir(os.path.dirname(filename))
        except OSError as e:
            # Ignore errno 17, directory already exists
            if e.errno != 17:
                print("Error creating group_vars directory: {}".format(e))

        try:
            with open(filename, 'w') as output_file:
                yaml.safe_dump(data, output_file)
            return True
        except OSError as e:
            print("Error writing to {}: {}".format(filename, e))

    def save_group(self, cluster, filename):
        '''Write each cluster file in group_vars/'''

        # Insert passwords where requested
        def insert_passwords(dictionary):
            '''Peruse the cluster recursively & generate passwords if needed'''

            for key, value in dictionary.iteritems():
                if isinstance(value, dict):
                    insert_passwords(value)
                else:
                    if value == "PLEASE-GENERATE":
                        dictionary[key] = generate_password()
        insert_passwords(cluster)

        destination = "group_vars/{}".format(filename)

        self.write_yaml(destination, cluster)

    def save_hostvar(self, host):
        '''Write each host file in host_vars/'''

        destination = "host_vars/{}".format(host['hostname'])
        self.write_yaml(destination, host)

    def save_hosts(self, hosts_data):
        '''Create the 'hosts' file'''
        try:
            with open("hosts", 'w') as hosts_file:
                for section in sorted(hosts_data.iterkeys(), reverse=True):
                    print("[{}]".format(section), file=hosts_file)
                    print("{}\n".format(hosts_data[section]), file=hosts_file)
        except OSError as e:
            print("Error writing to hosts: {}".format(e))


def main():
    try:
        parser = argparse.ArgumentParser(description='Generate Ansible files' +
                                                     ' from a YAML template')
        parser.add_argument('input_file', help='input config file (YAML)')
        (args) = parser.parse_args(sys.argv[1:])

        generator = AnsibleConfigGen(args.input_file)
        generator.run()
    except Exception as e:
        print("Exception: {}".format(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
