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
        """CPRSolarForecast instance requires the following parameters:
            energy_site: a string containing the XML for the EnergySite(s) as
                         defined by CPR's API
            un: Basic Auth account username
            pw: Basic Auth account password
            key: Client key provided by CPR
        """
        self.energy_site = energy_site
        self.username = un
        self.password = pw
        self.querystring['key'] = key

    def parse_results(self, output):
        def time_to_utc(t):
            ret = datetime.strptime(t[0:19], '%Y-%m-%dT%H:%M:%S')
            if t[19] == '+':
                ret -= timedelta(hours=int(t[20:22]), minutes=int(t[23:25]))
            elif t[19] == '-':
                ret += timedelta(hours=int(t[20:22]), minutes=int(t[23:25]))
            return ret

        def clean_attrib(d):
            map = {'WindSpeed_MetersPerSecond': int,
                   'AmbientTemperature_DegreesC': int,
                   'PowerAC_kW': float,
                   'GlobalHorizontalIrradiance_WattsPerMeterSquared': int,
                   'StartTime': time_to_utc,
                   'EndTime': time_to_utc}
            for k, v in d.iteritems():
                d[k] = map[k](v)
            return d

        def good_result(root):
            if root[0][0].attrib['Status'] == 'Failure':
                msg = root[0][0][0][0].attrib['Message']
                code = root[0][0][0][0].attrib['StatusCode']
                raise RuntimeError("SolarAnywhere " + code + ': ' + msg)
            else:
                return True

        root = ET.fromstring(output)
        if not good_result(root):
            return False
        result = []
        for period in root[0][0][1]:
            result.append(clean_attrib(period.attrib))

        return result

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
                return self.parse_results(data.content)
            else:
                requestNumber = requestNumber + 1
        return None

    def round_next_minute(self, ts):
        next_min = ts.minute+1
        return ts.replace(minute=next_min,second=0,microsecond=0)

    def get_1_min_forecast(self, utc_start=None, utc_end=None):
        """get_1_min_forecast returns a list of dictionaries. Each dict includes
           the simulation results as predicted by the CPR SolarAnywhere API. Each
           dict will always include a StartTime and EndTime key with values
           as datetime objects with the time in UTC. Note that tzinfo is not set
           for these objects.
           By default, the overall simulation start (utc_start) is now and the
           simulation end (utc_end) is now+30 minutes.
        """
        if utc_start is None:
            utc_start = datetime.utcnow()
        if utc_end is None:
            utc_end = datetime.utcnow() + timedelta(minutes=30)

        start_time = self.round_next_minute(utc_start).isoformat() + "-00:00"
        end_time = self.round_next_minute(utc_end).isoformat() + "-00:00"
        return self.execute(start_time, end_time, 1)

    def get_30_min_forecast(self, utc_start=None, utc_end=None):
        """get_30_min_forecast returns a list of dictionaries. Each dict includes
           the simulation results as predicted by the CPR SolarAnywhere API. Each
           dict will always include a StartTime and EndTime key with values
           as datetime objects with the time in UTC. Note that tzinfo is not set
           for these objects.
           By default, the overall simulation start (utc_start) is now and the
           simulation end (utc_end) is now+1 day.
        """
        if utc_start is None:
            utc_start = datetime.utcnow()
        if utc_end is None:
            utc_end = datetime.utcnow() + timedelta(days=1)

        start_time = self.round_next_minute(utc_start).isoformat() + "-00:00"
        end_time = self.round_next_minute(utc_end).isoformat() + "-00:00"
        return self.execute(start_time, end_time, 30)
