monasca-installer
=================

Installs monasca using ansible.  Uses a simple config template to generate ansible inventory.

# Installation

## Get the Code

```
git clone https://github.com/hpcloud-mon/monasca-installer
```

## Install ansible and download the monasca roles
#### Linux (Ubuntu)
```
sudo pip install ansible  (using ansible version >= 1.8)
cd monasca-installer/monasca_installer
ansible-galaxy install -r ../requirements.yml -p ./roles -f
```

# Using the installer

## Modify the monasca_config.yml


## Run build-ansible-files.py 
```
cd monasca_installer
cp monasca_config.yml.example monasca_config.yml
python build-ansible-files.py monasca_config.yml
```

## Run the ansible site playbook
```
ansible-playbook -i ./hosts site.yml
```

extras
======

## Optional ansible alarm configuration

Modify alarms.yml monasca_notification_method.address:
monasca_notification_method:
        name: "Email Root"
        type: 'EMAIL'
        address: 'root@localhost'

Run alarms.yml playbook:
```
ansible-playbook -i ./hosts alarms.yml
```

# Vagrant Environment
A vagrant file is setup that will build up 1 devstack box and 3 boxes for monasca. The installer can then be run against these machines. The ips of
the machines are:
  - devstack - 192.168.10.5
  - monasca1 - 192.168.10.6
  - monasca2 - 192.168.10.7
  - monasca3 - 192.168.10.8

The vagrant install of 1 devstack and 3 monasca servers takes about 24G memory.  To install with 1 devstack and 1 monasca server takes 16G memory.

Simply run `vagrant up` to start the vms.

Use the vagrant_config.yml, and run the playbook
python build-ansible-files.py vagrant_config.yml
