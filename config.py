
token = 'Token'
token2= 'Token2'


import telebot
bot = telebot.TeleBot(token)



'''
chat_test_id='-000000000'
chat_daeps_id='0000000000'

@bot.message_handler(commands=['anonim'])
def start_message(message):
	msg = bot.send_message(message.chat.id, "Это абсолютно анонимно, заверяю вас!")
	bot.register_next_step_handler(msg, anon)
	dell(message, 1)

def anon(message):
	bot.send_message(chat_test_id, message.text)
'''
