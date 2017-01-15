# Midas
Ein Kassen system für den Hackerspace Bielefeld. Es soll auf der einen seite ein Prepaid system anbieten und auf der anderen Seite unseren Kassenwart entlasten indem er passend informiert wird, wenn etwas zu neige geht.

## Eckpunkte
* Produkt-Barcode einlesen
* Bezahlen mit Tür RFID
* Option nur konto daten
* Option nur preis abfrage
* Bar zahlung
* storno
* aufladen mit Barcode

## Hardware
* RaspPi 1 oder besser
* TFT 1,8 Zoll SPI Display
* PS2-Barcode-Scanner

## Pinbelegung

## Probleme
### SQLSTATE[HY000] [14] unable to open database file
noch kein install.py ausgeführt

### DB nicht les/schreibbar
datei UND ordner rechte müssen lesen und schreibbar sein

## Links
* SPI
  * http://www.netzmafia.de/skripten/hardware/RasPi/RasPi_SPI.html
  * https://www.raspberrypi.org/documentation/hardware/raspberrypi/spi/README.md
* System
  * http://www.benjaminroesner.com/blog/raspberry-pi-benutzer-automatisch-anmelden-booten/
  * http://www.forum-raspberrypi.de/Thread-tutorial-automatisches-starten-von-scripte-programme-autostart
* Display
  * https://www.xgadget.de/anleitung/2-2-spi-display-ili9341-am-raspberry-betreiben/
* RFID
  * http://tutorials-raspberrypi.de/raspberry-pi-rfid-rc522-tueroeffner-nfc/
  * https://github.com/ondryaso/pi-rc522
