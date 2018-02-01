import SoftLayer.API
from pprint import pprint as pp

apiUsername = ''
apiKey = ''

client = SoftLayer.Client(
    username=apiUsername,
    api_key=apiKey,
)

# Virtual Guest Id
guest_id = 123456

guest = client['Virtual_Guest'].getObject(id=guest_id, mask="mask.monitoringUserNotification")

notification_id = guest['monitoringUserNotification'][0]['id']

# Create a list of SoftLayer_User_Customer_Notification_Virtual_Guest objects
# Only the id property is required
objects = [
    {'id': notification_id}
]

# deleteObjects will return a bool
result = client['User_Customer_Notification_Virtual_Guest'].deleteObjects(objects)

pp(result)