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
    chars = string.ascii_letters + string.digits + '!@#$%^&*()'
    random.seed = (os.urandom(1024))
    return ''.join(random.choice(chars) for i in range(length))


class AnsibleConfigGen(object):
    '''Read a site config and use it to build Ansible host and group files'''

    def get_parser(self):
        parser = argparse.ArgumentParser(description='Generate Ansible files from a YAML config template')
        parser.add_argument('input_file', help='input config file (YAML)')
        return parser

    def main(self, argv):
        '''Read config input from the command line and build Ansible files'''
        parser = self.get_parser()
        (args) = parser.parse_args(argv)

        try:
            with open(args.input_file, 'r') as config_yaml:
                config = yaml.safe_load(config_yaml)
        except IOError as e:
            print("Unable to open file {}, {}".format(args.input_file, e))
            sys.exit(1)

        # Zero out hosts file
        self.save_hosts(initialize=True)

        # Write out 'all' group_vars
        self.save_global(config['global'])

        for cluster in config['clusters']:
            # Extract sections out of the cluster, to be written to other files
            cluster_hosts = cluster.pop('hosts')
            master_config = cluster.pop('master_config')
            workers_config = cluster.pop('workers_config')

            # Initialize the various required host list variables
            for key in ['kafka_hosts', 'zookeeper_hosts']:
                cluster[key] = ""
            cluster['zookeeper_servers'] = {}
            cluster['wsrep_cluster_hosts'] = []
            workers_config['influxdb']['seed_servers'] = []

            # Build required host lists out of cluster_hosts
            for host in cluster_hosts:
                # Append to lists
                cluster['kafka_hosts'] = "{},{}:{}".format(cluster['kafka_hosts'],
                                                           host['internal_ip'],
                                                           cluster['kafka_client_port'])
                cluster['zookeeper_hosts'] = "{},{}:{}".format(cluster['zookeeper_hosts'],
                                                               host['internal_ip'],
                                                               cluster['zookeeper_client_port'])

                cluster['zookeeper_servers'][host['internal_ip']] = host['kafka_id']
                cluster['wsrep_cluster_hosts'].append(host['internal_ip'])
                workers_config['influxdb']['seed_servers'].append(host['internal_ip'])

            # Remove leading commas in the text string lists
            for key in ['kafka_hosts', 'zookeeper_hosts']:
                cluster[key] = cluster[key].lstrip(',')

            # Use the first host for nimbus_host
            cluster['nimbus_host'] = cluster_hosts[0]['internal_ip']

            # Build clusters in group_vars/
            self.save_group(cluster, cluster['cluster_name'])
            self.save_group(master_config,
                            "{}_master".format(cluster['cluster_name']))
            self.save_group(workers_config,
                            "{}_workers".format(cluster['cluster_name']))

            # Build files in host_vars/
            for host in cluster_hosts:
                self.save_hostvar(host)

            # Write hosts to the 'hosts' file (per cluster), first is master
            self.save_hosts("{}_master".format(cluster['cluster_name']),
                            cluster_hosts[0]['hostname'])
            self.save_hosts("{}_workers".format(cluster['cluster_name']),
                            "\n".join(h['hostname'] for h in cluster_hosts[1:]))

            self.save_hosts("{}:children".format(cluster['cluster_name']),
                            "{0}_master\n{0}_workers".format(cluster['cluster_name']))

        # Continue building hosts file (general)
        cluster_names = [c['cluster_name'] for c in config['clusters']]
        self.save_hosts("monasca:children",
                        "\n".join(cluster_names))
        self.save_hosts("monasca_master:children",
                        "\n".join(["{}_master".format(n) for n in cluster_names]))
        self.save_hosts("monasca_workers:children",
                        "\n".join(["{}_workers".format(n) for n in cluster_names]))

    def write_yaml(self, filename, data):
        '''Create parent directory if needed, and write out YAML to a file'''
        # Create the parent directory
        try:
            os.mkdir(os.path.dirname(filename))
        except OSError as e:
            # Ignore errno 17, directory already exists
            if e.errno != 17:
                print("Error creating group_vars directory: {}".format(e))
                sys.exit(1)

        try:
            with open(filename, 'w') as output_file:
                yaml.safe_dump(data, output_file)
            return True
        except OSError as e:
            print("Error writing to {}: {}".format(filename, e))
            sys.exit(1)

    def save_global(self, global_section):
        '''Write the group_vars/all file'''

        destination = "group_vars/all"
        self.write_yaml(destination, global_section)

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

    def save_hosts(self, section=None, content=None, initialize=False):
        '''Append config options to the 'hosts' file, initializing if asked'''
        try:
            if initialize:
                open("hosts", 'w').close()
            elif section is not None and content is not None:
                with open("hosts", 'a') as hosts_file:
                    print("[{}]".format(section), file=hosts_file)
                    print("{}\n".format(content), file=hosts_file)
        except OSError as e:
            print("Error writing to {}: {}".format(filename, e))
            sys.exit(1)


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    try:
        if args is None:
            args = sys.argv[1:]

        AnsibleConfigGen().main(args)
    except Exception as e:
        print("Exception: {}".format(e))
    sys.exit(1)

if __name__ == "__main__":
    main()
