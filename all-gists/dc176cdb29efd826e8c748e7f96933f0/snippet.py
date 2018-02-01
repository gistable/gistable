# -*- coding: UTF-8 -*-
import sys
from wit import Wit
from pyowm import OWM
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
import logging

DEFAULT_MAX_STEPS = 5
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

WIT_TOKEN = ''
OWM_API = ''
TELEGRAM_TOKEN = ''

class WitSystem():
    def __init__(self):
        self.owm = OWM(OWM_API, language='ru')
        actions = {
            'send': self.send,
            'getForecast': self.get_forecast,
            'getExtraForecast': self.get_extra_forecast,
            'clearStory': self.clear_story
        }
        self.client = Wit(access_token=WIT_TOKEN, actions=actions)
        self.contexts = {}
        self.context_answer = {}

    def first_entity_value(self, entities, entity):
        if entity not in entities:
            return None
        val = entities[entity][0]['value']
        if not val:
            return None
        return val['value'] if isinstance(val, dict) else val

    def send(self, request, response):
        print(response['text'].decode('utf-8'))
        logger.info('Info "%s" "%s" "%s"' % (response['text'].decode('utf-8'), str(request), str(response)))
        self.context_answer[request['session_id']] = response

    def recive(self, chat_id, message, max_steps=DEFAULT_MAX_STEPS):
        if chat_id not in self.contexts:
            self.contexts[chat_id] = {}
        self.contexts[chat_id] = self.client.run_actions(chat_id, message, self.contexts[chat_id], max_steps)
        return self.context_answer[chat_id]

    def get_forecast(self, request):
        context = request['context']
        entities = request['entities']

        loc = self.first_entity_value(entities, 'location')
        if loc:
            observation = self.owm.weather_at_place(loc)
            w = observation.get_weather()
            context['forecast'] = w.get_status() 
            context['location'] = loc

            if context.get('missingLocation') is not None:
                del context['missingLocation']
        else:
            context['missingLocation'] = True
            if context.get('forecast') is not None:
                del context['forecast']

        return context

    def get_extra_forecast(self, request):
        context = request['context']
        entities = request['entities']
        location = context['location']

        observation = self.owm.weather_at_place(location)
        w = observation.get_weather()
        temperature = w.get_temperature(unit='celsius')
        weather_temp = ' '.join(map(str, (temperature['temp_min'],temperature['temp'],temperature['temp_max'])))
        humidity = str(w.get_humidity())

        context['extraForecast'] = 'В '+ location + ' температура:' +weather_temp + ' влажность:' + humidity
        return context

    def clear_story(self, request):
        context = request['context']
        entities = request['entities']

        if context.get('missingLocation') is not None:
            del context['missingLocation']
        if context.get('forecast') is not None:
            del context['forecast']
        if context.get('extraForecast') is not None:
            del context['extraForecast']
        return context

def main():
    updater = Updater(TELEGRAM_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler([Filters.text], echo))

    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()

def echo(bot, update):
    logger.info('Info "%s" "%s"' % (update.message.text, ''))
    echo = witHandler.recive(update.message.chat_id, update.message.text)
    bot.sendMessage(update.message.chat_id, text=str(echo['text'].decode('utf-8')))
    if echo['quickreplies']:
        start(bot, update, echo['quickreplies'])

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

def start(bot, update, data):
    """keyboard = [[InlineKeyboardButton("Подробнее", callback_data='Подробнее'),
                 InlineKeyboardButton("Ясно", callback_data='Ясно')]]"""
    keyboard = [[InlineKeyboardButton(button, callback_data=button) for button in data]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    bot.sendMessage(update.message.chat_id, text="Ответить:", reply_markup=reply_markup)


def button(bot, update):
    query = update.callback_query
    echo = witHandler.recive(query.message.chat_id, query.data)
    bot.editMessageText(text="%s" % str(echo['text'].decode('utf-8')),
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id)

witHandler = WitSystem()
if __name__ == '__main__':
    main()