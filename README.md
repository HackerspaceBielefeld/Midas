# Midas
Ein Kassen system für den Hackerspace Bielefeld. Es soll auf der einen seite ein Prepaid system anbieten und auf der anderen Seite unseren Kassenwart entlasten indem er passend informiert wird, wenn etwas zu neige geht.

## Eckpunkte
- [x] Produkt-Barcode einlesen
- [x] Bezahlen mit Tür RFID
- [x] Option nur konto daten
- [x] Option nur preis abfrage
- [ ] Bar zahlung
- [ ] storno
- [x] aufladen mit Barcode

## Installation
### 1. config
im raspi-config, den spi treiber aktivieren
### 2. modprobe
mit 
```
modprobe spi_bcm2708
```
oder
```
modprobe spi_bcm2835
```
testen ob der SPI treiber läuft
### 3. apt	
Pakete nach installieren
```
sudo -i
apt install git-core python-dev
apt install python-spidev python-sqlite
apt install python-pip

pip install spi
pip install pi-rc522
```
### 4. test
Testen ob python alles übernommen hat in python
```
import spidev
```
Es muss eine /dev/spidev0.0 datei existieren
### 5. User
user anlegen
 sudo adduser midas
 
user in gruppe hinzufügen
 usermod -a -G spi midas
 usermod -a -G gpio midas

### 6. Installieren
git clonen
 su midas
 git clone https://git.electronicfreak.de/HSB/Midas
 
autologin
 sudo nano /etc/systemd/system/getty@tty1.service.d/autologin.conf
```
dort folgendes anhängen
 cd Midas
 ./midas.py
```
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

### 40pin Pi brauchen noch /boot/config.txt update
  device_tree_param=spi=on
  dtoverlay=spi-bcm2708

## Links
* SPI
  * http://www.netzmafia.de/skripten/hardware/RasPi/RasPi_SPI.html
  * https://www.raspberrypi.org/documentation/hardware/raspberrypi/spi/README.md
* System
  * http://www.benjaminroesner.com/blog/raspberry-pi-benutzer-automatisch-anmelden-booten/
  * http://www.forum-raspberrypi.de/Thread-tutorial-automatisches-starten-von-scripte-programme-autostart
* Display
  * http://www.raspberrypi-spy.co.uk/2012/07/16x2-lcd-module-control-using-python/
* RFID
  * http://tutorials-raspberrypi.de/raspberry-pi-rfid-rc522-tueroeffner-nfc/
  
# V3
##evtl nicht mehr nötig
SPI-Py installieren
github clone und dann
  sudo ./SPI-py/setup.py install