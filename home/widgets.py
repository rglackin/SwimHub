from django import forms
from datetime import timedelta

class MicrosecondWidget(forms.widgets.Widget):
    def render(self, name, value, attrs=None, renderer=None):
        # Convert the value (a string of microseconds) to minutes, seconds, and milliseconds
        value = (  value)
        secs , microseconds = value.seconds, value.microseconds
        mins = secs//60
        secs = secs-(mins*60)
        millisecs  = microseconds/1000
        # Format the value as "minutes:seconds:milliseconds"
        value = '{:02d}:{:02d}:{:03d}'.format(mins, secs, millisecs)
        # Return the rendered widget as a string
        return super().render(name, value, attrs, renderer)


def format_time(time):
        secs , microseconds = time.seconds, time.microseconds
        mins = secs//60
        secs = secs-(mins*60)
        millisecs  = microseconds/1000
        return "{:02}:{:02}:{:03}".format(int(mins),int(secs),int(millisecs))