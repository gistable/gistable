import SoftLayer.API
from pprint import pprint as pp

apiUsername = ''
apiKey = ''

client = SoftLayer.Client(
    username=apiUsername,
    api_key=apiKey,
)

subject_id = 1181
assigned_user_id = 

new_ticket = {
    'subjectId': subject_id,
    'assignedUserId': assigned_user_id,
}

result = client['Ticket'].createStandardTicket(new_ticket, 'Testing ticket creation')

pp(result)