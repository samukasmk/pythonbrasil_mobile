'''Screen Schedule
'''

from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.factory import Factory
import datetime
from kivy.properties import ObjectProperty
from uix.tabbedcarousel import TabbedCarousel
import datetime
app = App.get_running_app()


class TalkInfo(Factory.TouchRippleBehavior, Factory.ButtonBehavior, Factory.BoxLayout):
    '''
    '''

    talk = ObjectProperty(None)

    Builder.load_string('''
<TalkInfo>
    canvas.before:
        Color:
            rgba: (.5, .5, .5, .2) if root.parent and root.parent.children.index(self)%2 == 0 else (.3, .3, .3, .2)
        Rectangle:
            size: self.size
            pos: self.pos
    size_hint_y: None
    height: dp(40)
    spacing: dp(9)
    LeftAlignedLabel:
        size_hint_x: None
        width: dp(45)
        text: "{}\\n{}".format(root.talk['start_time'], root.talk['end_time'])
    LeftAlignedLabel:
        valign: 'middle'
        text: root.talk['title']
''')




class ScreenSchedule(Screen):
    '''
    Screen to display the schedule as per schedule.json generated by
    pydelhiconf.network every time the app is started. A default
    schedule is provided.
    '''

    Builder.load_string('''
<Topic@Label>
    canvas.before:
        Color
            rgba: app.base_active_color
        Rectangle
            size: self.width, self.height
            pos: self.right - self.width  , self.y + dp(5)
        Color
            rgba: app.base_active_color[:3]+[.5]
        Rectangle
            size: self.width, self.height
            pos: self.right - self.width - dp(5), self.y
        Color
            rgba: 0, 0, 0, .5
        Rectangle
            texture: self.texture
            size: self.width - dp(50), self.height
            pos: self.x + dp(28), self.y - dp(3)
    font_size: dp(27)
    text_size: self.width - dp(50), self.height
    size_hint: None, None
    width: dp(300)
    height: dp(45)
    halign: 'right'
    valign: 'middle'
    pos_hint: {'right': 1}

<AccordionItemTitle>
    text_size: self.width - dp(10), self.height
    halign: 'left'
    valign: 'middle'

<AccordionItem>
    back_color: app.base_inactive_light
    canvas.before:
        Color
            rgba: root.back_color or (1, 1, 1, 1)
        Rectangle
            size: dp(270), dp(32)
            pos: self.x, self.top - dp(40)
        Color
            rgba: (list(root.back_color[:3])+[.3]) if root.back_color else (1, 1, 1, 1)
        Rectangle
            size: dp(270), dp(32)
            pos: self.x + dp(5), self.top - (dp(40) + dp(5)) 

<Header@LeftAlignedLabel>
    size_hint_y: None
    height: dp(27)
    width: dp(40)
    size_hint: None, 1
    background_color: app.base_active_color[:3] + [.3]
    canvas.before:
        Color
            rgba: root.background_color if root.background_color else (1, 1, 1, 1)
        Rectangle
            size: self.size
            pos: self.pos
    
   
<ScreenSchedule>
    name: 'ScreenSchedule'
    BoxLayout
        # spacing: dp(20)
        orientation: 'vertical'
        padding: dp(4)
        Topic
            text: app.event_name
        Accordion
            id: accordian_days
            orientation: 'vertical'

<TalkTitle@BoxLayout>
    spacing: dp(9)   
    height: dp(30)
    size_hint_y: None
    Header
        size_hint: None,None
        text: 'Time'
    Header
        text: 'Ttile'

<TabbedCarousel>
    background_color: 1, 1, 1, 0

<TabbedPanelHeader>
    background_color: (1, 1, 1, 1) if self.state == 'down' else app.base_active_color
    background_normal: 'atlas://data/default/but_overlay'
    background_down: 'atlas://data/default/but_overlay'

<Track@Screen>
    ScrollView
        GridLayout
            id: container
            cols: 1
            size_hint_y: None
            padding: '15dp'
            spacing: '2dp'
            height: self.minimum_height
 ''')

    def on_enter(self, onsuccess=False):
        '''Series of actions to be performed when Schedule screen is entered
        '''
        self.ids.accordian_days.clear_widgets()
        from network import get_data

        # this should update the file on disk
        events = get_data('event', onsuccess=onsuccess).get('0.0.1')
        schedule = get_data('schedule', onsuccess=onsuccess).get('0.0.1')[0]

        # take first event as the one to display schedule for.
        event = events[0]
        app.event_name = event['name']
        app.venue_name = event['venue']
        start_date = event['start_date']
        end_date = event['end_date']
        
        dates = schedule.keys()[1:]
        # each day could have multiple tracks
        tracks = schedule['tracks']
        dates = sorted(
            dates,
            key=lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'))

        # perf optims, minimize dot lookups
        acordion_add = self.ids.accordian_days.add_widget
        AccordionItem = Factory.AccordionItem
        Track = Factory.Track

        first = None
        for date in dates:
            # add current day as accordion widget
            cday = AccordionItem(title=date)
            if not first: first = cday
            acordion_add(cday)
            sched = schedule[date]
            # create a carousel for each track
            tcarousel = TabbedCarousel()
            
            # this carousel would show each track as new tab
            trackscreens = []
            for track in tracks:
                trk = Track(name=track)
                trackscreens.append(trk)
                # add track to carousel
                tcarousel.add_widget(trk)
            
            items = len(sched)
            for i in xrange(items):
                talk = sched[i]
                tid = talk['track']
                if tid.lower() == 'all':
                    for tlk in trackscreens:
                        ti = TalkInfo(talk=talk)
                        tlk.ids.container.add_widget(ti)
                    continue
                ti = TalkInfo(talk=talk)
                trackscreens[int(tid)-1].ids.container.add_widget(ti)

            cday.add_widget(tcarousel)
            self.ids.accordian_days.select(first)


    def load_screentalk(self, instance):
        ldscr = app.load_screen('ScreenTalks', manager=app.navigation_manager)
        ldscr.talkid = self.talkid