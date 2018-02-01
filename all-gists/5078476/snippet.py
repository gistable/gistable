import os
import MySQLdb as mysql
from jinja2 import Template
import unicodecsv as csv

conn = mysql.connect("s1-analytics-slave.eqiad.wmnet", "research", os.environ["RESEARCH_PASSWORD"], "log")

def execute(sql):
    cur = conn.cursor()
    cur.execute(sql)
    return cur


def render(template, env):
    t = Template(template)
    return t.render(**env)

sql_env = {
        "tables": {
            "upload_attempts": "MobileAppUploadAttempts_5257716",
            "login_attempts": "MobileAppLoginAttempts_5257721",
            "upload_web": "MobileWebUploads_5281063"
            },
        "intervals": {
            "running_average": "7 DAY"
            }
        }

graphs = {
        "error-uploads": {
            "title": "Error Uploads",
            "headers": [ "Date", "Total Uploads", "iOS Uploads", "iOS Uploads", "Camera", "Gallery", "External", "Camera (iOS)", "Gallery (iOS)", "External (iOS)", "Camera (iOS)", "Gallery (iOS)", "External (iOS)"],
            "sql": """SELECT    DATE(timestamp),
                                COUNT( * ),

                                SUM( IF( event_platform LIKE 'Android%', 1, 0) ) AS "Android",
                                SUM( IF( event_platform LIKE 'iOS%', 1, 0) ) AS "iOS",

                                SUM( IF( event_source = 'camera', 1, 0 ) ) as 'Camera',
                                SUM( IF( event_source = 'gallery', 1, 0 ) ) as 'Gallery',
                                SUM( IF( event_source = 'external', 1, 0 ) ) as 'External',

                                SUM( IF( event_source = 'camera' AND event_platform LIKE 'Android%', 1, 0 ) ) as 'Camera (Android)',
                                SUM( IF( event_source = 'gallery' AND event_platform LIKE 'Android%', 1, 0 ) ) as 'Gallery (Android)',
                                SUM( IF( event_source = 'external' AND event_platform LIKE 'Android%', 1, 0 ) ) as 'External (Android)',

                                SUM( IF( event_source = 'camera' AND event_platform LIKE 'iOS%', 1, 0 ) ) as 'Camera (iOS)',
                                SUM( IF( event_source = 'gallery' AND event_platform LIKE 'iOS%', 1, 0 ) ) as 'Gallery (iOS)',
                                SUM( IF( event_source = 'external' AND event_platform LIKE 'iOS%', 1, 0 ) ) as 'External (iOS)'

                      FROM      {{ tables.upload_attempts }}
                      WHERE     event_result != 'cancelled' AND
                                event_result != 'success' AND
                                wiki = 'commonswiki'
                      GROUP BY  DATE(timestamp)
                      """
                      },
        "cancelled-uploads": {
            "title": "Cancelled Logins",
            "headers": [ "Date", "Total Uploads", "iOS Uploads", "iOS Uploads", "Camera", "Gallery", "External", "Camera (iOS)", "Gallery (iOS)", "External (iOS)", "Camera (iOS)", "Gallery (iOS)", "External (iOS)"],
            "sql": """SELECT    DATE(timestamp),
                                COUNT( * ),

                                SUM( IF( event_platform LIKE 'Android%', 1, 0) ) AS "Android",
                                SUM( IF( event_platform LIKE 'iOS%', 1, 0) ) AS "iOS",

                                SUM( IF( event_source = 'camera', 1, 0 ) ) as 'Camera',
                                SUM( IF( event_source = 'gallery', 1, 0 ) ) as 'Gallery',
                                SUM( IF( event_source = 'external', 1, 0 ) ) as 'External',

                                SUM( IF( event_source = 'camera' AND event_platform LIKE 'Android%', 1, 0 ) ) as 'Camera (Android)',
                                SUM( IF( event_source = 'gallery' AND event_platform LIKE 'Android%', 1, 0 ) ) as 'Gallery (Android)',
                                SUM( IF( event_source = 'external' AND event_platform LIKE 'Android%', 1, 0 ) ) as 'External (Android)',

                                SUM( IF( event_source = 'camera' AND event_platform LIKE 'iOS%', 1, 0 ) ) as 'Camera (iOS)',
                                SUM( IF( event_source = 'gallery' AND event_platform LIKE 'iOS%', 1, 0 ) ) as 'Gallery (iOS)',
                                SUM( IF( event_source = 'external' AND event_platform LIKE 'iOS%', 1, 0 ) ) as 'External (iOS)'

                      FROM      {{ tables.upload_attempts }}
                      WHERE     event_result = 'cancelled' AND
                                wiki = 'commonswiki'
                      GROUP BY  DATE(timestamp)
                      """
                      },
        "successful-uploads": {
            "title": "Successful Logins",
            "headers": [ "Date", "Total Uploads", "iOS Uploads", "iOS Uploads", "Camera", "Gallery", "External", "Camera (iOS)", "Gallery (iOS)", "External (iOS)", "Camera (iOS)", "Gallery (iOS)", "External (iOS)"],
            "sql": """SELECT    DATE(timestamp),
                                COUNT( * ),

                                SUM( IF( event_platform LIKE 'Android%', 1, 0) ) AS "Android",
                                SUM( IF( event_platform LIKE 'iOS%', 1, 0) ) AS "iOS",

                                SUM( IF( event_source = 'camera', 1, 0 ) ) as 'Camera',
                                SUM( IF( event_source = 'gallery', 1, 0 ) ) as 'Gallery',
                                SUM( IF( event_source = 'external', 1, 0 ) ) as 'External',

                                SUM( IF( event_source = 'camera' AND event_platform LIKE 'Android%', 1, 0 ) ) as 'Camera (Android)',
                                SUM( IF( event_source = 'gallery' AND event_platform LIKE 'Android%', 1, 0 ) ) as 'Gallery (Android)',
                                SUM( IF( event_source = 'external' AND event_platform LIKE 'Android%', 1, 0 ) ) as 'External (Android)',

                                SUM( IF( event_source = 'camera' AND event_platform LIKE 'iOS%', 1, 0 ) ) as 'Camera (iOS)',
                                SUM( IF( event_source = 'gallery' AND event_platform LIKE 'iOS%', 1, 0 ) ) as 'Gallery (iOS)',
                                SUM( IF( event_source = 'external' AND event_platform LIKE 'iOS%', 1, 0 ) ) as 'External (iOS)'

                      FROM      {{ tables.upload_attempts }}
                      WHERE     event_result = 'success' AND
                                wiki = 'commonswiki'
                      GROUP BY  DATE(timestamp)
                      """
                      },
        "unique-uploaders": {
            "title": "Unique uploaders",
            "headers": [ "Date", "Total Unique Uploaders", "Android Unique Uploaders", "iOS Unique Uploaders"],
            "sql": """SELECT    DATE(T1.timestamp),
                                (SELECT COUNT( DISTINCT T2.event_username ) 
                                    FROM {{ tables.upload_attempts }} AS T2
                                    WHERE   T2.timestamp < T1.timestamp AND
                                            (T2.timestamp + INTERVAL 0 DAY) > (T1.timestamp - INTERVAL {{ intervals.running_average }} )) AS total,
                                (SELECT COUNT( DISTINCT T2.event_username ) 
                                    FROM {{ tables.upload_attempts }} AS T2
                                    WHERE   T2.event_platform LIKE 'Android%' AND
                                            T2.timestamp < T1.timestamp AND
                                            (T2.timestamp + INTERVAL 0 DAY) > (T1.timestamp - INTERVAL {{ intervals.running_average }} )) AS android,
                                (SELECT COUNT( DISTINCT T2.event_username ) 
                                    FROM {{ tables.upload_attempts }} AS T2
                                    WHERE   T2.event_platform LIKE 'iOS%' AND
                                            T2.timestamp < T1.timestamp AND
                                            (T2.timestamp + INTERVAL 0 DAY) > (T1.timestamp - INTERVAL {{ intervals.running_average}} )) AS iOS
                      FROM      {{ tables.upload_attempts }} AS T1
                      WHERE     T1.event_result = 'success' AND
                                T1.wiki = 'commonswiki'
                      GROUP BY  DATE(T1.timestamp)
                      """
                      },
        "successful-logins": {
            "title": "Successful Logins",
            "headers": [ "Date", "Total Logins", "iOS Logins", "Android Logins"],
            "sql": """SELECT    DATE(timestamp),
                                COUNT( * ), 
                                SUM( IF( event_platform LIKE 'Android%', 1, 0) ) AS "Android",
                                SUM( IF( event_platform LIKE 'iOS%', 1, 0) ) AS "iOS"
                      FROM      {{ tables.login_attempts }}
                      WHERE     event_result = 'success' AND
                                wiki = 'commonswiki'
                      GROUP BY  DATE(timestamp)
                      """
                      }
        }


for key, value in graphs.items():
    title = value['title']
    sql = render(value['sql'], sql_env)
    rows = execute(sql)
    writer = csv.writer(open(key + ".csv", "w"))
    writer.writerow(value['headers'])
    for row in rows:
        writer.writerow(row)
