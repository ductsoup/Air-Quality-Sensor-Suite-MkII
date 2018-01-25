"""

Derived weather variable and utility classes

"""

from math import log
from crr_avg import *

"""

Unit conversion

"""
class T:
    """ 
    Temperature 
    """
    def __init__(self, t):  # in Celsius
        self.C = t
        self.K = t + 273.15     
        self.F = 9.0 * t / 5.0 + 32.0
        self.R = self.F + 459.67

class P:                    
    """ 
    Pressure 
    """
    def __init__(self, p):  # in Pascals
        self.Pa = p
        self.mb = self.hPa = p / 100.0
        self.bar = 0.001 * p
        self.mmHg = 0.75006157584566  * self.hPa
        self.inHg = 0.0295300 * self.hPa
    
class D:                    
    """ 
    Density 
    """
    def __init__(self, d):  # in kg/m3  
        self.kgperm3 = d
        self.lbperft3 = 0.062428 * d 

class WX():
    """
    Reference
    http://andrew.rsmas.miami.edu/bmcnoldy/Humidity.html
    https://www.gribble.org/cycling/air_density.html
    https://www.weather.gov/media/epz/wxcalc/vaporPressure.pdf
    """
    t = None    # temperature (C)
    p = None    # pressure (hPa)
    RH = None   # relative humidity (%)
    rh = None   # relative humidity 
    td = None   # dewpoint temperature 
    Pv = None   # partial pressure saturation vapor (hPa)
    Pd = None   # partial pressure dry air (hPa)
    Rho = None  # air density (kg/m3)
      
    def __init__(self, t, p, RH):
        self.t = t
        self.p = p
        self.RH = RH
        self.rh = RH / 100.0
        self.td = T(243.04*(log(self.rh)+((17.625*t.C)/(243.04+t.C)))/(17.625-log(self.rh)-((17.625*t.C)/(243.04+t.C))))

        # Herman Wobus saturation vapor pressure calculation
        # https://www.gribble.org/cycling/air_density.html
        td = self.td.C
        eso = 6.1078
        c0 = 0.99999683
        c1 = -0.90826951 * 10**-2
        c2 = 0.78736169 * 10**-4
        c3 = -0.61117958 * 10**-6
        c4 = 0.43884187 * 10**-8
        c5 = -0.29883885 * 10**-10
        c6 = 0.21874425 * 10**-12
        c7 = -0.17892321 * 10**-14
        c8 = 0.11112018 * 10**-16
        c9 = -0.30994571 * 10**-19
        p1 = c0 + td * (c1 + td * (c2 + td * (c3 + td * (c4 + td * (c5 + td * (c6 + td * (c7 + td * (c8 + td * (c9)))))))))
        self.Pv = P(100 * eso / p1 ** 8)
        self.Pd = P(100 * (self.p.hPa - self.Pv.hPa))
        Rv = 461.4964 # specific gas constant for water vapor
        Rd = 287.0531 # specific gas constant for dry air
        self.Rho = D(100 * (self.Pd.hPa / (Rd * t.K)) + (self.Pv.hPa / (Rv * t.K)))

class AQI():
    """ 
    Class to calculate the air quality index from PM2.5 and PM10.

    AQI uses PM25 and PM10 24 hour averages. If we don't have that much history just 
    use what's been provided so far as an approximation. 

    Samples are expected at about 1 second intervals. AQI uses 24 hour averages
    so if we don't have that much history just use what's been provided.

    AQI and NowCast results range from 0 to 500 or -1 if not available.

      0 -  50 Good
     51 - 100 Moderate
    101 - 150 Unhealthy for sensitive groups
    151 - 200 Unhealthy
    201 - 300 Very unhealth
    301 - 500 Hazardous
    
    Reference
    https://en.wikipedia.org/wiki/Air_quality_index
    https://en.wikipedia.org/wiki/NowCast_(air_quality_index)
    https://github.com/G6EJD/BME680-Example/blob/master/ESP32_bme680_CC_demo_02.ino
    https://forums.pimoroni.com/t/bme680-air-quality-low/6293/12

    To Do
    http://www.winsen-sensor.com/products/air-quality-detection-module/ze14-o3.html
    """

    AQI_PM25 = -1           # PM25 contribution to AQI
    AQI_PM10 = -1           # PM10 contribution to AQI
    AQI = -1                # Overall AQI
    AQI_PM25_NOWCAST = -1   # PM25 contribution to NowCast
    AQI_PM10_NOWCAST = -1   # PM10 contribution to NowCast
    AQI_NOWCAST = -1        # Overall NowCast
    AQI_PM25_CURRENT = -1   # PM25 contribution to current
    AQI_PM10_CURRENT = -1   # PM10 contribution to current
    AQI_CURRENT = -1        # Overall current

    def __init__(self):
        """ Constructor """
        self._ILOW       = 0                            
        self._IHIGH      = 1
        self._CLOW_PM25  = 2
        self._CHIGH_PM25 = 3
        self._CLOW_PM10  = 4
        self._CHIGH_PM10 = 5
        self._AQI_REF = [
            [   0,  50,   0.0,  12.0,   0,  54 ],
            [  51, 100,  12.1,  35.4,  55, 154 ],
            [ 101, 150,  35.5,  55.4, 155, 254 ],
            [ 151, 200,  55.5, 150.4, 255, 354 ],
            [ 201, 300, 150.5, 250.4, 355, 424 ],
            [ 301, 400, 250.5, 350.4, 425, 504 ], 
            [ 401, 500, 350.5, 500.4, 505, 604 ]
            ]
        self.pm25_24h = CRR_AVG(24, jfile = "pm25_24h")    # daily average (retained)
        self.pm25_60m = CRR_AVG(60, self.pm25_24h)         # hourly average
        self.pm25_60s = CRR_AVG(60, self.pm25_60m)         # minutely average
        self.pm10_24h = CRR_AVG(24, jfile = "pm10_24h") 
        self.pm10_60m = CRR_AVG(60, self.pm10_24h)           
        self.pm10_60s = CRR_AVG(60, self.pm10_60m)

    def _aqi(self, C, _CLOW, _CHIGH):
        """ Calculate the AQI for a given concentration of a pollutant """
        for i in self._AQI_REF:
            if i[_CHIGH] >= C:
                break
        return (i[self._IHIGH] - i[self._ILOW]) * (C - i[_CLOW]) \
            / (i[_CHIGH] - i[_CLOW]) + i[self._ILOW]  

    def _nowcast(self, i, buf):
        """ Calculate the NowCast concentration of a pollutant """
        if len(buf) > 2:
            C = []
            j = (i - 1) % len(buf) #
            for k in range(0, min(12, len(buf))):
                C.append(buf[(j-k) % len(buf)]) 
            w = 1 if sum(C) == 0 else max((min(C) / max(C)), 0.5)
            yn = yd = 0
            for k in range(1, len(C)+1):
                yn += C[k - 1] * pow(w, k - 1)
                yd += pow(w, k - 1)
            return yn / yd
        else:
            return -1

    def pm25(self, C):
        """ Given a new sample update the PM2.5 AQI and NowCast """
        self.pm25_60s.y(C)            
        C24 = min(self.pm25_24h.avg or self.pm25_60m.avg or self.pm25_60s.avg, self._AQI_REF[-1][self._CHIGH_PM25])
        self.AQI_PM25 = self._aqi(C24, self._CLOW_PM25, self._CHIGH_PM25)
        CNOW = self._nowcast(self.pm25_24h.buf_i, self.pm25_24h.buf)
        if CNOW > -1:
            self.AQI_PM25_NOWCAST = self._aqi(CNOW, self._CLOW_PM25, self._CHIGH_PM25)
        C1M = min(self.pm25_60s.avg, self._AQI_REF[-1][self._CHIGH_PM25])
        self.AQI_PM25_CURRENT = self._aqi(C1M, self._CLOW_PM25, self._CHIGH_PM25)
        self._update_aqi()

    def pm10(self, C):
        """ Given a new sample update the PM10 AQI and NowCast """
        self.pm10_60s.y(C)            
        C24 = min(self.pm10_24h.avg or self.pm10_60m.avg or self.pm10_60s.avg, self._AQI_REF[-1][self._CHIGH_PM10])
        self.AQI_PM10 = self._aqi(C24, self._CLOW_PM10, self._CHIGH_PM10)
        CNOW = self._nowcast(self.pm10_24h.buf_i, self.pm10_24h.buf)
        if CNOW > -1:
            self.AQI_PM10_NOWCAST = self._aqi(CNOW, self._CLOW_PM10, self._CHIGH_PM10)
        C1M = min(self.pm10_60s.avg, self._AQI_REF[-1][self._CHIGH_PM10])
        self.AQI_PM10_CURRENT = self._aqi(C1M, self._CLOW_PM10, self._CHIGH_PM10)
        self._update_aqi()

    def _update_aqi(self):
        self.AQI = max(self.AQI_PM25, self.AQI_PM10)
        self.AQI_NOWCAST = max(self.AQI_PM25_NOWCAST, self.AQI_PM10_NOWCAST)
        self.AQI_CURRENT = max(self.AQI_PM25_CURRENT, self.AQI_PM10_CURRENT)

class IAQ():
    """ 
    Calculate the Indoor Air Quality from relative humidity and VOC.

    By convention the baseline relative humidity is fixed at 40%. The VOC baseline uses
    a 24 hour average. If we don't have that much VOC history just use what's been provided 
    so far as an approximation. Samples are expected at about 1 second intervals.

    IAQ results range from 0 (worst) to 100 (best) or -1 if not available.

    Reference
    https://forums.pimoroni.com/t/bme680-air-quality-low/6293/10
    """

    RH0 = 40        # Relative humidity baseline (fixed)
    IAQ_RH = -1     # RH contribution to IAQ
    VOC0 = -1       # VOC baseline (24 hour average)
    IAQ_VOC = -1    # VOC contribution to IAQ 
    IAQ = -1        # Overall IAQ

    def __init__(self):
        """ Constructor """
        self.voc_24h = CRR_AVG(24, jfile = "voc_24h") 
        self.voc_60m = CRR_AVG(60, self.voc_24h) 
        self.voc_60s = CRR_AVG(60, self.voc_60m)

    def rh(self, RH):
        """ Given a new sample update the RH IAQ component """
        self.IAQ_RH = 100 * max((self.RH0 - abs(self.RH0 - RH)) / self.RH0, 0)
        self._update_iaq()
        return self.IAQ_RH

    def voc(self, VOC):
        """ Given a new sample update the VOC IAQ component """
        self.voc_60s.y(VOC)
        self.VOC0 = self.voc_24h.avg or self.voc_60m.avg or self.voc_60s.avg
        self.IAQ_VOC = 100 * max((self.VOC0 - abs(self.VOC0 - VOC)) / self.VOC0, 0)
        self._update_iaq()
        return self.IAQ_VOC

    def _update_iaq(self):
        if self.IAQ_RH != -1 and self.IAQ_VOC != -1:
            self.IAQ = 0.25 * self.IAQ_RH + 0.75 * self.IAQ_VOC        
