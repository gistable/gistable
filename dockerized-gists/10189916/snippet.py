import SoftLayer.API
from pprint import pprint as pp

apiUsername = 'set me'
apiKey = 'set me'

client = SoftLayer.Client(
    username=apiUsername,
    api_key=apiKey,
)

start_date = '03/01/2014'
end_date = '03/01/2014'

# Virtual Guest ID
server_id = 000

# Retrieve all SoftLayer_Monitoring_Agent objects associated with this server
monitoring_agents = client['Virtual_Guest'].getMonitoringAgents(id=server_id)

# Store the Cpu, Disk, and Memory Monitoring Agent as cpu_disk_mem_agent
for agent in monitoring_agents:
    if agent['name'] == 'Cpu, Disk, and Memory Monitoring Agent':
        cpu_disk_mem_agent = agent

# Retrieve a list of SoftLayer_Monitoring_Agent_Configuration_Value objects
mask = 'mask.definition.monitoringDataFlag'
configuration_values = client['Monitoring_Agent'].getConfigurationValues(
    mask=mask, id=cpu_disk_mem_agent['id'])

# Bulid a list of SoftLayer_Container_Metric_Data_Type objects
metric_data_types = []
for configuration_value in configuration_values:
    # We only need configuration_values that have a 'value' and
    # 'monitoringDataFlag' of True
    if configuration_value['value'] is False:
        continue

    if configuration_value['definition']['monitoringDataFlag'] is not True:
        continue

    types = client['Monitoring_Agent_Configuration_Value'].getMetricDataType(
        id=configuration_value['id'])
    metric_data_types.append(types)

# Retrieve & display the graph data points
data = client['Monitoring_Agent'].getGraphData(
    metric_data_types, start_date, end_date, id=cpu_disk_mem_agent['id'])
pp(data)