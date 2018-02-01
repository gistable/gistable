# Gistable

## Command Line Usage

Gistable provides a NodeJS command line and can be installed globally using NPM and git.

```
npm i -g git+https://github.com/gistable/gistable.git
```

If Gistable has already been cloned, it can also be linked with

```
npm link
```

Display help with

```
gistable --help
```

## Running Inference Harness

Gistable includes Vagrant, Terraform, and Ansible configuration required for replicating gist inference. The list
of gists scraped is stored as a list in the YAML file `playbooks/vars/gists.yml`.

The provided Terraform configuration describes the resources needed to orchestrate the inference harness running in
DigitalOcean. A DigitalOcean authentication token is required. Public/Private keys named 
`playbooks/keys/do-test-harness(.pub)` must exist and are used to create the DigitalOcean ssh key. All IP addresses
are displayed as output after orchestration. To orchestrate with Terraform, run `terraform apply`. On the first run,
it is also necessary to run `terraform init`.

The provided Vagrant configuration orchestrates an inference harness locally using VirtualBox. To orchestrate using
Vagrant, run `vagrant up`. The machines have the following local IP addresses.

| Machine | IP Address |
| ------- | ---------- |
| Control | 192.168.33.10 |
| Nomad1 | 192.168.33.11 |
| Nomad2 | 192.168.33.12 |
| Nomad3 | 192.168.33.13 |

Orchestration requires Ansible to be present on the local system, and configures the following machines

| Machine | Description |
| ------- | ----------- |
| Control | A control machine with Ansible installed, used to manage Nomad machines. |
| Nomad1 | Nomad server used to schedule and manage jobs. |
| Nomad2 | Nomad client. |
| Nomad3 | Nomad client. |

Once orchestration is complete, ssh into the control machine and `cd ~/harness`. You will need to bootstrap the nomad 
cluster, install nomad, and schedule jobs using the following commands.

```
ansible-playbook -i inventory playbooks/bootstrap-cluster.yml
ansible-playbook -i inventory playbooks/install-nomad.yml
ansible-playbook -i inventory playbooks/run-gist-jobs.yml
```

Scheduling and running jobs takes approximately 8-10 hours. Once complete, gists and results can be scraped from the
inference harness using the provided script.

```
python2 scripts/scrape_consul_gists.py http://<nomad1 ip addr>:8500/
```

`scrape_consul_gists.py` generates three outputs. The first is a `gists/` directory containing all gists which either
succeeded on the first trial run, or failed due to `ImportError` on the first run but not the second. All gists of 
these gists have an accompanying Dockerfile for building and running them. `gists-other/` contains all gists which 
failed for any other reason. `gists.csv` is a csv file containing gist metatdata and inference execution results.

Finally, as a convenience, the Ansible playbook `playbooks/purge-nomad-jobs.yml` is provided to purge nomad job
execution if inference is to be rerun.
