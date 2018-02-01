def webhook():
  json_str = request.josn
  json_obj = json.loads(json_str)
  new_message = types.Message.de_json(json_obj['message'])
  telebot.process_new_messages([new_messages])  # process_new_messages need message array