# Air-Quality-Sensor-Suite-MkII
A simple, compact and accurate air quality monitor built around a Raspberry Pi 3 or Pi Zero W with the ability to inteface with industrial SCADA systems via Modbus TCP. With a few additional lines of code in the main loop it's relatively straightfoward to push the entire collected and calculated data set to an MQTT broker.

The two attached sensors read temperature, pressure, humidity, VOC and particulates. The script then derives other quantities such as dewpoint, air density, air quality index (AQI), NowCast and indoor air quality (IAQ).

* [Air Quality Index](https://en.wikipedia.org/wiki/Air_quality_index)
* [NowCast](https://en.wikipedia.org/wiki/NowCast_(air_quality_index))

## Usage Notes
While tested on Raspian Jessie and Python3 it will probably run on older versions of Python or newer versions of Raspbian with little or no modification.

```sudo python3 main.py```

By default the Modbus slave binds to all active connections. Root privledges are
requred because we're serving on the Modbus default port 502.

As a practical matter you'll probably want to set this script up to run as a service 
with systemd rather than using cron or rc.local. 

https://www.raspberrypi.org/documentation/linux/usage/systemd.md

## Requirements

### Modbus-tk
https://github.com/ljean/modbus-tk

This provides the MODBUS TCP transport. Values are mapped into holding registeres encoded as an [IEEE 754 32-bit float](https://en.wikipedia.org/wiki/IEEE_754). If you're using Modpoll for testing be aware that tool uses an older IEEE 754 standard so the values it reports will be a little bit off. 

If you'd like to send the data to an MQTT broker instead just install Paho and modify the relevant sections in ```main.py```.

### Pigpio
http://abyz.me.uk/rpi/pigpio/index.html

This is used to bitbang GPIO 18 to interface with the PMS5003, just pick another pin if that's inconvenient. 

### Pimoroni BME680
https://github.com/pimoroni/bme680

I'm using an Adafruit breakout board with the Pimoroni library for their breakout board. Both breakout boards are functionally identical, the only difference between them is the default I2C address so we just specify that when we create the instance.

```bme680.BME680(i2c_addr=0x77)```

## Sensors/Interfaces
### BME680 (I2C) 
* [datasheet](https://cdn-shop.adafruit.com/product-files/3660/BME680.pdf)
* https://shop.pimoroni.com/products/bme680
* https://www.adafruit.com/product/3660

### PMS5003 (software serial)
* [datasheet](https://cdn-shop.adafruit.com/product-files/3686/plantower-pms5003-manual_v2-3.pdf)
* https://www.adafruit.com/product/3686

![wiring](/img/aqm-mk-II_bb1.jpg)

## MODBUS Register Map
### System
```
40001   Quality Control (3.14159265359)
```
### Measured BME680
```
40003   Temperature (C)
40005   Temperature (F)
40007   Pressure (hPa)
40009   Pressure (inHg)
40011   Relative Humidity (%)
40013   VOC (kOhm)
```
### Measured PMS5003
```
40015   PM1.0 standard (ug/m3)
40017   PM2.5 standard (ug/m3)
40019   PM10 standard (ug/m3)
40021   PM1.0 environmental (ug/m3)
40023   PM2.5 environmental (ug/m3)
40025   PM10 environmental (ug/m3)
40027   Particles > 0.3 um / 0.1L air
40029   Particles > 0.5 um / 0.1L air
40031   Particles > 1.0 um / 0.1L air
40033   Particles > 2.5 um / 0.1L air
40035   Particles > 5.0 um / 0.1L air
40037   Particles > 50  um / 0.1L air
```
### Derived
```
40039   Dewpoint (C)
40041   Dewpoint (F)
40043   Partial pressure water vapor (hPa)
40045   Partial pressure dry air (hPa)
40047   Air density (kg/m3)
40049   Air density (lb/ft3)

40051   AQI (0-500, -1 if unavailable)
40053   PM25 contribution to AQI
40055   PM10 contribution to AQI
40057   AQI NowCast
40059   PM25 contribution to AQI NowCast
40061   PM10 contribution to AQI NowCast
40063   AQI Current (1 minute)
40065   PM25 contribution to AQI Current
40067   PM10 contribution to AQI Current

40069   PM01 60 second average (ug/m3)
40071   PM01 60 minute average (ug/m3)
40073   PM01 24 hour average (ug/m3)
40075   PM25 60 second average (ug/m3)
40077   PM25 60 minute average (ug/m3)
40079   PM25 24 hour average (ug/m3)
40081   PM10 60 second average (ug/m3)
40083   PM10 60 minute average (ug/m3)
40085   PM10 24 hour average (ug/m3)

40087   IAQ (0-100, -1 if unavailable)
40089   RH contribution to IAQ
40091   VOC contribution to IAQ
40093   VOC 60 second average (kOhm)
40095   VOC 60 minute average (kOhm)
40097   VOC 24 hour average (kOhm)
```
## Classes
### Cascadable Running/Retained Average 
The first challenge is that AQI requires a 24 hour average measurement and embedded systems can rest at any time. The second is if you're sampling at 1 second intervals that's 86400 (60*60*24) samples to average.

This class allows you to define a one second sample aggregated to a one minute average, cascaded to a one hour average, cascaded to a one day average (lather, rise and repeat for weekly, monthly or annual), writing the results to storage and reloading as necessary between resets. In the 24 hour example it only retains 144 values (60+60+24). As you're building history to whatever average you've defined, the class will provide the best approximation available.

The caveat with SD storage is you have a finite number of write cycles. To start I've chosen the compromise of writing hourly. If the reset is short duration, it won't significantly compromise the results. 

```python
pm25_24h = CRR_AVG(24, jfile = "pm25_24h")    # daily average (retained)
pm25_60m = CRR_AVG(60, pm25_24h)              # hourly average
pm25_60s = CRR_AVG(60, pm25_60m)              # minutely average
```
### Unit Conversion
Weather calculations are notorious for mixing SI and imperial units and combining constants making them difficult to follow. Even with SI it's not uncommon to switch back and forth between units like Celsius and Kelvin.

To simplify, pass an SI value (Celsius) when you initialize a unit conversion object. You can then retrieve the value in any relavant unit, SI or imperial (Celsius, Kelvin, Fahrenheit or Rankine).

```python
Temperature = T(25)
print(Temperature.C, Temperature.K, Temperature.F, Temperature.R)
```

