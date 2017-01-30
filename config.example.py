#!/usr/bin/python
# coding: utf8

DBFILE = 'data/data.db'	#SQLite file

BCLEN = 3				#barcode länge
TIMEO = 5				#timeout für unvollständige eingaben

TIMED = 10				#Displayzeit bzw zeit um zukaufen

DPWM = 18				#pin für helligkeit des monitors
DHELL = 20				#default helligkeit

DEBUG = True


# Define GPIO to LCD mapping
LCD_RS = 3
LCD_E  = 5
LCD_D4 = 7
LCD_D5 = 18
LCD_D6 = 16
LCD_D7 = 12

# Define some device constants
LCD_WIDTH = 20    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line

# LED GPIOs
LED_GREEN = 32
LED_RED = 36

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005