#!/usr/bin/python
# -*- coding: utf-8 -*-

#import
import config as c
import RPi.GPIO as g
from pirc522 import RFID
from time import sleep
from time import time
from thread import start_new_thread as thread
import sqlite3 as lite
import binascii
import signal
import termios
import sys
import tty
###########################################

#RFID
r = RFID()
inbuf = []
bc = False
bt = 0

class Database:
	db = False

	#def __init__(self):
	#	self.open()

	#def __exit__(self):
	#	self.close()
	def open(self):
		self.db = lite.connect(c.DBFILE)
		if self.db:
			return True
		else:
			return False

	def close(self):
		if self.db:
			self.db.close()

	def query(self,que):
		cur = self.db.cursor()
		if que.startswith("SELECT") or que.startswith("select"):
			cur.execute(str(que))
			return cur.fetchall()
		else:
			try:
				cur.execute(str(que))
				self.db.commit()
				return True
			except:
				return False

###########################################
# allg funktionen
def cent(integ):
	if integ < 0:
		vorz = "-"
		integ = integ*(-1)
	else:
		vorz = ""
	cent = integ % 100
	euro = (integ-cent)/100
	if cent < 10:
		return vorz+str(euro)+",0"+str(cent)
	else:
		return vorz+str(euro)+","+str(cent)

def debug(s):
	if c.DEBUG:
		print(s)

def toHex(s):
	return binascii.hexlify(bytearray(s))

def main():
	rf = False
	rt = 0
	global bc
	global bt
	sql = False
	account = False
	product = False
	on = False

	# Display GPIO
	g.setwarnings(False)
	g.setmode(g.BOARD)       # Use BCM GPIO numbers
	g.setup(c.LCD_E, g.OUT)  # E
	g.setup(c.LCD_RS, g.OUT) # RS
	g.setup(c.LCD_D4, g.OUT) # DB4
	g.setup(c.LCD_D5, g.OUT) # DB5
	g.setup(c.LCD_D6, g.OUT) # DB6
	g.setup(c.LCD_D7, g.OUT) # DB7
	
	#LED GPIO
	g.setup(c.LED_RED, g.OUT) #rote LED
	g.setup(c.LED_GREEN, g.OUT) #gruene LED

	# Initialise display
	lcd_init()

	debug("D: init")
	# Send some test
	lcd_string("XXXXXXXXXXXXXXXXXXXX",c.LCD_LINE_1)
	lcd_string("XXXXXXXXXXXXXXXXXXXX",c.LCD_LINE_2)
	lcd_string("XXXXXXXXXXXXXXXXXXXX",c.LCD_LINE_3)
	lcd_string("XXXXXXXXXXXXXXXXXXXX",c.LCD_LINE_4)
	sleep(1)

	debug("D: test")
	lcd_string("   Projekt  Midas   ",c.LCD_LINE_1)
	lcd_string("    Kassensystem    ",c.LCD_LINE_2)
	lcd_string("    Version 0.3.1    ",c.LCD_LINE_3)
	lcd_string("   electronicfreak  ",c.LCD_LINE_4)
	sleep(3)
	debug("D: start")

	lcd_blank()

	thread(barc_thread,())

	while True:
		rf = rfid_get()
		if rf:
			db.open()
			account = db_account(rf)
			if account:
				on = True
				rt = time()
				if not product:
					dis_account(account[0][0],account[0][1],account[0][2])
			else:
				rt = time()
				dis_unkacc()
				db_newacc(rf)
				led_insert()

		if bc:
			db.open()
			product = db_product(bc)
			if product:
				on = True
				#lcd_string(bc,c.LCD_LINE_2)
				if not account:
					dis_product(product[0][0],product[0][1],product[0][2],product[0][3])
			else:
				on = True
				bc = False
				bt = time()
				dis_unkpro()

		soon = time() - c.TIMED
		#debug(str(product) +" - "+ str(account))
		if product and account:
			bt = time()
			rt = bt
			if db_buy(account[0][0],product[0][0]):
				dis_buy(account[0][1],product[0][3])
				led_ok()
			else:
				dis_nobuy()
				led_fail()
			bc = False
			rf = False
			product = False
			account = False

		if soon > bt:
			bt = 0
			bc = False
			product = False

		if soon > rt:
			rt = 0
			account = False

		if rt == 0 and bt == 0 and on:
			on = False
			lcd_blank()
			db.close()
		
		sleep(0.5)

# ungetestet
def db_account(uuid):
	global db
	data = db.query("SELECT tokenID, cash, saldo FROM tokens WHERE tokenID = '"+uuid+"'")
	if len(data) == 1:
		#token gefunden
		return data
	return False

#ungetestet
def db_product(barcode):
	global db
	data = db.query("SELECT snackID, name, amount, price FROM snacks WHERE snackID = '"+barcode+"'")
	if len(data) == 1:
		#code gefunden
		return data
	else:
		#code nicht existent
		return False

def db_newacc(uuid):
	global db
	if db.query("INSERT INTO tokens (tokenID,cash,saldo) VALUES ('"+uuid+"',0,0);"):
		debug("New Token success")
	else:
		debug("New Token failed")

def db_buy(rfid,barcode):
	global db
	snack = db.query("SELECT price, amount FROM snacks WHERE snackID = '"+barcode+"'")
	if rfid != "":
		token = db.query("SELECT cash, saldo FROM tokens WHERE tokenID = '"+rfid+"'")
		#prüfen ob ausreichend geld da ist
		if (token[0][0]+token[0][1])>snack[0][1]:
			#wenn ja, 
			#geld abziehen
			if snack[0][0] < 0:
				db.query("UPDATE tokens set cash=cash+("+str(snack[0][0]*(-1))+") WHERE tokenID='"+rfid+"';")
			else:
				db.query("UPDATE tokens set cash=cash-"+str(snack[0][0])+" WHERE tokenID='"+rfid+"';")
			#todo prüfen, ob geld wirklich abgebucht wurde
			#snack amount reducen
			db.query("UPDATE snacks SET amount=amount-1 WHERE snackID = '"+barcode+"'")
			return True
	return False

def dis_account(uuid,guthaben,limit):
	lcd_string(uuid,c.LCD_LINE_1)
	lcd_string("Guthaben: "+ str(cent(guthaben)),c.LCD_LINE_2)
	lcd_string("Limit: "+ str(cent(limit)),c.LCD_LINE_3)
	lcd_string("",c.LCD_LINE_4)

	debug("D: account abfrage UUID:"+ str(uuid) +" Guthaben:"+ str(guthaben) +" Limit:"+ str(limit))

#produkt daten
def dis_product(barcode,prodname,amount,price):
	lcd_string(prodname,c.LCD_LINE_1)
	lcd_string("Preis: "+ str(cent(price)),c.LCD_LINE_2)
	lcd_string("Anzahl: "+ str(amount),c.LCD_LINE_3)
	lcd_string("",c.LCD_LINE_4)

	debug("D: produkt abfrage "+ str(barcode) +" Bez:"+ str(prodname) +" Anzahl:"+ str(amount) +" Preis:"+ str(price))

def dis_unkpro():
	lcd_string("O------------------O",c.LCD_LINE_1)
	lcd_string("|     No Entry     |",c.LCD_LINE_2)
	lcd_string("O------------------O",c.LCD_LINE_3)
	lcd_string("",c.LCD_LINE_4)
	
	debug("D: unbekannter Barcode")

#rfid ohne account gescannt
def dis_unkacc():
	lcd_string("O------------------O",c.LCD_LINE_1)
	lcd_string("|   New Account    |",c.LCD_LINE_2)
	lcd_string("O------------------O",c.LCD_LINE_3)
	lcd_string("",c.LCD_LINE_4)
	
	debug("D: unbekannte RFID")

def dis_buy(guthaben,price):
	lcd_string(str(cent(guthaben)),c.LCD_LINE_1)
	lcd_string(str(cent(price*(-1))),c.LCD_LINE_2)
	lcd_string("--------------------",c.LCD_LINE_3)
	lcd_string(str(cent(guthaben-price)),c.LCD_LINE_4)
	
	debug("D: kauf erfolgreich Guthaben:"+ str(guthaben) +" Preis:"+ str(price))

#kauf fehlgeschlagen
def dis_nobuy():
	lcd_string("O------------------O",c.LCD_LINE_1)
	lcd_string("|  N O    D E A L  |",c.LCD_LINE_2)
	lcd_string("O------------------O",c.LCD_LINE_3)
	lcd_string("",c.LCD_LINE_4)
	
	debug("D: kauf fehlgeschlagen")

def rfid_get():
	global r

	(error, tag_type) = r.request()
	if not error:
		debug("Tag detected")
		(error, uid) = r.anticoll()
		if not error:
			uuid = toHex(uid)
			debug("UID: " + uuid)
			return uuid
	return False

# warte auf eingabe in den eingabe buffer und nehme ein zeichen
# getestet
def bc_char():
	fd = sys.stdin.fileno()
	old_settings = termios.tcgetattr(fd)
	debug("CH:check")
	try:
		tty.setraw(sys.stdin.fileno())
		ch = sys.stdin.read(1)
		debug(ch)
	finally:
		termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
	return ch

# timeout aufräum funktion
# glaube unnoetig
def interrupted(signum,frame):
	global inbuf
	inbuf = []
	debug("Interrupted!!!")
	
# warte auf eingabe mit timeout
# getestet
def barc_thread():
	global inbuf
	global bc
	global bt
	sig = 0
	
	while True:
		r = bc_char()
		if r == '#':
			exit()
		
		
		debug(str((sig + c.TIMEO)) +" : "+ str(time()))
		if (sig + c.TIMEO) < time():
			inbuf = []
		sig = time()
		inbuf.append(str(r))
		
		debug((r,len(inbuf)))
		if len(inbuf) >= c.BCLEN:
			bc = "".join(inbuf)
			debug(bc)
			bt = time()
			inbuf = []
		else:
			bc = False
			bt = 0

def lcd_init():
	# Initialise display
	lcd_byte(0x33,c.LCD_CMD) # 110011 Initialise
	lcd_byte(0x32,c.LCD_CMD) # 110010 Initialise
	lcd_byte(0x06,c.LCD_CMD) # 000110 Cursor move direction
	lcd_byte(0x0C,c.LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
	lcd_byte(0x28,c.LCD_CMD) # 101000 Data length, number of lines, font size
	lcd_byte(0x01,c.LCD_CMD) # 000001 Clear display
	sleep(c.E_DELAY)

def lcd_blank():
	debug("L: blank")
	lcd_byte(0x01,c.LCD_CMD)
	sleep(c.E_DELAY)

def lcd_byte(bits, mode):
	# Send byte to data pins
	# bits = data
	# mode = True  for character
	#        False for command

	g.output(c.LCD_RS, mode) # RS

	# High bits
	g.output(c.LCD_D4, False)
	g.output(c.LCD_D5, False)
	g.output(c.LCD_D6, False)
	g.output(c.LCD_D7, False)
	if bits&0x10==0x10:
		g.output(c.LCD_D4, True)
	if bits&0x20==0x20:
		g.output(c.LCD_D5, True)
	if bits&0x40==0x40:
		g.output(c.LCD_D6, True)
	if bits&0x80==0x80:
		g.output(c.LCD_D7, True)

	# Toggle 'Enable' pin
	lcd_toggle_enable()

	# Low bits
	g.output(c.LCD_D4, False)
	g.output(c.LCD_D5, False)
	g.output(c.LCD_D6, False)
	g.output(c.LCD_D7, False)
	if bits&0x01==0x01:
		g.output(c.LCD_D4, True)
	if bits&0x02==0x02:
		g.output(c.LCD_D5, True)
	if bits&0x04==0x04:
		g.output(c.LCD_D6, True)
	if bits&0x08==0x08:
		g.output(c.LCD_D7, True)

	# Toggle 'Enable' pin
	lcd_toggle_enable()

def lcd_toggle_enable():
	# Toggle enable
	sleep(c.E_DELAY)
	g.output(c.LCD_E, True)
	sleep(c.E_PULSE)
	g.output(c.LCD_E, False)
	sleep(c.E_DELAY)

def lcd_string(message,line):
	# Send string to display

	message = message.ljust(c.LCD_WIDTH," ")

	lcd_byte(line, c.LCD_CMD)

	for i in range(c.LCD_WIDTH):
		lcd_byte(ord(message[i]),c.LCD_CHR)

def led(io,muster):
	m = list(muster)
	for n in m:
		g.output(io,int(n))
		sleep(0.25)
	g.output(io,0)

def led_ok():
	thread(led,(c.LED_GREEN,"1111"))

def led_fail():
	thread(led,(c.LED_RED,"11110000111100001111"))

def led_insert():
	thread(led,(c.LED_GREEN,"10101010"))

if __name__ == '__main__':
	#try:
		db = Database()
		main()
	#except KeyboardInterrupt:
		pass
	#finally:
		lcd_byte(0x01, c.LCD_CMD)
		g.cleanup()