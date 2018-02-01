import requests
import json 

# assumes RobotReviewer running locally on port 5000
url = "http://127.0.0.1:5000/is_an_rct"
# toy example
citation_data = {'title': 'a randomized control trial', 'abstract': 'hello world'}
headers = {'content-type': 'application/json'}

payload = {'title': 'a randomized control trial', 'abstract': 'hello world'}
response = requests.post(url, data=json.dumps(payload), headers=headers)
print (response.json())
# something like: {'title': 'Is an RCT?', 'type': 'Trial Design', 'annotations': [], 'description': 'RCT (p=0.88)'}

# more realistic example (actual citation data)
title =    '''Does usage of a parachute in contrast to free fall prevent major trauma?: a prospective randomised-controlled trial in rag dolls.'''
abstract = '''PURPOSE: It is undisputed for more than 200 years that the use of a parachute prevents major trauma when falling from a great height. Nevertheless up to date no prospective randomised controlled trial has proven the superiority in preventing trauma when falling from a great height instead of a free fall. The aim of this prospective randomised controlled trial was to prove the effectiveness of a parachute when falling from great height. METHODS: In this prospective randomised-controlled trial a commercially acquirable rag doll was prepared for the purposes of the study design as in accordance to the Declaration of Helsinki, the participation of human beings in this trial was impossible. Twenty-five falls were performed with a parachute compatible to the height and weight of the doll. In the control group, another 25 falls were realised without a parachute. The main outcome measures were the rate of head injury; cervical, thoracic, lumbar, and pelvic fractures; and pneumothoraxes, hepatic, spleen, and bladder injuries in the control and parachute groups. An interdisciplinary team consisting of a specialised trauma surgeon, two neurosurgeons, and a coroner examined the rag doll for injuries. Additionally, whole-body computed tomography scans were performed to identify the injuries. RESULTS: All 50 falls-25 with the use of a parachute, 25 without a parachute-were successfully performed. Head injuries (right hemisphere p = 0.008, left hemisphere p = 0.004), cervical trauma (p < 0.001), thoracic trauma (p < 0.001), lumbar trauma (p < 0.001), pelvic trauma (p < 0.001), and hepatic, spleen, and bladder injures (p < 0.001) occurred more often in the control group. Only the pneumothoraxes showed no statistically significant difference between the control and parachute groups. CONCLUSIONS: A parachute is an effective tool to prevent major trauma when falling from a great height.'''
payload = {'title': title, 'abstract': abstract}
print(requests.post(url, data=json.dumps(payload), headers=headers).json())
# {'type': 'Trial Design', 'description': 'RCT (p=0.68)', 'annotations': [], 'title': 'Is an RCT?'}

# one more example (this time a negative case)
title = '''Morphology and size of stem cells from mouse and whale: observational study.'''
abstract = ''' OBJECTIVE: To compare the morphology and size of stem cells from two mammals of noticeably different body size. DESIGN: Observational study. SETTING: The Netherlands. PARTICIPANTS: A humpback whale (Megaptera novaeangliae) and a laboratory mouse (Mus musculus). MAIN OUTCOME MEASURES: Morphology and size of mesenchymal stem cells from adipose tissue. RESULTS: Morphologically, mesenchymal stem cells of the mouse and whale are indistinguishable. The average diameter of 50 mesenchymal stem cells from the mouse was 28 (SD 0.86) µm and 50 from the whale was 29 (SD 0.71) µm. The difference in cell size between the species was not statistically significant. Although the difference in bodyweight between the species is close to two million-fold, the mesenchymal stem cells of each were of similar size. CONCLUSIONS: The mesenchymal stem cells of whales and mice are alike, in both morphology and size.''' 
payload = {'title': title, 'abstract': abstract}
print(requests.post(url, data=json.dumps(payload), headers=headers).json())
# {'type': 'Trial Design', 'description': 'Not an RCT (p=0.20)', 'annotations': [], 'title': 'Is an RCT?'}
