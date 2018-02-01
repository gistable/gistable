import docker
import json

def to_mounts_string(mounts):
    l = []
    for m in mounts:
        l.append('Type = {}, Source = {}, Target = {}'
        .format(m.get('Type'), m.get('Source'), m.get('Target')))

    return json.dumps(l, sort_keys=True, indent=4, ensure_ascii=False)

def to_networks_string(nets):
    l = []
    for n in nets:
        l.append('Target = {}'.format(n.get('Target','')))

    return json.dumps(l, sort_keys=True, indent=4, ensure_ascii=False)

def to_ports_string(ports):
    l = []
    for p in ports:
        l.append('TargetPort = {}, PublishedPort = {}, Protocol = {}, PublishMode = {}'
        .format(p.get('TargetPort'), p.get('PublishedPort'), p.get('Protocol'), p.get('PublishMode')))

    return json.dumps(l, sort_keys=True, indent=4, ensure_ascii=False)

client = docker.from_env()
service_list = client.services.list()

print("Services")
print("--------")

for v in service_list:
    name = v.name
    service_details = client.services.get(name)
    attrs = service_details.attrs
    spec = attrs.get('Spec')
    replicas = spec.get('Mode').get('Replicated', { 'Replicas': 'Global' }).get('Replicas')
    networks = spec.get('Networks')
    task = spec.get('TaskTemplate').get('ContainerSpec')
    image = task.get('Image') + '@' # Ignore sha256 digest
    env = task.get('Env', [])
    args = task.get('Args', [])
    mounts = task.get('Mounts', [])
    ports = spec.get('EndpointSpec').get('Ports', [])
    hostname = task.get('Hostname')

    print("Name : {}".format(name))
    print('- Replicas : {}'.format(replicas))
    print('- Image : {}'.format(image[0:image.index('@')]))
    print('- Env : {}'.format(', '.join(env)))
    print('- Args : {}'.format(' '.join(args)))
    print('- Mounts : {}'.format(to_mounts_string(mounts)))
    print('- Network : {}'.format(to_networks_string(networks)))
    print('- Ports : {}'.format(to_ports_string(ports)))
    print('- Hostname : {}'.format(hostname))
    print("\n")
