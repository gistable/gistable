from rx import Observable, Observer
from collections import defaultdict

users = [
    { "id" : 0, "name" : "Hero" },
    { "id" : 1, "name" : "Dunn" },
    { "id" : 2, "name" : "Sue" },
    { "id" : 3, "name" : "Chi" },
    { "id" : 4, "name" : "Thor" },
    { "id" : 5, "name" : "Clive" },
    { "id" : 6, "name" : "Hicks" },
    { "id" : 7, "name" : "Devin" },
    { "id" : 8, "name" : "Kate" },
    { "id" : 9, "name" : "Klein" },
]

friendships = [
    (0,1),
    (0,2),
    (1,2),
    (1,3),
    (2,3),
    (3,4),
    (4,5),
    (5,6),
    (5,7),
    (6,8),
    (7,8),
    (8,9)
]

interests = [
(0, "Hadoop"), (0, "Big Data"), (0, "HBase"), (0, "Java"),
(0, "Spark"), (0, "Storm"), (0, "Cassandra"),
(1, "NoSQL"), (1, "MongoDB"), (1, "Cassandra"), (1, "HBase"),
(1, "Postgres"), (2, "Python"), (2, "scikit-learn"), (2, "scipy"),
(2, "numpy"), (2, "statsmodels"), (2, "pandas"), (3, "R"), (3, "Python"),
(3, "statistics"), (3, "regression"), (3, "probability"),
(4, "machine learning"), (4, "regression"), (4, "decision trees"),
(4, "libsvm"), (5, "Python"), (5, "R"), (5, "Java"), (5, "C++"),
(5, "Haskell"), (5, "programming languages"), (6, "statistics"),
(6, "probability"), (6, "mathematics"), (6, "theory"),
(7, "machine learning"), (7, "scikit-learn"), (7, "Mahout"),
(7, "neural networks"), (8, "neural networks"), (8, "deep learning"),
(8, "Big Data"), (8, "artificial intelligence"), (9, "Hadoop"),
(9, "Java"), (9, "MapReduce"), (9, "Big Data")
]

class SimplePrint(Observer):
    def on_next(self,t):
        print(t)
    def on_completed(self):
        print("")
    def on_error(self,e):
        print(e)

# returns an Observable emitting friends of a given user
def get_friends(user):
    return Observable.from_(friendships) \
        .filter(lambda friendship: friendship[0] == user["id"] or friendship[1] == user["id"]) \
        .flat_map(lambda friendship: Observable.from_(friendship)) \
        .filter(lambda user_id: user_id != user["id"]) \
        .flat_map(lambda friend_id: Observable.from_(users).filter(lambda user: user["id"] == friend_id))


# emit friends for "Chi"
print("Friends of \"Chi\"")
get_friends(users[3]).subscribe(SimplePrint())

# get a count of each user's friends, and order by reverse rank
print("\r\nUsers and friend counts, sorted descending")

Observable.from_(users) \
    .flat_map(lambda user: get_friends(user).count().map(lambda ct: (user["name"], ct))) \
    .to_list() \
    .map(lambda list: sorted(list,key=lambda t: t[1],reverse=True)) \
    .flat_map(lambda list: Observable.from_(list)) \
    .subscribe(SimplePrint())


# get mutual friend for Hero and Sue
print("\r\nMutual friends of Hero and Sue")

def get_mutual_friends(user, other_user):
    return get_friends(other_user) \
        .filter(lambda foaf: foaf["id"] != user["id"]) \
        .flat_map(lambda foaf: get_friends(user)
                  .filter(lambda user_friend: user_friend["id"] == foaf["id"]).count()
                  .filter(lambda ct: ct > 0).map(lambda b: foaf)
        )

hero = users[0]
chi = users[3]

get_mutual_friends(hero,chi).subscribe(SimplePrint())

# rank friends of Chi by mutual friend count
print("\r\nRanked friends of Chi by mutual friend count")

get_friends(chi) \
    .flat_map(lambda friend: get_mutual_friends(chi,friend).count().map(lambda ct: (friend["name"], ct))) \
    .to_list() \
    .map(lambda list: sorted(list,key=lambda t: t[1],reverse=True)) \
    .flat_map(lambda list: Observable.from_(list)) \
    .subscribe(SimplePrint())

# finding common interests
def data_scientists_who_like(target_interest):
    return Observable.from_(interests) \
        .filter(lambda applied_interest: applied_interest[1] == target_interest) \
        .map(lambda applied_interest: applied_interest[0])  \
        .flat_map(lambda user_id: Observable.from_(users).filter(lambda user: user["id"] == user_id))

def interests_for_data_scientist(user):
    return Observable.from_(interests) \
        .filter(lambda applied_interest: applied_interest[0] == user["id"]) \
        .map(lambda applied_interest: applied_interest[1])

def common_interests_between(user, other_user):
    return interests_for_data_scientist(user) \
            .flat_map(lambda interest: interests_for_data_scientist(other_user)
                      .filter(lambda other_interest: interest == other_interest)
            )

def common_interest_count(user):
    return Observable.from_(users) \
            .filter(lambda other_user: other_user["id"] != user["id"]) \
            .flat_map(lambda other_user: common_interests_between(user,other_user).
                      count()
                      .map(lambda ct: (other_user["name"],ct))
            ).to_list() \
            .map(lambda list: sorted(list, key=lambda t: t[1], reverse=True)) \
            .flat_map(lambda list: Observable.from_(list))

print("\r\nCommon interest counts for Chi")
common_interest_count(users[3]).subscribe(SimplePrint())


# Salary and Tenure

print("\r\nAverage salary by tenure range")

salaries_and_tenures = [(83000,8.7),(88000,8.1),
                        (48000, 0.7), (76000, 6),
                        (69000,6.5), (76000,7.5),
                        (60000,2.5), (83000,10),
                        (48000,1.9), (63000,4.2)]

tenure_buckets = [(0,1.9),(2,5),(5.1,50)]

class SalaryTenureBucket:
    def __init__(self, salary, tenure, bucket):
        self.salary = salary
        self.tenure = tenure
        self.bucket = bucket


def get_bucket(tenure):
    return Observable.from_(tenure_buckets).filter(lambda tb: tb[0] <= tenure and tenure <= tb[1])



def average_salary_by_tenure():
    return Observable.from_(salaries_and_tenures) \
        .flat_map(lambda st: get_bucket(st[1]).map(lambda b: SalaryTenureBucket(st[0],st[1],b))) \
        .group_by(lambda stb: stb.bucket) \
        .flat_map(lambda grp: grp.average(lambda stb: stb.salary)
                         .map(lambda salary: (grp.key, salary)) \
        ).subscribe(SimplePrint())

average_salary_by_tenure()

## Words and Counts
print("\r\nInterest occurrence count")

def words_and_counts():
    return Observable.from_(interests) \
        .flat_map(lambda interest: Observable.from_(interest[1].lower().split())) \
        .group_by(lambda s: s) \
        .flat_map(lambda grp: grp.count().map(lambda ct: (grp.key,ct))) \
        .to_list().map(lambda list: sorted(list,key=lambda t: t[1],reverse=True)).flat_map(lambda list: Observable.from_(list)) \
        .subscribe(SimplePrint())

words_and_counts()

# Friends of "Chi"
# {'id': 1, 'name': 'Dunn'}
# {'id': 2, 'name': 'Sue'}
# {'id': 4, 'name': 'Thor'}
#
#
# Users and friend counts, sorted descending
# ('Dunn', 3)
# ('Sue', 3)
# ('Chi', 3)
# ('Clive', 3)
# ('Kate', 3)
# ('Hero', 2)
# ('Thor', 2)
# ('Hicks', 2)
# ('Devin', 2)
# ('Klein', 1)
#
#
# Mutual friends of Hero and Sue
# {'id': 1, 'name': 'Dunn'}
# {'id': 2, 'name': 'Sue'}
#
#
# Ranked friends of Chi by mutual friend count
# ('Dunn', 1)
# ('Sue', 1)
# ('Thor', 0)
#
#
# Common interest counts for Chi
# ('Clive', 2)
# ('Hicks', 2)
# ('Sue', 1)
# ('Thor', 1)
# ('Hero', 0)
# ('Dunn', 0)
# ('Devin', 0)
# ('Kate', 0)
# ('Klein', 0)
#
#
# Average salary by tenure range
# ((5.1, 50), 79166.66666666667)
# ((0, 1.9), 48000.0)
# ((2, 5), 61500.0)
#
#
# Interest occurrence count
# ('big', 3)
# ('data', 3)
# ('java', 3)
# ('python', 3)
# ('learning', 3)
# ('hadoop', 2)
# ('hbase', 2)
# ('cassandra', 2)
# ('scikit-learn', 2)
# ('r', 2)
# ('statistics', 2)
# ('regression', 2)
# ('probability', 2)
# ('machine', 2)
# ('neural', 2)
# ('networks', 2)
# ('spark', 1)
# ('storm', 1)
# ('nosql', 1)
# ('mongodb', 1)
# ('postgres', 1)
# ('scipy', 1)
# ('numpy', 1)
# ('statsmodels', 1)
# ('pandas', 1)
# ('decision', 1)
# ('trees', 1)
# ('libsvm', 1)
# ('c++', 1)
# ('haskell', 1)
# ('programming', 1)
# ('languages', 1)
# ('mathematics', 1)
# ('theory', 1)
# ('mahout', 1)
# ('deep', 1)
# ('artificial', 1)
# ('intelligence', 1)
# ('mapreduce', 1)