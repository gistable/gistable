from locust import HttpLocust, TaskSet, task

class MostBasicLoadTest(TaskSet):
    def on_start(self):
        """ on_start is called when a Locust start before any task is scheduled """
        self.login()

    def login(self):
        self.client.post("/api/api-token-auth/",
            {
                "username":"your_username",
                "password":"your_password"
            })

    @task(2)
    def index(self):
        self.client.get("/")

    @task(1)
    def profile(self):
        self.client.get("/about")


class TemplateLoadTest(TaskSet):

    @task(5)
    def preview_template(self):
        response = self.client.request(method="POST",
            url="/api/preview-template/",
            headers={
                "Authorization": 'Token 182bc14esdf334438ec02d8b192a89d37267d4bfc'
            },
            files={
                "user_photo": open("logo.png", 'r'),
            },
            data={
                "template_choice": "blank"
            })
        print "Preview; Response status code:", response.status_code

    @task(1)
    def create_tempalte(self):
        response = self.client.request(method="POST",
            url="/api/create-template/",
            headers={
                "Authorization": 'Token 182bc14e571b4438ec02d8b192a454ddd7267d4bfc'
            },
            files={
                "user_photo": open("logo.png", 'r'),
            },
            data={
                "email": "example@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "template_text": "Locust Test",
                "quantity": 3,
                "street_address": "123 Fake Street",
                "state": "NY",
                "city": "New York",
                "zip_code": 10001,
                "international_shipping": True,
            })
        print "Create; Response status code:", response.status_code
        print "Create; Response content:", response.content

class WebsiteUser(HttpLocust):
    host = 'http://www.example.com'
    task_set = TemplateLoadTest
    min_wait = 5000
    max_wait = 9000