#!/usr/bin/env python -u
"""
Air Quality Monitor Mk II rev 1
"""

import sys
import time
from math import *

import modbus_tk
import modbus_tk.defines as cst
from modbus_tk import modbus_tcp

import bme680
import adafruit_sgp30
import board
import busio
import pigpio

from derived_wx import *
from crr_avg import *

import struct

def mb_set(addr, val):
    """ Set a pair of MODBUS holding registers with an encoded IEEE 754 32-bit float """
    j = struct.unpack('>HH',struct.pack('>f', float(val)))
    slave_1.set_values('ro', addr, j)
    return val

class sgp30hc(adafruit_sgp30.Adafruit_SGP30):
    AH = 0  # Absolute humidity (g/m^3)
    def set_humidity(self, t, RH):
        """Set the humitity compensation using temperature (C) and RH (0-100)"""
        self.AH = 216.7 * (((RH / 100) * 6.112 * exp((17.62 * t) / (243.12 + t))) / (273.15 + t))    
        if self.AH > 256:
            raise RuntimeError('Invalid humidity compensation')
        buffer = []
        arr = [int(self.AH), floor(256 * (self.AH - int(self.AH)))]
        arr.append(self._generate_crc(arr))
        buffer += arr
        print("**** Temperature = %3.2f (C), RH = %3.2f (%%), AH = %3.2f (g/m^3), HC = 0x%02x%02x" % (t, RH, self.AH, arr[0], arr[1]))
        return self._run_profile(["set_humidity", [0x20, 0x61] + buffer, 0, 0.01])

    def disable_humidity(self):
        """Disable humidity compensation"""
        buffer = []
        arr = [0x00, 0x00]
        arr.append(self._generate_crc(arr))
        buffer += arr
        return self._run_profile(["disable_humidity", [0x20, 0x61] + buffer, 0, 0.01])

if __name__ == "__main__":
    try:
        """ Initialize the MODBUS TCP slave """        
        mb_start = 40000
        mb_len = 120
        server = modbus_tcp.TcpServer(address='0.0.0.0')
        server.start()
        slave_1 = server.add_slave(1)
        slave_1.add_block('ro', cst.HOLDING_REGISTERS, mb_start, mb_len)
        # Example: modpoll -m tcp -t 4:float -r 40001 -c 46 192.168.x.x
    
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

        """ Initialize the PMS5003 """
        RX=18
        s2 = pigpio.pi()
        s2.set_mode(RX, pigpio.INPUT)
        s2.bb_serial_read_open(RX, 9600, 8)  

        """ Initialize the SGP30 """
        i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
        s3 = sgp30hc(i2c)
        print("SGP30 serial #", [hex(i) for i in s3.serial])
        s3.iaq_init()
        s3.set_iaq_baseline(0x8895, 0x8a44)
        elapsed_sec = 0

        """ Initialize running average for PM1.0, PM2.5, PM10, RH and VOC """
        pm01_24h = CRR_AVG(24, jfile = "pm01_24h")    # daily average (retained)
        pm01_60m = CRR_AVG(60, pm01_24h)              # hourly average 
        pm01_60s = CRR_AVG(60, pm01_60m)              # minutely average
        co2e_24h = CRR_AVG(24, jfile = "co2e_24h")    # daily average (retained)
        co2e_60m = CRR_AVG(60, co2e_24h)              # hourly average 
        co2e_60s = CRR_AVG(60, co2e_60m)              # minutely average
        tvoc_24h = CRR_AVG(24, jfile = "tvoc_24h")    # daily average (retained)
        tvoc_60m = CRR_AVG(60, tvoc_24h)              # hourly average 
        tvoc_60s = CRR_AVG(60, tvoc_60m)              # minutely average

        """ Initialize AQI object """ 
        aqi = AQI()   
        iaq = IAQ()   

        print("Ready")

        while True:
            """
            40001   Quality Control (3.14159265359)            
            """
            mb_set(40001, pi)                                      

            """ Poll the BME680 """
            if s1.get_sensor_data():
                RH = s1.data.humidity
                wx = WX(T(s1.data.temperature), P(100.0*s1.data.pressure), RH)
                iaq.rh(RH)                        

                """
                40003   Temperature (C)
                40005   Temperature (F)
                40007   Pressure (hPa)
                40009   Pressure (inHg)
                40011   Relative Humidity (%)  
                40013   VOC (kOhm)
                """               
                mb_set(40003, wx.t.C)                                
                mb_set(40005, wx.t.F)                                
                mb_set(40007, wx.p.hPa)                              
                mb_set(40009, wx.p.inHg)                             
                mb_set(40011, wx.RH)

                """
                40039   Dewpoint (C)
                40041   Dewpoint (F)
                40043   Partial pressure water vapor (hPa)
                40045   Partial pressure dry air (hPa)
                40047   Air density (kg/m3)
                40049   Air density (lb/ft3)
                """
                mb_set(40039, wx.td.C)                               
                mb_set(40041, wx.td.F)                              
                mb_set(40043, wx.Pv.hPa)                             
                mb_set(40045, wx.Pd.hPa)                             
                mb_set(40047, wx.Rho.kgperm3)                        
                mb_set(40049, wx.Rho.lbperft3)    
                
                if s1.data.heat_stable:
                    VOC = s1.data.gas_resistance/1000.0
                    mb_set(40013, VOC)    
                    iaq.voc(VOC)

                    """
                    40091   VOC contribution to IAQ
                    40093   VOC 60 second average (kOhm)
                    40095   VOC 60 minute average (kOhm)
                    40097   VOC 24 hour average (kOhm)
                    """
                    mb_set(40091, iaq.IAQ_VOC)
                    mb_set(40093, iaq.voc_60s.avg)
                    mb_set(40095, iaq.voc_60m.avg or iaq.voc_60s.avg)
                    mb_set(40097, iaq.voc_24h.avg or iaq.voc_60m.avg or iaq.voc_60s.avg)

                """
                40087   IAQ
                40089   RH contribution to IAQ
                """
                mb_set(40087, iaq.IAQ)
                mb_set(40089, iaq.IAQ_RH)

            """ Retrieve a packet from the PMS5003 """
            (count, data) = s2.bb_serial_read(RX)
            if count == 32 and data[0] == 0x42 and data[1] == 0x4d:
                s = (struct.Struct(">"+"H"*16)).unpack(data)
                pm01_60s.y(float(s[2]))
                aqi.pm25(float(s[3]))
                aqi.pm10(float(s[4]))

                """
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
                """
                for i in range(0,12):                    
                    mb_set(40015 + 2 * i, float(s[i + 2]))

                """
                40051   AQI
                40053   PM25 contribution to AQI
                40055   PM10 contribution to AQI
                """
                mb_set(40051, aqi.AQI)
                mb_set(40053, aqi.AQI_PM25)
                mb_set(40055, aqi.AQI_PM10)
                
                """
                40057   AQI NowCast
                40059   PM25 contribution to AQI NowCast
                40061   PM10 contribution to AQI NowCast
                """
                mb_set(40057, aqi.AQI_NOWCAST)
                mb_set(40059, aqi.AQI_PM25_NOWCAST)
                mb_set(40061, aqi.AQI_PM10_NOWCAST)

                """
                40063   AQI Current
                40065   PM25 contribution to AQI Current
                40067   PM10 contribution to AQI Current
                """
                mb_set(40063, aqi.AQI_CURRENT)              
                mb_set(40065, aqi.AQI_PM25_CURRENT)
                mb_set(40067, aqi.AQI_PM10_CURRENT)

                """
                40069   PM01 60 second average (ug/m3)
                40071   PM01 60 minute average (ug/m3)
                40073   PM01 24 hour average (ug/m3)
                40075   PM25 60 second average (ug/m3)
                40077   PM25 60 minute average (ug/m3)
                40079   PM25 24 hour average (ug/m3)
                40081   PM10 60 second average (ug/m3)
                40083   PM10 60 minute average (ug/m3)
                40085   PM10 24 hour average (ug/m3)
                """
                mb_set(40069, pm01_60s.avg)
                mb_set(40071, pm01_60m.avg or pm01_60s.avg)
                mb_set(40073, pm01_24h.avg or pm01_60m.avg or pm01_60s.avg)
                mb_set(40075, aqi.pm25_60s.avg)
                mb_set(40077, aqi.pm25_60m.avg or aqi.pm25_60s.avg)
                mb_set(40079, aqi.pm25_24h.avg or aqi.pm25_60m.avg or aqi.pm25_60s.avg)
                mb_set(40081, aqi.pm10_60s.avg)
                mb_set(40083, aqi.pm10_60m.avg or aqi.pm10_60s.avg)
                mb_set(40085, aqi.pm10_24h.avg or aqi.pm10_60m.avg or aqi.pm10_60s.avg)

                """
                SGP30 serial # ['0x0', '0x64', '0xef7b']
                40099   CO2 equivalent (ppm)
                40101   VOC (ppb)
                40103   Absolute Humidity (g/m^3)
                40105   CO2 equivalent 60 second average (ppm)
                40107   CO2 equivalent 60 minute average (ppm)
                40109   CO2 equivalent 24 hour average (ppm)
                40111   VOC 60 second average (ppm)
                40113   VOC 60 minute average (ppm)
                40115   VOC 24 hour average (ppm)  
                """
                if (elapsed_sec > 10):
                    elapsed_sec = 0
                    try:
                        s3.set_humidity(wx.t.C, wx.RH)
                        print("**** Baseline values set: co2eq = 0x%x, tvoc = 0x%x"
                            % (s3.baseline_co2eq, s3.baseline_tvoc))
                    except:
                        s3.disable_humidity()
                else:
                    elapsed_sec += 1
                mb_set(40099, s3.co2eq)
                co2e_60s.y(s3.co2eq)
                mb_set(40101, s3.tvoc)
                tvoc_60s.y(s3.tvoc)
                mb_set(40103, s3.AH)
                mb_set(40105, co2e_60s.avg)
                mb_set(40107, co2e_60m.avg or co2e_60s.avg)
                mb_set(40109, co2e_24h.avg or co2e_60m.avg or co2e_60s.avg)
                mb_set(40111, tvoc_60s.avg)
                mb_set(40113, tvoc_60m.avg or tvoc_60s.avg)
                mb_set(40115, tvoc_24h.avg or tvoc_60m.avg or tvoc_60s.avg)
                print("co2eq = %d ppm \t tvoc = %d ppb" % (s3.co2eq, s3.tvoc))

            time.sleep(1)

    finally:
        s2.bb_serial_read_close(RX)
        s2.stop()
        server.stop()
