// Configure Digital Ocean provider
provider "digitalocean" {
  token = "${var.DIGITAL_OCEAN_TOKEN}"
}

// SSH Key
resource "digitalocean_ssh_key" "do_test_harness" {
  name = "${var.KEY_NAME}"
  public_key = "${file(var.PUBLIC_KEY)}"
}

// Configure control server
resource "digitalocean_droplet" "control_server" {
  name = "${var.CONTROL_SERVER_NAME}"
  image = "${var.DO_IMAGE_SLUG}"
  region = "${var.DO_REGION}"
  size = "${var.CONTROL_SERVER_SIZE}"
  ssh_keys = ["${digitalocean_ssh_key.do_test_harness.id}"]
}

// Configure Nomad server
resource "digitalocean_droplet" "nomad_server" {
  name = "${var.NOMAD_SERVER_NAME_PREFIX}1"
  image = "${var.DO_IMAGE_SLUG}"
  region = "${var.DO_REGION}"
  size = "${var.NOMAD_SERVER_SIZE}"
  ssh_keys = ["${digitalocean_ssh_key.do_test_harness.id}"]
  volume_ids = ["${digitalocean_volume.consul_data.id}"]
}

// Configure Nomad Clients
resource "digitalocean_droplet" "nomad_client" {
  count = 2
  name = "${var.NOMAD_SERVER_NAME_PREFIX}${count.index + 2}"
  image = "${var.DO_IMAGE_SLUG}"
  region = "${var.DO_REGION}"
  size = "${var.NOMAD_CLIENT_SIZE}"
  ssh_keys = ["${digitalocean_ssh_key.do_test_harness.id}"]
}


// Storage volume
resource "digitalocean_volume" "consul_data" {
  name = "${var.CONSUL_VOLUME_NAME}"
  region = "${var.DO_REGION}"
  size = "${var.CONSUL_VOLUME_SIZE}"
}


data "template_file" "inventory" {
  template = <<-EOF
${var.CONTROL_SERVER_NAME} ansible_user=${var.SSH_USERNAME} ansible_host=${digitalocean_droplet.control_server.ipv4_address} ansible_ssh_private_key_file=${var.PRIVATE_KEY}

[servers]
${var.NOMAD_SERVER_NAME_PREFIX}1 ansible_user=${var.SSH_USERNAME} ansible_host=${digitalocean_droplet.nomad_server.ipv4_address} ansible_ssh_private_key_file=${var.PRIVATE_KEY} nomad_node_role=server consul_node_role=bootstrap consul_client_address=${digitalocean_droplet.nomad_server.ipv4_address}

[clients]
${join("\n", formatlist("%s ansible_host=%s ansible_user=%s ansible_ssh_private_key_file=%s nomad_node_role=client consul_node_role=client consul_client_address=%s", digitalocean_droplet.nomad_client.*.name, digitalocean_droplet.nomad_client.*.ipv4_address, var.SSH_USERNAME, var.PRIVATE_KEY, digitalocean_droplet.nomad_client.*.ipv4_address))}

[nodes]
[nodes:children]
servers
clients

[nomad_instances]
[nomad_instances:children]
nodes

[consul_instances]
[consul_instances:children]
nodes
  EOF
}

resource "local_file" "inventory" {
  content = "${data.template_file.inventory.rendered}"
  filename = "${var.INVENTORY_FILE}"
}


resource "null_resource" "provision_control_server" {
  depends_on = ["local_file.inventory", "digitalocean_droplet.control_server"]
  provisioner "remote-exec" {
    // Forces local-exec to wait until ssh is available, otherwise Ansible may time out
    inline = ["ls"]
    connection {
      type = "ssh"
      user = "root"
      private_key = "${file(var.PRIVATE_KEY)}"
      host = "${digitalocean_droplet.control_server.ipv4_address}"
    }
  }
  provisioner "local-exec" {
    command = "ansible-playbook -i ${var.INVENTORY_FILE} playbooks/configure-control-server.yml"
  }
}

output "username" {
  value = "${var.SSH_USERNAME}"
}
output "volume-attach-location" {
  value = "/dev/disk/by-id/scsi-0DO_Volume_${digitalocean_volume.consul_data.name}"
}
output "control-ip" {
  value = "${digitalocean_droplet.control_server.ipv4_address}"
}
output "server-ip" {
  value = "${digitalocean_droplet.nomad_server.ipv4_address}"
}
output "client-ips" {
  value = "${join(", ", digitalocean_droplet.nomad_client.*.ipv4_address)}"
}