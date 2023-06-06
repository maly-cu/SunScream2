from kivy.lang import Builder
from plyer import gps, notification
from kivy.app import App
from kivy.properties import StringProperty
from kivy.clock import mainthread
from kivy.utils import platform
from kivy.properties import ListProperty
from kivymd.app import MDApp

" _______ TODAY, REVERT TO OLD GPS KV FILE AND ADD THE PLYER NOTIFICATION EXAMPLE IF THEY BOTH WORK, ADD TIMER FUNCTION _______"


kv = '''
BoxLayout:
    orientation: "vertical"
    padding: "5dp"
    size_hint: 1, .45
    pos_hint: {'top': 1}
    spacing: "10dp"                

    AnchorLayout:
        # position of Anchor Layout
        anchor_x: 'center'
        anchor_y: 'top'
        
        size_hint: None, None
        size: "150dp", "150dp"
        pos_hint: {'center_x': .5, 'center_y': .5, 'top': 1}

        canvas.before:
            Color:
                rgba: app.bar_color + [0.3]
            Line:
                width: app.bar_width
                ellipse: (self.x, self.y, self.width, self.height,0,360)

        canvas.after:
            Color:
                rgb: app.bar_color
            Line:
                width: app.bar_width
                ellipse: (self.x, self.y, self.width, self.height, 0, app.set_temp*6)

                # set to celcius (freezing - 0 to boiling - 100). Since circle is 360 degrees,
                # multiply by 3.6 i.e. 360/100 for a range of 100 but since highest temp ever recorded is 51,
                # set my max at 360/60 so multiply by 6

        Label:
            text: app.temp_text

            markup: True
            font_size: "22dp"
            pos_hint: {"center_x":0.5, "center_y":0.5}
            halign: "center"
            color: 0, 0, 0, 1

    ToggleButton:

        background_color: 250/255, 177/255, 109/255, 1
        background_normal: ""
        line_color: 250/255, 177/255, 109/255, 1
        text_color: 1,1,1,1

        text: 'Start' if self.state == 'normal' else 'Stop'
        
        on_state:
            app.start(1000, 0) if self.state == 'down' else \
            app.stop()
'''


class GpsTest(MDApp):

    gps_location = StringProperty()
    gps_status = StringProperty('Click Start to get GPS location updates')

    set_temp = 32
    uvi = 0

    temp_text = f"[b]{set_temp}°C[/b]\n[size=12dp]Location: {gps_location}[/size]\n" \
                f"[size=12dp]Status: {gps_status}[/size]"  # edit text with diff sizes in same label
    bar_width = 10
    bar_color = ListProperty([1, 1, 0])

    def request_android_permissions(self):
        """
        Since API 23, Android requires permission to be requested at runtime.
        This function requests permission and handles the response via a
        callback.
        The request will produce a popup if permissions have not already been
        been granted, otherwise it will do nothing.
        """
        from android.permissions import request_permissions, Permission

        def callback(permissions, results):
            """
            Defines the callback to be fired when runtime permission
            has been granted or denied. This is not strictly required,
            but added for the sake of completeness.
            """
            if all([res for res in results]):
                print("callback. All permissions granted.")
            else:
                print("callback. Some permissions refused.")

        request_permissions([Permission.ACCESS_COARSE_LOCATION,
                             Permission.ACCESS_FINE_LOCATION], callback)
        # # To request permissions without a callback, do:
        # request_permissions([Permission.ACCESS_COARSE_LOCATION,
        #                      Permission.ACCESS_FINE_LOCATION])

    def build(self):
        try:
            gps.configure(on_location=self.on_location,
                          on_status=self.on_status)
        except NotImplementedError:
            import traceback
            traceback.print_exc()
            self.gps_status = 'GPS is not implemented for your platform'

        if platform == "android":
            print("gps.py: Android detected. Requesting permissions")
            self.request_android_permissions()

        return Builder.load_string(kv)

    def start(self, minTime, minDistance):
        gps.start(minTime, minDistance)

    def stop(self):
        gps.stop()

    @mainthread
    def on_location(self, **kwargs):
        # self.gps_location = '\n'.join([
        #     '{}={}'.format(k, v) for k, v in kwargs.items()])
        global gps_location
        gps_location = '\n'.join([
            '{}={}'.format(k, v) for k, v in kwargs.items()])

    @mainthread
    def on_status(self, stype, status):
        # self.gps_status = 'type={}\n{}'.format(stype, status)
        global gps_status
        gps_status = 'type={}\n{}'.format(stype, status)

    def on_pause(self):
        gps.stop()
        return True

    def on_resume(self):
        gps.start(1000, 0)
        pass

if __name__ == '__main__':
    GpsTest().run()