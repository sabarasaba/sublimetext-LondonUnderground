from datetime import datetime
import xml.etree.ElementTree as et

import sublime
import sublime_plugin
import urllib.request
import urllib.error
import urllib.parse


class StatusBarWeather(sublime_plugin.EventListener):
    def on_activated(self, view):
        self.displayTubeLines(view)

    def load_settings(self):
        settings = sublime.load_settings('StatusBarTubeLines.sublime-settings')
        self._lines = settings.get('lines', 'victoria').upper()
        self._debug = settings.get('debug', False)
        if self._debug:
            print("StatusBarTubeLines | Settings: Lines({0}) Debug({1}) | {2}".format(self._lines, self._debug, self.time()))

    def fetchTubeLines(self):
        if hasattr(self, '_debug') and self._debug:
            print("StatusBarTubeLines | Fetching tube lines data | {0}".format(self.time()))
        if not hasattr(self, '_lines'):
            print("StatusBarTubeLines | Settings not loaded, reload plugin | {0}".format(self.time()))
        else:
            print("fetch actual tube lines data")
            # self._data = Weather(self._code, self._unit).get_weather()

    def displayTubeLines(self, view, async=True):
        self.load_settings()
        if not hasattr(self, '_data') and async:
            self.fetchTubeLines()
        if hasattr(self, '_data') and sublime.active_window():
            sublime.active_window().active_view().set_status(self._STATUS_KEY, self.format_data(self._data, self._format))

    def time(self):
        return datetime.now().strftime('%H:%M:%S')

    def format_data(self, data, format):
        """ Returns tube lines data as formated string """
        for key, data in data.items():
            format = format.replace('[' + key + ']', data)
        if len(data) == 0:
            print("StatusBarTubeLines | Cannot fetch tube lines, check settings")
            format = ""

        format = "StatusBarTubeLines"

        return format

    _STATUS_KEY = "statustubelines"


class Weather():
    """ Class providing weather service """
    def __init__(self, code, unit):
        """ Constructor """
        self._url = "http://weather.yahooapis.com/forecastrss?p={0}&u={1}".format(code, unit)

    def _get_node(self, root, name, node=''):
        """ Retrieves node """
        return root.find(('channel/' + node + '{%s}' + name) % "http://xml.weather.yahoo.com/ns/rss/1.0")

    def get_weather(self):
        """ Returns weather information in dictionary """
        data = {}
        try:
            root = et.fromstring(urllib.request.urlopen(self._url).read())
            weather_data = self._get_node(root, "condition", "item/")
            if weather_data is not None:
                data["Temp"] = weather_data.get('temp')
                data["Text"] = weather_data.get('text')
            weather_data = self._get_node(root, "location")
            if weather_data is not None:
                data["City"] = weather_data.get('city')
                data["Country"] = weather_data.get('country')
            weather_data = self._get_node(root, "units")
            if weather_data is not None:
                if weather_data.get('temperature') == "C":
                    data["Unit"] = u'\N{DEGREE SIGN}C'
                else:
                    data["Unit"] = "F"
            weather_data = self._get_node(root, "astronomy")
            if weather_data is not None:
                data["Sunrise"] = weather_data.get('sunrise')
                data["Sunset"] = weather_data.get('sunset')
            weather_data = self._get_node(root, "atmosphere")
            if weather_data is not None:
                data["Pressure"] = weather_data.get('pressure')
                data["Humidity"] = weather_data.get('humidity')
        except Exception as e:
            pass
        return data
