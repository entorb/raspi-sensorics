# raspi-sensorics
Code for reading various sources and sensors attached to a Raspberry Pi

## Setup
* Raspberry Pi 3 Model B
* Data is stored in an InfluxDB V. 1.8.3
* Data is visualized via Grafana V. 7.2.2
* Multiple Arduino ESP32 micro-controllers are pushing data to the same InfluxDB too, see my [arduino-sensorics](https://github.com/entorb/arduino-sensorics/) repository

## Sensors
* BME280 3.3V version (Temperature, Humidity, Pressure) via wired I2C protocol
* Fritzbox for reading list of online devices via API
* Mi Flower Care for reading plant condition via Bluetooth

