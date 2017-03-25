"""This is a Python module that provides an interface to the PrevisionMeteo! Weather

more details from API: http://www.prevision-meteo.ch/services
or API pdf: http://www.prevision-meteo.ch/uploads/pdf/recuperation-donnees-meteo.pdf
"""
import json
import logging
import urllib.error
from urllib.parse import urlencode
from urllib.request import urlopen

_PREVISION_METEO_BASE_URL = "http://www.prevision-meteo.ch/services/json/lat={0}lng={1}"

_LOGGER = logging.getLogger(__name__)

def _pm_query(pos):
    """Fetch data from prevision meteo! Return a dict if successfull or None."""
    url = _PREVISION_METEO_BASE_URL.format(*pos)

    # send request
    _LOGGER.debug("Send request to url: %s", url)
    try:
        request = urlopen(url)
        rawData = request.read()

        # parse jason
        data = json.loads(rawData.decode("utf-8"))

        _LOGGER.debug("Length of query data from prevision meteo: %s", len(str(data)))
        return data #data.get("query", {}).get("results", {})
    except (urllib.error.HTTPError, urllib.error.URLError):
        _LOGGER.info("Can't fetch data from Yahoo!")
    return None


class PrevisionMeteo(object):
    """PrevisionMeteo! API access."""
    def __init__(self, pos, when = None, hour = None):
        """Init Object."""
        self._pos = pos
        self._when = None
        self._hour = None
        self._data = {}
        self.SetForecast(when , hour)

    def SetForecast( self , a , b ):
        """Raw Data."""
        if a is None :
            self._when = "current_condition"
        else:
            self._when = "fcst_day_{0}".format(a)
        
        if b is not None:
            self._hour = "%0dH00" % b
        else:
            self._hour = None
   
    def updateWeather(self):
        """Fetch weather data from Yahoo! True if success."""
        # send request
        tmpData = _pm_query(self._pos)

        # data exists
        if tmpData is not None and "current_condition" in tmpData:
            self._data = tmpData
            return True

        _LOGGER.error("Fetch no weather data Yahoo!")
        self._data = {}
        return False

    @property
    def RawData(self):
        """Raw Data."""
        return self._data

    @property
    def Condition(self):
        """Current weather data."""
        if self._hour  is None:
            return self._data.get(self._when, {}).get("condition", None)
        else:
            return self._data.get(self._when, {}).get("hourly_data", {}).get(self._hour, {}).get("CONDITION", None)

    @property
    def Temp(self):
        """Current weather data."""
        if self._hour  is None:
            return self._data.get(self._when, {}).get("tmp", None)
        else:
            return self._data.get(self._when, {}).get("hourly_data", {}).get(self._hour, {}).get("TMP2m", None)

    @property
    def Date(self):
        """Current weather data."""
        return self._data.get(self._when, {}).get("date", None)
        
    @property
    def Hour(self):
        """Current weather data."""
        if self._hour  is None:
            return self._data.get(self._when, {}).get("hour", None)
        else:
            return self._hour

    @property
    def Temp_max(self):
        """Current weather data."""
        value = self._data.get(self._when, {}).get("tmax", None)
        #else, return temperature of current day
        if value is None:
            value = self._data.get("fcst_day_0", {}).get("tmax",None)
        return value

    @property
    def Temp_min(self):
        """Current weather data."""
        value = self._data.get(self._when, {}).get("tmin", None)
        #else, return temperature of current day
        if value is None:
            value = self._data.get("fcst_day_0", {}).get("tmin",None)
        return value

    @property
    def Wind(self):
        """Wind weather data."""
        value = self._data.get(self._when, {}).get("hourly_data", {}).get(self._hour, {}).get("WNDSPD10m", None)
        if value is None:
            value = self._data.get(self._when, {}).get("wnd_spd", None)
        return value

    @property
    def Wind_dir(self):
        """Wind weather data."""
        value = self._data.get(self._when, {}).get("hourly_data", {}).get(self._hour, {}).get("WNDDIRCARD10", None)
        if value is None:
            value = self._data.get(self._when, {}).get("wnd_dir", None)
        return value
