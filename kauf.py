
import requests


class Light:
    def __init__(self, host):
        self.host = host

    @property
    def url(self):
        return f'http://{self.host}/light/kauf_bulb/'

    def turn_off(self, transition=0):
        requests.post(self.url + f'turn_off?transition={transition}')

    def turn_on(self, **kwargs):
        '''
        from https://esphome.io/web-api/index.html#light
        brightness: The brightness of the light, from 0 to 255.

        r: The red color channel of the light, from 0 to 255.
        g: The green color channel of the light, from 0 to 255.
        b: The blue color channel of the light, from 0 to 255.
        white_value: The white channel of RGBW lights, from 0 to 255.

        flash: Flash the color provided by the other properties for a duration
                in seconds.
        transition: Transition to the specified color values in this duration
                in seconds.
        effect: Set an effect for the light. (Doesn't appear any are available)
        '''

        requests.post(self.url + 'turn_on', params=kwargs)
