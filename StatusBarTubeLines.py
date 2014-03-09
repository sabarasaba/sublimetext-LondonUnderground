from datetime import datetime

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
            self._data = TubeStatus(self._lines).getTubeStatus()

    def displayTubeLines(self, view, async=True):
        self.load_settings()
        if not hasattr(self, '_data') and async:
            self.fetchTubeLines()
        if hasattr(self, '_data') and sublime.active_window():
            sublime.active_window().active_view().set_status(self._STATUS_KEY, self._data)

    def time(self):
        return datetime.now().strftime('%H:%M:%S')

    _STATUS_KEY = "statustubelines"


class TubeStatus():
    """ Class providing tube status service """
    def __init__(self, lines):
        """ Constructor """
        self._url = "http://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20html%20where%20url%3D%22http%3A%2F%2Fwww.tfl.gov.uk%2F%22%20and%20xpath%3D%22%2Fhtml%2Fbody%5B%40class%3D'template-4'%5D%2Fdiv%5B%40id%3D'container'%5D%2Fdiv%5B%40id%3D'supporting-content'%5D%2Fdiv%5B%40id%3D'service-board-ajax'%5D%2Fdiv%5B%40class%3D'service-board-wrapper'%5D%2Ftable%5B%40class%3D'service-board-tbl'%5D%2Ftbody%22%0A&format=json&diagnostics=true&callback="

        def trimmer(e):
            return e.title().strip()

        self._lines = list(map(trimmer, lines.split(',')))

    def getPrettyResult(self, dic):
        result = ""
        x = 0

        for key, value in dic.items():
            result += "{}: {}".format(key, value)
            x += 1

            if (x < len(dic)):
                result += ' | '

        return result

    def getTubeStatus(self):
        """ Returns tube status information in dictionary """
        results = {}

        try:
            root = urllib.request.urlopen(self._url).read().decode("utf-8")
            data = json.loads(root)

            lines = data["query"]["results"]["tbody"]["tr"]

            for x in range(0, len(lines)):
                title = lines[x]["td"][0]["p"].title()

                # Get status of the line
                if ("class" in lines[x]["td"][1]):
                    status = lines[x]["td"][1]["class"].title()
                else:
                    status = lines[x]["td"][1]["div"]["p"].title()

                # Filter the results with the parameters setted in the config file
                if any(title in element for element in self._lines):
                    results[title] = status

        except Exception as e:
            print(e)
        return self.getPrettyResult(results)
