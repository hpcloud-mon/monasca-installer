# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2" # Vagrantfile API/syntax version. Don't touch unless you know what you're doing!

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  if Vagrant.has_plugin?("vagrant-cachier")
    config.cache.scope = :box
  end

  # Handle local proxy settings
  if Vagrant.has_plugin?("vagrant-proxyconf")
    if ENV["http_proxy"]
      config.proxy.http = ENV["http_proxy"]
    end
    if ENV["https_proxy"]
      config.proxy.https = ENV["https_proxy"]
    end
    if ENV["no_proxy"]
      config.proxy.no_proxy = ENV["no_proxy"]
    end
  end

  config.vm.synced_folder "~/", "/vagrant_home"

  # One vm just for devstack (to access the UI)
  config.vm.define "devstack" do |ds|
    ds.vm.hostname = "devstack"
    ds.vm.box = "monasca/devstack"
    ds.vm.network :private_network, ip: "192.168.10.5"
    ds.vm.provider "virtualbox" do |vb|
      vb.memory = 4096
      vb.cpus = 4
    end
  end

  # Vms for monasca
  config.vm.define "monasca1" do |mm|
    mm.vm.hostname = 'monasca1'
    mm.vm.box = "ubuntu/trusty64"
    mm.vm.network :private_network, ip: "192.168.10.6"
    mm.vm.provider "virtualbox" do |vb|
      vb.memory = 6144 
      vb.cpus = 4
    end
  end
  config.vm.define "monasca2" do |mm|
    mm.vm.hostname = 'monasca2'
    mm.vm.box = "ubuntu/trusty64"
    mm.vm.network :private_network, ip: "192.168.10.7"
    mm.vm.provider "virtualbox" do |vb|
      vb.memory = 6144 
      vb.cpus = 4
    end
  end
  config.vm.define "monasca3" do |mm|
    mm.vm.hostname = 'monasca3'
    mm.vm.box = "ubuntu/trusty64"
    mm.vm.network :private_network, ip: "192.168.10.8"
    mm.vm.provider "virtualbox" do |vb|
      vb.memory = 6144 
      vb.cpus = 4
    end
  end

end
