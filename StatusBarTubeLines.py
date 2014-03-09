from datetime import datetime
import xml.etree.ElementTree as et

import sublime
import sublime_plugin
import urllib.request
import urllib.error
import urllib.parse
import json


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
            # self._data = TubeStatus().getTubeStatus()
            TubeStatus(self._lines).getTubeStatus()

    def displayTubeLines(self, view, async=True):
        self.load_settings()
        if not hasattr(self, '_data') and async:
            self.fetchTubeLines()
        # if hasattr(self, '_data') and sublime.active_window():
            # sublime.active_window().active_view().set_status(self._STATUS_KEY, self.format_data(self._data, self._format))

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


class TubeStatus():
    """ Class providing weather service """
    def __init__(self, lines):
        """ Constructor """
        self._url = "http://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20html%20where%20url%3D%22http%3A%2F%2Fwww.tfl.gov.uk%2F%22%20and%20xpath%3D%22%2Fhtml%2Fbody%5B%40class%3D'template-4'%5D%2Fdiv%5B%40id%3D'container'%5D%2Fdiv%5B%40id%3D'supporting-content'%5D%2Fdiv%5B%40id%3D'service-board-ajax'%5D%2Fdiv%5B%40class%3D'service-board-wrapper'%5D%2Ftable%5B%40class%3D'service-board-tbl'%5D%2Ftbody%22%0A&format=json&diagnostics=true&callback="

    def _get_node(self, root, name, node=''):
        """ Retrieves node """
        return root.find(('channel/' + node + '{%s}' + name) % "http://xml.weather.yahoo.com/ns/rss/1.0")

    def getTubeStatus(self):
        """ Returns weather information in dictionary """
        data = {}

        try:
            root = urllib.request.urlopen(self._url).read().decode("utf-8")
            data = json.loads(root)

            lines = data["query"]["results"]["tbody"]["tr"]

            # print(len(lines))
            for x in range(0, len(lines)):
                print(lines[x]["td"][0]["class"].title())

                if ("class" in lines[x]["td"][1]):
                    print(lines[x]["td"][1]["class"])
                else:
                    print(lines[x]["td"][1]["div"]["p"])

            # for key, value in dict.items(lines):
            #     print(key, value)


            # weather_data = self._get_node(root, "condition", "item/")
            # if weather_data is not None:
            #     data["Temp"] = weather_data.get('temp')
            #     data["Text"] = weather_data.get('text')
            # weather_data = self._get_node(root, "location")
            # if weather_data is not None:
            #     data["City"] = weather_data.get('city')
            #     data["Country"] = weather_data.get('country')
            # weather_data = self._get_node(root, "units")
            # if weather_data is not None:
            #     if weather_data.get('temperature') == "C":
            #         data["Unit"] = u'\N{DEGREE SIGN}C'
            #     else:
            #         data["Unit"] = "F"
            # weather_data = self._get_node(root, "astronomy")
            # if weather_data is not None:
            #     data["Sunrise"] = weather_data.get('sunrise')
            #     data["Sunset"] = weather_data.get('sunset')
            # weather_data = self._get_node(root, "atmosphere")
            # if weather_data is not None:
            #     data["Pressure"] = weather_data.get('pressure')
            #     data["Humidity"] = weather_data.get('humidity')
        except Exception as e:
            print(e)
        return data
