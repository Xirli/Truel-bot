from config import *
from duel import *
from bot import *


@bot.message_handler(commands=['help'])
def start_message(message):
    bot.send_message(message.chat.id, 
    	'Вы учасник перестрелки.\n'+
    	'Ваша задача убить всех противников и выжить.\n' +
    	'Перед боем вы можете выбрать оружие.\n' +
    	'Выживший является победителем.\n' +
    	'/battle - начать битву!\n')


####################################################



import time

ExceptKolSecond = 5
ExceptKolX = 10

print("Start")

while(ExceptKolX>0 or ExceptKolSecond>0):
	try:
		print ("polling")
		bot.polling(none_stop=True)      #Это всё только ради этой строчки
		ExceptKolSecond = 10;
		ExceptKolX = 10
	except:                           #Если нет интернета (плохая связь) тут возникает ошибка, её мы и ловим
		if(ExceptKolSecond>0):             #Спим 1 секунду, а потом опять пробуем присоеденится (bot.polling)
			print ("ERROR sleep 1 sec")
			time.sleep(1)                 
			ExceptKolSecond-=1
		else:                               #Спим 10 секунд, а потом опять пробуем присоеденится (bot.polling)
			print ("ERROR sleep 10 sec")
			time.sleep(10)
			ExceptKolX-=1

