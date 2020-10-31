# raspi-sensorics
Code for reading various sensors attached to a Raspberry Pi

Sensors
* BME280 3.3V version (Temperature, Humidity, Pressure) via wired I2C protocol
* Fritzbox for reading list of online devices via API
* Mi Flower Care for reading plant condition via Bluetooth

Setup
* Raspberry Pi 3 Model B
* Data is stored in an InfluxDB V. 1.8.3
* Data is visualized via Grafana V. 7.2.2
* Multiple Arduino ESP32 microcontrollers are pushing data to the same InfluxDB too, see https://github.com/entorb/arduino-sensorics/
