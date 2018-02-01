# -*- mode: ruby -*-
# vi: set ft=ruby :


Vagrant.configure('2') do |config|

  config.vm.box = 'ubuntu/xenial64'

  config.vm.provider :virtualbox do |vb|
    vb.customize [ 'modifyvm', :id, '--natdnshostresolver1', 'on' ]
  end

  config.vm.define :control do |machine|

    machine.vm.network 'private_network', ip: '192.168.33.10'
    machine.vm.synced_folder '.vagrant/machines/', '/ssh'

    machine.vm.provision :ansible do |ansible|

      ansible.compatibility_mode = '2.0'
      ansible.playbook = 'playbooks/configure-control-server.yml'
      ansible.extra_vars = {
          inventory_file_name: '../inventory.vagrant',
      }

    end

  end

  config.vm.define :nomad1 do |machine|

    machine.vm.network 'private_network', ip: '192.168.33.11'

  end

  config.vm.define :nomad2 do |machine|

    machine.vm.network 'private_network', ip: '192.168.33.12'

  end

  config.vm.define :nomad3 do |machine|

    machine.vm.network 'private_network', ip: '192.168.33.13'

  end

end
