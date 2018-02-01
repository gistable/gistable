'''A python script to export the raw data from mailchimp lists and campaigns. 
The output of this script will be a CSV file with the open and click rates for each campaign 
and each list member (identified by an email.) You can use this data for further analysis 
as seen here:

http://www.silota.com/docs/recipes/sql-email-customer-list-segmentation-lead-scoring.html

Written by Ganesh, 2017. 
'''

import requests

API_KEY = "MAILCHIMP_API_KEY"

LISTS = ["LIST_ID"]

session = requests.Session()
session.headers.update({"Authorization": "apikey %s" % API_KEY})


def quote(x):
    return '"%s"' % x


def get_campaigns():
    '''Return an enriched data structure of all campaigns in this account'''
    r = session.get("https://us7.api.mailchimp.com/3.0/campaigns/")

    fields = ["id", "send_time", "emails_sent"]
    ret = []

    print ",".join(fields), ", title"
    for c in r.json()["campaigns"]:
        print ",".join([str(c[x]) for x in fields]), ",", quote(c["settings"]["subject_line"])
        ret.append((c["id"], c["send_time"], c["emails_sent"],
                    c["settings"]["subject_line"]))

    return ret


def click_reports():
    campaigns = get_campaigns()

    print "id, campaign_id, sent_time, subject, email, open_count, click_count"
    for c in campaigns:
        n, offset = 0, 0

        while True:
            r = session.get(
                "https://us7.api.mailchimp.com/3.0/reports/%s/email-activity/?fields=emails.campaign_id,emails.email_address,emails.activity&count=100&offset=%d" % (c[0], offset))

            for e in r.json()["emails"]:
                open_count, click_count = 0, 0
                for a in e["activity"]:
                    if a["action"] == "open":
                        open_count += 1
                    elif a["action"] == "click":
                        click_count += 1

                print ",".join("%s" % x for x in [n, e["campaign_id"], quote(c[1]), quote(c[3]), e["email_address"], open_count, click_count])
                n += 1

            if n < (offset + 100 - 1):
                break

            offset += 100

click_reports()
