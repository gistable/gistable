class User(db.Model):
  location      = db.StringProperty()
  timezone      = db.StringProperty(default='America/Los_Angeles')

  # Do this once per user
  def calculate_timezone(self):
    from simplegeo import Client
    client = Client('oauth key', 'oauth secret SHH')
    response = client.context.get_context_by_address(self.location)
    for feature in response['features']:
      if feature['classifiers'][0]['category'] == 'Time Zone':
        timezone = feature['name']
    self.timezone = timezone
    self.put()