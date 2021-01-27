import os
import database 
import telebot
from telebot import types

import datetime
import pytz


API_KEY = os.environ['API_KEY']
DATABASE_URL=os.environ['DATABASE_URL']



db = database.DB(DATABASE_URL)

'''
 gets datetime
 returns [lesson, url]
'''
def get_timetable(date):
    chet = int(date.astimezone().isocalendar()[1])%2 == 0
    weekday = date.weekday()
    day = db.execute('select * from dow where id = '+str(weekday))[0]
    lessons = db.execute('select * from lesson')

    timetable = []
    if isinstance(day[2],list):
      for lessonFromTable in day[2]: # 2 - числитель 3 - знаменатель
        for lessonFromList in lessons:
            if lessonFromTable == lessonFromList[1]:
                timetable.append([lessonFromTable,lessonFromList[2]])

    return timetable

class Bot:
    def __init__(self, API_TOKEN):
        self.bot = telebot.TeleBot(API_TOKEN)
        self.set_real_today()

    def set_real_today(self):
        self.today = datetime.datetime.now(pytz.timezone('Europe/Kiev'))

    # LaU = [['Lesson','URL'],...]
    def generate_markup(self, LaU, markup = None):
        if markup is None:
            markup = types.InlineKeyboardMarkup()
        for lesson in LaU:
            markup.add(types.InlineKeyboardButton(text = lesson[0], url = 'google.com'))
        return markup

    #first message
    def start(self):
        @self.bot.message_handler(commands=['start'])
        def start_message(message):
            timetable = get_timetable(self.today)

            markup = self.generate_markup(timetable)

            previousB = types.InlineKeyboardButton(text = '<', callback_data = 'previous')
            todayB = types.InlineKeyboardButton(text = '=', callback_data = 'today')
            nextB = types.InlineKeyboardButton(text = '>', callback_data = 'next')
            markup.row(previousB,todayB,nextB)

            self.bot.send_message(message.chat.id,str(self.today.strftime("%A, %d. %B")), reply_markup=markup)

        #callback
        @self.bot.callback_query_handler(func=lambda call: True)
        def callback_inlinett(call):
            if call.message:
                if call.data == 'today':
                    self.set_real_today()
                    timetable = get_timetable(self.today)
                    
                    markup = self.generate_markup(timetable)

                    previousB = types.InlineKeyboardButton(text = '<', callback_data = 'previous')
                    todayB = types.InlineKeyboardButton(text = '=', callback_data = 'today')
                    nextB = types.InlineKeyboardButton(text = '>', callback_data = 'next')
                    markup.row(previousB,todayB,nextB)
                    self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = 'К' ,reply_markup=markup)
                    self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = str(self.today.strftime("%A, %d. %B")), reply_markup=markup)

                if call.data == 'previous':
                    self.today -= datetime.timedelta(1)
                    timetable = get_timetable(self.today)
                    
                    markup = self.generate_markup(timetable)

                    previousB = types.InlineKeyboardButton(text = '<', callback_data = 'previous')
                    todayB = types.InlineKeyboardButton(text = '=', callback_data = 'today')
                    nextB = types.InlineKeyboardButton(text = '>', callback_data = 'next')
                    markup.row(previousB,todayB,nextB)
                    self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = str(self.today.strftime("%A, %d. %B")), reply_markup=markup)

                if call.data == 'next':
                    self.today += datetime.timedelta(1)
                    timetable = get_timetable(self.today)
                    markup = self.generate_markup(timetable)

                    previousB = types.InlineKeyboardButton(text = '<', callback_data = 'previous')
                    todayB = types.InlineKeyboardButton(text = '=', callback_data = 'today')
                    nextB = types.InlineKeyboardButton(text = '>', callback_data = 'next')
                    markup.row(previousB,todayB,nextB)
                    
                    self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = str(self.today.strftime("%A, %d. %B")), reply_markup=markup)


        self.bot.polling()

bot = Bot(API_KEY)
bot.start()
