import mysql.connector
import datetime

# MySQL Connection Parameters

cnx = mysql.connector.connect(user='xxx', password='xxx',
                              host='xx',
                              database='xx')

# Querying for data

cursor = cnx.cursor()

select = "select id,date from xxx order by id"

cursor.execute(select)


all_dates_from_news = []
all_ids_from_news = []

# Making Python dictionary (collections) from retrieved ID and Date from database

for i in cursor:
    all_ids_from_news.append(i[0])
    value = datetime.datetime.fromtimestamp(float(i[1]))
    value = value.strftime('%Y-%m-%d %H:%M:%S')
    all_dates_from_news.append(value)


dict_from_select = dict(zip(all_ids_from_news, all_dates_from_news))


print "##################"

# Generating an incremental set of numbers from min(ID) to max(ID)

counter = 36306

all_ids = []
    
while counter < 90129:
    all_ids.append(counter)
    counter = counter + 1

print "########################"
    
# Finding those IDs that does not appear in database

excluded_ids = []
    
for i in all_ids:
    if i not in all_ids_from_news:
        excluded_ids.append(i)
        

print len(excluded_ids)
print "############################"

    
# #######################################################################################################

# Finding only those IDs which are incremente only by 1.

incremented_ids = []

for x ,y  in zip(excluded_ids, excluded_ids[1:]):
    #print x ,y
    if y-x==1:
       incremented_ids.append(x)
       incremented_ids.append(y)


incremented_ids_sorted = sorted(set(incremented_ids))



# ########################################################################################################

"""
Original Code from Adil Aliyev.
URL: https://www.facebook.com/adilek
"""
# Finding values incremented by 1 and creating from these values portions 

t = []

new_t = []
for i in range(0,len(incremented_ids_sorted)-1):
	p=(incremented_ids_sorted[i]-incremented_ids_sorted[i-1]==1)
	if p:
		t.append(incremented_ids_sorted[i])
	else:
		new_t.append(t)
		t = []
		t.append(incremented_ids_sorted[i])

# ########################################################################################################

new_list_from_ids  = []

# Finding those chunks of incremented values which lenght more than 5

for i in range(len(new_t)):
	if len(new_t[i]) > 5:
		#print new_t[i]
                new_list_from_ids.append(new_t[i])

# Finding the date of publishing of these values
for i in new_list_from_ids:
    print "Silinen melumat sayi? : " , len(i)
    #print min(i), max(i)
    x = min(i) - 1
    y = max(i) + 1
    print "Silinen melumatlarin daxil edilme tarix araliqlari: "
    print dict_from_select[x]
    print dict_from_select[y]


