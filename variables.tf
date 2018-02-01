variable "DIGITAL_OCEAN_TOKEN" {
  type = "string"
}
variable "KEY_NAME" {
  type = "string"
  default = "do-test-harness"
}
variable "PRIVATE_KEY" {
  type = "string"
  default = "playbooks/keys/do-test-harness"
}
variable "PUBLIC_KEY" {
  type = "string"
  default = "playbooks/keys/do-test-harness.pub"
}
variable "INVENTORY_FILE" {
  type = "string"
  default = "inventory.terraform"
}
variable "DO_IMAGE_SLUG" {
  type = "string"
  default = "ubuntu-16-04-x64"
}
variable "CONTROL_SERVER_NAME" {
  type = "string"
  default = "control"
}
variable "DO_REGION" {
  type = "string"
  default = "nyc1"
}
variable "CONTROL_SERVER_SIZE" {
  type = "string"
  default = "512mb"
}
variable "NOMAD_SERVER_NAME_PREFIX" {
  type = "string"
  default = "nomad"
}
variable "NOMAD_SERVER_SIZE" {
  type = "string"
  default = "2gb"
}
variable "NOMAD_CLIENT_SIZE" {
  type = "string"
  default = "2gb"
}
variable "CONSUL_VOLUME_NAME" {
  type = "string"
  default = "consul-data"
}
variable "CONSUL_VOLUME_SIZE" {
  type = "string"
  default = 50
}
variable "SSH_USERNAME" {
  type = "string"
  default = "root"
}