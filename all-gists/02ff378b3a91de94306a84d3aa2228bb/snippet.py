import azure.mgmt.compute
import azure.mgmt.compute.models
import azure.mgmt.network
import azure.mgmt.network.models
import azure.mgmt.resource
import azure.mgmt.resource.resources.models
import azure.mgmt.storage
import azure.mgmt.storage.models
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource.resources import ResourceManagementClient, ResourceManagementClientConfiguration

BASE_NAME = 'armpytest1404'

GROUP_NAME = BASE_NAME
STORAGE_NAME = BASE_NAME
VIRTUAL_NETWORK_NAME = BASE_NAME
SUBNET_NAME = BASE_NAME
NETWORK_INTERFACE_NAME = BASE_NAME
VM_NAME = BASE_NAME
OS_DISK_NAME = BASE_NAME
PUBLIC_IP_NAME = BASE_NAME
COMPUTER_NAME = BASE_NAME
ADMIN_USERNAME='azureuser'
ADMIN_PASSWORD='P@ssw0rd'
REGION = 'northeurope'
IMAGE_PUBLISHER = 'Canonical'
IMAGE_OFFER = 'UbuntuServer'
IMAGE_SKU = '14.04.4-LTS'
IMAGE_VERSION = 'latest'

subscription_id = '252281c3-8a06-4af8-8f3f-d6af13e4fde3'

credentials = ServicePrincipalCredentials(
    client_id = 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
    secret = 'abcdefg',
    tenant = 'yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy'
)

compute_client = azure.mgmt.compute.ComputeManagementClient(
    azure.mgmt.compute.ComputeManagementClientConfiguration(
        credentials,
        subscription_id
    )
)

network_client = azure.mgmt.network.NetworkManagementClient(
    azure.mgmt.network.NetworkManagementClientConfiguration(
        credentials,
        subscription_id
    )
)

storage_client = azure.mgmt.storage.StorageManagementClient(
    azure.mgmt.storage.StorageManagementClientConfiguration(
        credentials,
        subscription_id
    )
)

resource_client = ResourceManagementClient(
    ResourceManagementClientConfiguration(
        credentials,
        subscription_id
    )
)


def create_network_interface(network_client, region, group_name, interface_name,
                             network_name, subnet_name, ip_name):

    result_vnet = network_client.virtual_networks.create_or_update(
        group_name,
        network_name,
        azure.mgmt.network.models.VirtualNetwork(
            location=region,
            address_space=azure.mgmt.network.models.AddressSpace(
                address_prefixes=[
                    '10.1.0.0/16',
                ],
            ),
            subnets=[
                azure.mgmt.network.models.Subnet(
                    name=subnet_name,
                    address_prefix='10.1.0.0/24',
                ),
            ],
        ),
    )

    result_vnet.wait()

    subnet = network_client.subnets.get(group_name, network_name, subnet_name)

    result_pubip = network_client.public_ip_addresses.create_or_update(
        group_name,
        ip_name,
        azure.mgmt.network.models.PublicIPAddress(
            location=region,
            public_ip_allocation_method=azure.mgmt.network.models.IPAllocationMethod.dynamic,
            idle_timeout_in_minutes=4,
        ),
    )

    result_pubip.wait()

    public_ip_address = network_client.public_ip_addresses.get(group_name, ip_name)
    public_ip_id = public_ip_address.id

    result_nic = network_client.network_interfaces.create_or_update(
        group_name,
        interface_name,
        azure.mgmt.network.models.NetworkInterface(
            name=interface_name,
            location=region,
            ip_configurations=[
                azure.mgmt.network.models.NetworkInterfaceIPConfiguration(
                    name='default',
                    private_ip_allocation_method=azure.mgmt.network.models.IPAllocationMethod.dynamic,
                    subnet=subnet,
                    public_ip_address=public_ip_address,
                ),
            ],
        ),
    )

    result_nic.wait()

    network_interface = network_client.network_interfaces.get(
        group_name,
        interface_name,
    )

    return network_interface.id

# 1. Create a resource group
result_rg = resource_client.resource_groups.create_or_update(
    GROUP_NAME,
    azure.mgmt.resource.resources.models.ResourceGroup(
        location=REGION,
    ),
)

# result_list_sizes = compute_client.virtual_machine_sizes.list(REGION)
#
# for i in result_list_sizes:
#     print(i)

# 2. Create a storage account
result_stor = storage_client.storage_accounts.create(
    GROUP_NAME,
    STORAGE_NAME,
    azure.mgmt.storage.models.StorageAccountCreateParameters(
        location=REGION,
        account_type=azure.mgmt.storage.models.AccountType.standard_lrs,
    ),
)
result_stor.wait() # async operation

# 3. Create the network interface using a helper function (defined below)
nic_id = create_network_interface(
    network_client,
    REGION,
    GROUP_NAME,
    NETWORK_INTERFACE_NAME,
    VIRTUAL_NETWORK_NAME,
    SUBNET_NAME,
    PUBLIC_IP_NAME,
)

# 4. Create the virtual machine
result = compute_client.virtual_machines.create_or_update(
    GROUP_NAME,
    VM_NAME,
    azure.mgmt.compute.models.VirtualMachine(
        location=REGION,
        name=VM_NAME,
        os_profile=azure.mgmt.compute.models.OSProfile(
            admin_username=ADMIN_USERNAME,
            admin_password=ADMIN_PASSWORD,
            computer_name=COMPUTER_NAME,
        ),
        hardware_profile=azure.mgmt.compute.models.HardwareProfile(
            vm_size=azure.mgmt.compute.models.VirtualMachineSizeTypes.standard_d1
        ),
        network_profile=azure.mgmt.compute.models.NetworkProfile(
            network_interfaces=[
                azure.mgmt.compute.models.NetworkInterfaceReference(
                    id=nic_id,
                ),
            ],
        ),
        storage_profile=azure.mgmt.compute.models.StorageProfile(
            os_disk=azure.mgmt.compute.models.OSDisk(
                caching=azure.mgmt.compute.models.CachingTypes.none,
                create_option=azure.mgmt.compute.models.DiskCreateOptionTypes.from_image,
                name=OS_DISK_NAME,
                vhd=azure.mgmt.compute.models.VirtualHardDisk(
                    uri='https://{0}.blob.core.windows.net/vhds/{1}.vhd'.format(
                        STORAGE_NAME,
                        OS_DISK_NAME,
                    ),
                ),
            ),
            image_reference=azure.mgmt.compute.models.ImageReference(
                publisher=IMAGE_PUBLISHER,
                offer=IMAGE_OFFER,
                sku=IMAGE_SKU,
                version=IMAGE_VERSION,
            ),
        ),
    ),
)

result.wait()

public_ip_address = network_client.public_ip_addresses.get(GROUP_NAME, PUBLIC_IP_NAME)
print('VM available at {}'.format(public_ip_address.ip_address))
