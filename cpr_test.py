from cpr_api_v2 import CPRSolarForecast

userName = "Intwine.Client@intwineconnect.com"
password = "Sol@rCar5"
querykey = "INTW_TEST"

energy_site = """<EnergySite Name="Sample 1-Min Site" Description="Pensacola">
      <Location Latitude="30.51153" Longitude="-87.3305" />
      <PvSystems>
        <PvSystem Albedo_Percent="17" GeneralDerate_Percent="85.00">
          <Inverters>
            <Inverter Count="1" MaxPowerOutputAC_kW="4.470000" EfficiencyRating_Percent="97.000000" />
          </Inverters>
          <PvArrays>
            <PvArray>
              <PvModules>
                <PvModule Count="1" NameplateDCRating_kW="0.22000" PtcRating_kW="0.19760" PowerTemperatureCoefficient_PercentPerDegreeC="0.4"  NominalOperatingCellTemperature_DegreesC="45" />
              </PvModules>
              <ArrayConfiguration Azimuth_Degrees="177.000" Tilt_Degrees="25.000" Tracking="Fixed" TrackingRotationLimit_Degrees="90" ModuleRowCount="1" RelativeRowSpacing="3"  />
              <SolarObstructions>
                <SolarObstruction Azimuth_Degrees="90.000" Elevation_Degrees="33.000"  Opacity_Percent="80"/>
                <SolarObstruction Azimuth_Degrees="120.000" Elevation_Degrees="50.000" />
                <SolarObstruction Azimuth_Degrees="150.000" Elevation_Degrees="22.000" />
                <SolarObstruction Azimuth_Degrees="180.000" Elevation_Degrees="3.000" />
                <SolarObstruction Azimuth_Degrees="210.000" Elevation_Degrees="1.000" />
                <SolarObstruction Azimuth_Degrees="240.000" Elevation_Degrees="2.000" />
                <SolarObstruction Azimuth_Degrees="270.000" Elevation_Degrees="4.000"  Opacity_Percent="70"/>
              </SolarObstructions>
            </PvArray>
          </PvArrays>
        </PvSystem>
      </PvSystems>
    </EnergySite>"""

a = CPRSolarForecast(energy_site, userName, password, querykey)
#print a.get_1_min_forecast()
print a.get_30_min_forecast()
