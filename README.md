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
cd monasca_installer
ansible-galaxy install -r requirements.yml -p ./roles -f
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
