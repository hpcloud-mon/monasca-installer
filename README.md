monasca-installer
=================

Installs monasca using ansible.

# Installation

## Get the Code

```
git clone https://github.com/hpcloud-mon/monasca-installer
```

## Install ansible and download the monasca roles
#### Linux (Ubuntu)
```
sudo pip install ansible  (using ansible version >= 1.8)
cd monasca_installer/monasca_installer
ansible-galaxy install -r ../requirements.yml -p ./roles -f
```

# Using the installer

## Modify the monasca_config.yml


## Run build-ansible-files.py 
```
cd monasca_installer
cp monasca_config.yaml.example monasca_config.yml
python build-ansible-files.py monasca_config.yml
```

## Run the ansible site playbook
To set everything up simply run `ansible-playbook -i hosts site.yml`. Of course individual plays, tags and
limiting can be used to run just portions. In particular limiting to just a single cluster will be common.
See the name of the plays for a description on what they cover and refer to docs.ansible.com for additional details.

# Vagrant Environment
A vagrant file is setup that will build up 1 devstack box and 3 boxes for monasca. The installer can then be run against these machines. The ips of
the machines are:
  - devstack - 192.168.10.5
  - monasca1 - 192.168.10.6
  - monasca2 - 192.168.10.7
  - monasca3 - 192.168.10.8

Simple run `vagrant up` to start the vms.

Use the vagrant_config.yml, and run the playbook
python build-ansible-files.py vagrant_config.yml
