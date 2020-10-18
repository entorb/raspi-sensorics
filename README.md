# raspi-sensorics
Code for reading various sensors attached to a Raspberry Pi

Sensors
* BME280 3.3V version (Temperature, Humidity, Pressure) via wired I2C protocol
* Fritzbox for reading list of online devices via API
* Mi Flower Care for reading plant condition via Bluetooth

Setup
* Raspberry Pi 3 Model B
* Data is stored in an InfluxDB V. 1.6.4
* Data is visualized via Grafana V. 6.2.5
