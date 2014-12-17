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
sudo pip install ansible  (using version 1.7.2)
cd monasca_installer
ansible-galaxy install -r ansible_roles -p ./roles -f
```

# Using the installer

## Modify the monasca_config.yml


## Run the installer 
build-ansible-files.py monasca_config.yml
