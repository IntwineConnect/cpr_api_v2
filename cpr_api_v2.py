########################################################################
# Copyright (c) 2017, Intwine Connect, LLC.                            #
# This file is licensed under the BSD-3-Clause                         #
# See LICENSE for complete text                                        #
########################################################################

import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET
import time
from datetime import datetime, timedelta

DEBUG = False


class CPRSolarForecast:
    url = "https://service.solaranywhere.com/api/v2/Simulation"
    url2 = "https://service.solaranywhere.com/api/v2/SimulationResult/"

    headers = {'content-type': "text/xml; charset=utf-8",
               'content-length': "length"
              }
    payload = """<CreateSimulationRequest xmlns="http://service.solaranywhere.com/api/v2"><EnergySites>{}</EnergySites><SimulationOptions PowerModel="CprPVForm" ShadingModel="ShadeSimulator" OutputFields="StartTime,EndTime,PowerAC_kW,GlobalHorizontalIrradiance_WattsPerMeterSquared,AmbientTemperature_DegreesC,WindSpeed_MetersPerSecond"><WeatherDataOptions WeatherDataSource="SolarAnywhere3_2" WeatherDataPreference = "Auto" PerformTimeShifting = "false" StartTime="{}" EndTime="{}" SpatialResolution_Degrees="0.01" TimeResolution_Minutes="{}"/></SimulationOptions></CreateSimulationRequest>"""
    energy_site = None

    # Auth parameters
    username = None
    password = None
    querystring = {'key': None}

    def __init__(self, energy_site, un, pw, key):
        self.energy_site = energy_site
        self.username = un
        self.password = pw
        self.querystring['key'] = key

    def send_query(self, ts, te, dt):
        payload = self.payload.format(self.energy_site, ts, te, dt)
        response = requests.post(self.url,
                                 auth=HTTPBasicAuth(self.username, self.password),
                                 data=payload,
                                 headers=self.headers,
                                 params=self.querystring)
        if not response.ok:
            raise(requests.HTTPError(response.status_code, response.reason))

        root = ET.fromstring(response.content)
        return root.attrib.get("SimulationId")

    def execute(self, ts, te, dt):
        publicId = self.send_query(ts, te, dt)
        if DEBUG: print publicId
        requestNumber = 0
        MAX_requestNumber = 100

        while (requestNumber < MAX_requestNumber):
            time.sleep(5)
            data = requests.get(self.url2 + publicId,
                                auth=HTTPBasicAuth(self.username, self.password))
            if not data.ok:
                raise (requests.HTTPError(data.status_code, data.reason))

            radicle = ET.fromstring(data.content)
            status = radicle.attrib.get("Status")
            if DEBUG: print(status)
            if status == "Done":
                if DEBUG: print data.content
                return data.content
            else:
                requestNumber = requestNumber + 1
        return None

    def get_1_min_forecast(self, utc_start=datetime.utcnow(), utc_end=datetime.utcnow() + timedelta(minutes=30)):
        start_time = utc_start.replace(microsecond=0).isoformat() + "-00:00"
        end_time = utc_end.replace(microsecond=0).isoformat() + "-00:00"
        return self.execute(start_time, end_time, 1)

    def get_30_min_forecast(self, utc_start=datetime.utcnow(), utc_end=datetime.utcnow() + timedelta(days=1)):
        start_time = utc_start.replace(microsecond=0).isoformat() + "-00:00"
        end_time = utc_end.replace(microsecond=0).isoformat() + "-00:00"
        return self.execute(start_time, end_time, 30)
