#!/usr/bin/env python
from mastodon import Mastodon

mastodon_url = "https://your.instance.com"
mastodon_bot_login = "your-bot@email.address"
mastodon_bot_password = "youR_B0t_P4ssw0rD"

m_client_id, m_client_secret = Mastodon.create_app(client_name="serverstatus", api_base_url=mastodon_url)
masto = Mastodon(client_id=m_client_id, client_secret=m_client_secret, api_base_url=mastodon_url)
access_token = masto.log_in(mastodon_bot_login, mastodon_bot_password)

print("client_id: " + m_client_id + "\nclient_secret: " + m_client_secret + "\naccess_token: " + access_token)
