""" Example SGP30 humidity compensation using a BME680 on a Raspberry Pi """

import time
import board
import busio
import bme680

import adafruit_sgp30
from math import *
""" Extend the SPG30 class to include humidity compensation """
class sgp30hc(adafruit_sgp30.Adafruit_SGP30):
    def set_humidity(self, t, RH):
        """Set the humitity compensation using temperature (C) and RH (0-100)"""
        AH = 216.7 * (((RH / 100) * 6.112 * exp((17.62 * t) / (243.12 + t))) / (273.15 + t))    
        if AH > 256:
            raise RuntimeError('Invalid humidity compensation')
        buffer = []
        arr = [int(AH), floor(256 * (AH - int(AH)))]
        arr.append(self._generate_crc(arr))
        buffer += arr
        print("**** Temperature = %3.2f (C), RH = %3.2f (%%), AH = %3.2f (g/m^3), HC = 0x%02x%02x" % (t, RH, AH, arr[0], arr[1]))
        return self._run_profile(["set_humidity", [0x20, 0x61] + buffer, 0, 0.01])

    def disable_humidity(self):
        """Disable humidity compensation"""
        buffer = []
        arr = [0x00, 0x00]
        arr.append(self._generate_crc(arr))
        buffer += arr
        return self._run_profile(["disable_humidity", [0x20, 0x61] + buffer, 0, 0.01])

i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)

""" Initialize the BME680 """
s1 = bme680.BME680(i2c_addr=0x77)
s1.set_humidity_oversample(bme680.OS_2X)
s1.set_pressure_oversample(bme680.OS_4X)
s1.set_temperature_oversample(bme680.OS_8X)
s1.set_filter(bme680.FILTER_SIZE_3)
s1.set_gas_status(bme680.ENABLE_GAS_MEAS)
s1.set_gas_heater_temperature(320)
s1.set_gas_heater_duration(150)
s1.select_gas_heater_profile(0)

""" Initialize the SGP30 """
s3 = sgp30hc(i2c)
print("SGP30 serial #", [hex(i) for i in s3.serial])
s3.iaq_init()
s3.set_iaq_baseline(0x8849, 0x8ace)

try:
    elapsed_sec = 0
    while True:
        print("co2eq = %d ppm \t tvoc = %d ppb" % (s3.co2eq, s3.tvoc))
        time.sleep(1)
        elapsed_sec += 1
        if elapsed_sec > 10:
            elapsed_sec = 0
            print("**** Baseline values: co2eq = 0x%x, tvoc = 0x%x"
                  % (s3.baseline_co2eq, s3.baseline_tvoc))
            if s1.get_sensor_data():
                s3.set_humidity(s1.data.temperature, s1.data.humidity)
            else:
                s3.disable_humidity()
finally:
    #s2.bb_serial_read_close(RX)
    #s2.stop()
    #server.stop()
    pass