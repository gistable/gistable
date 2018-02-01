requests.post("https://api.mailgun.net/v2/DOMAIN/messages",
              auth=("api", "key-SECRET"),
              files={
                  "attachment[0]": ("FileName1.ext", open(FILE_PATH_1, 'rb')),
                  "attachment[1]": ("FileName2.ext", open(FILE_PATH_2, 'rb'))
              },
              data={"from": "FROM_EMAIL",
                    "to": [TO_EMAIL],
                    "subject": SUBJECT,
                    "html": HTML_CONTENT
              })