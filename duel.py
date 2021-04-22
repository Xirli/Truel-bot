
from telebot import types
from config import *
from random import random
import time
from threading import Thread
from enum import Enum


class Game(Enum):
	OFF       = 0
	ENROLMENT = 1
	WAITING   = 2
	ON        = 3

gamer = []    # Массив игроков
dead  = []    # Массив мёртвых

game = Game.OFF
timeEnrolment = 10
timeWaiting   = 5

#kolGamer = 0     # Количество игроков
#isReady  = 0     # Сколько игроков готовы к бою
#isGame   = False # Идёт ли сейчас игра?

speedLight = 2   # Время полёта пули, да, название переменной немного не совпадает с её предназначением...
reloadGun  = 5   # Время перезарядки оружияы
timeEnd    = 1   # Игра заканчивается через timeEnd секунд, после попадания последней пули

#isEnd = False    # True = игра окончена



class Duelist:

	def __init__ (self, name, user_id):
		self.name = name
		self.user_id = user_id
		self.gun = None
		self.area_id = None
		self.keyboard_id = None


	def kill(self, user):
		t = Thread(target=user.shot(self))
		t.start()

		if user == self :
			return 0

		if self.area_id is not None:
			bot.delete_message(self.user_id, self.area_id)
		if self.keyboard_id is not None:
			bot.delete_message(self.user_id, self.keyboard_id)

		bot.send_message(self.user_id, "Перезарядка...")
		time.sleep(reloadGun)

		if searchDuelist(self.user_id) is None:
			return 0;

		self.area = sendListGamers()
		self.area_id = bot.send_message(self.user_id, self.area).message_id

		keyboard = getKeyboard()
		self.keyboard_id = bot.send_message(self.user_id, "Стрельнуть в:", reply_markup = keyboard, parse_mode="Markdown").message_id

	def shot(user, killer):
		global gamer
		global dead

		if killer == user:
			user.death(killer)
			return 0

		bot.send_message(killer.user_id, "Пуля летит в " + user.name)
		time.sleep(speedLight)

		if random() > killer.gun.hit:
			bot.send_message(killer.user_id, "Вы промазали.")
			return 0


		if searchDuelistName(user.name) == None:
			bot.send_message(killer.user_id, "Игрока " + user.name + " убили раньше вас!")
			return 0

		user.death(killer)



	def death(self, killer):
		global gamer
		global dead

		if killer == self:
			bot.send_message(self.user_id, "Вы неспешно поднесли " + self.gun.name + " к виску...\nЕщё секунда и на земле лежит ещё один труп.")
		else:
			bot.send_message(self.user_id, "Вас убил " + str(killer.name))
			bot.send_message(killer.user_id, "Вы убили игрока " + self.name )

		gamer.remove(self)
		dead.append(self)

		#if area_id is not None:
		bot.delete_message(self.user_id, self.area_id)
		bot.delete_message(self.user_id, self.keyboard_id)

		text = sendListGamers()
		keyboard = getKeyboard()
		for g in gamer:
			"""
			bot.edit_message_text(chat_id=g.user_id, message_id=g.area_id,     text=text)
			bot.edit_message_text(chat_id=g.user_id, message_id=g.keyboard_id, text="Стрельнуть в:", reply_markup=keyboard)
			"""
			g.area_id     = bot.edit_message_text(chat_id=g.user_id, message_id=g.area_id,     text=text).message_id
			g.keyboard_id = bot.edit_message_text(chat_id=g.user_id, message_id=g.keyboard_id, text="Стрельнуть в:", reply_markup=keyboard).message_id
		
		time.sleep(speedLight + timeEnd)
		isEndF()

		return 0
		


class Gun:

	def __init__ (self,id):
		self.id = id
		if(id == 0):
			self.name = "AWP"
			self.hit  = 0.9
		elif (id == 1):
			self.name = "Револьер"
			self.hit  = 0.5

		elif (id == 2):
			self.name = "Дротики"
			self.hit  = 0.1

#Поиск игрока за id/именем
def searchDuelist(user_id):
	for g in gamer:
		if user_id == g.user_id:
			return g
	return None

def searchDuelistName(user_name):
	for g in gamer:
		if user_name == g.name:
			return g
	return None


#Составляет список врагов, и отравляет их игроку
def sendListGamers():
	text = ""
	for g in gamer:
		text += g.name + " " + str(g.gun.hit) +"\n"

	for d in dead:
		text += "~~" + d.name + "~~\n"

	return text
 
#Составляет список врагов, и добавляет их в клавиатуру keyboard
def getKeyboard():
	keyboard = types.InlineKeyboardMarkup()
	for g in gamer:
		user = types.InlineKeyboardButton(text = g.name +' '+str(g.gun.hit), callback_data="game"+g.name)
		keyboard.add(user)
	return keyboard



def isEndF():
	global gamer
	global dead

	global game

	if len(gamer) >1:
		return 0
	if game == Game.OFF:
		return 0

	game = Game.OFF

	if len(gamer) == 1:
		winer = gamer[0]
		bot.send_message(winer.user_id,"Вы победили!")
		for d in dead:
			bot.send_message(d.user_id,"Игра окончена! Игрок " + winer.name + " победил.")

	if len(gamer) == 0:
		for d in dead:
			bot.send_message(d.user_id,"Игра окончена!\nНа поле остались лишь трупы, никто не выжил...")

	gamer.clear()
	dead.clear()


def timer():
	global game

	game = Game.ENROLMENT
	time.sleep(timeEnrolment)
	game = Game.WAITING
	time.sleep(timeWaiting)
	game = Game.ON

	
	if len(gamer) == 1 :
		bot.send_message(gamer[0].user_id, "Недостаточно игроков для игры.")
	if len(gamer) <= 1 :
		game = Game.OFF
		gamer.clear()
		return 0


	area =  sendListGamers()
	keyboard = getKeyboard()

	for g in gamer:
		g.area_id     = bot.send_message(g.user_id, area).message_id
		g.keyboard_id = bot.send_message(g.user_id, "Стрельнуть в:", reply_markup=keyboard).message_id




#Игрок вступает в бой
@bot.message_handler(commands=['battle'])
def start_message(message):
	global kolGamer
	global gamer

	#Записываем данные игрока
	duelist = Duelist( message.from_user.first_name, message.from_user.id )

	#Проверяем всякие ситуации
	if searchDuelist(duelist.user_id) is not None:
		bot.send_message(message.chat.id, "Вы уже в игре!")
		return 0

	global game
	if game.value > 1:
		bot.send_message(message.chat.id, "Уже идёт бой, дождитесь его окончания.")
		return 0

	if(message.chat.type != 'private'):
		bot.send_message(message.chat.id, "Напишите в личку /battle чтоб начать игру.")
		return 0
	

	
	
	t = Thread(target = timer)
	t.start()

	#Выбираем пушку
	keyboard = types.InlineKeyboardMarkup()
	gun0 = types.InlineKeyboardButton(text = Gun(0).name, callback_data = "gun0")
	gun1 = types.InlineKeyboardButton(text = Gun(1).name, callback_data = "gun1")
	gun2 = types.InlineKeyboardButton(text = Gun(2).name, callback_data = "gun2")
	keyboard.add(gun0,gun1,gun2)
	bot.send_message(message.chat.id, "Выберете оружие:", reply_markup=keyboard)


#Выбрали пушку
@bot.callback_query_handler(func=lambda call: call.data == "gun0" or call.data == "gun1" or call.data == "gun2")
def gun(call):

	if game.value > 2:
		bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Вы слишком долго думали, игра началась без вас.")
		return 0

	duelist = Duelist( call.message.chat.first_name, call.message.chat.id )
	gamer.append(duelist)

	if   call.data == "gun0":
		bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Вы выбрали винтовку.")
		#duelist.gun = Gun(0)
	elif call.data == "gun1":
		bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Револьер — вот ваше оружие.")
		#duelist.gun = Gun(1)
	elif call.data == "gun2":
		bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Настоящие мужики стреляют только дротиками!")
		#duelist.gun = Gun(2)
	duelist.gun = Gun(int(call.data[3:]))

	bot.send_message(call.message.chat.id, "Набираем игроков...")





#Игрок стрельнул
@bot.callback_query_handler(func=lambda call: call.data[:4] == "game")
def gun(call):

	user = searchDuelistName(call.data[4:])
	killer = searchDuelist(call.message.chat.id)

	if killer is None:
		return 0

	killer.kill(user)
	
