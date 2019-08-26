import logging
import platform
import sys
import threading
import subprocess
import time

import aiy.assistant.auth_helpers
from aiy.assistant.library import Assistant
import aiy.voicehat
from google.assistant.library.event import EventType

from emailer import email
from creds import email_user, email_password

from picamera import PiCamera

camera = PiCamera()

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
)


class MyAssistant(object):
    """An assistant that runs in the background.

    The Google Assistant Library event loop blocks the running thread entirely.
    To support the button trigger, we need to run the event loop in a separate
    thread. Otherwise, the on_button_pressed() method will never get a chance to
    be invoked.
    """

    def __init__(self):
        self._task = threading.Thread(target=self._run_task)
        self._can_start_conversation = False
        self._assistant = None

    def start(self):
        """Starts the assistant.

        Starts the assistant event loop and begin processing events.
        """
        self._task.start()

    def _run_task(self):
        credentials = aiy.assistant.auth_helpers.get_assistant_credentials()
        with Assistant(credentials) as assistant:
            self._assistant = assistant
            for event in assistant.start():
                self._process_event(event)

    def _power_off_pi(self):
        aiy.audio.say('Good bye!')
        subprocess.call('sudo shutdown now', shell=True)

    def _reboot_pi(self):
        aiy.audio.say('See you in a bit!')
        subprocess.call('sudo reboot', shell=True)

    def _say_ip(self):
        ip_address = subprocess.check_output("hostname -I | cut -d' ' -f1", shell=True)
        aiy.audio.say('My IP address is %s' % ip_address.decode('utf-8'))

    def _email_picture(self):
        aiy.audio.say('Sure I can take a picture for you')
        self._take_picture()
        email('Here is the picture you asked for:', 'Took Picture', email_user, email_password, 'rishavb123@gmail.com', files=['/home/pi/Desktop/image.jpg'])
        aiy.audio.say("I emailed the picture to you")

    def _take_picture(self):
        for i in range(3, 0, -1):
            aiy.audio.say(str(i))
            time.sleep(1)
        camera.capture('/home/pi/Desktop/image.jpg')

    def _process_event(self, event):
        status_ui = aiy.voicehat.get_status_ui()
        if event.type == EventType.ON_START_FINISHED:
            status_ui.status('ready')
            self._can_start_conversation = True
            # Start the voicehat button trigger.
            aiy.voicehat.get_button().on_press(self._on_button_pressed)
            if sys.stdout.isatty():
                print('Say "OK, Google" or press the button, then speak. '
                      'Press Ctrl+C to quit...')

        elif event.type == EventType.ON_CONVERSATION_TURN_STARTED:
            self._can_start_conversation = False
            status_ui.status('listening')

        elif event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED and event.args:
            print('You said:', event.args['text'])
            text = event.args['text'].lower()
            if text == 'power off':
                self._assistant.stop_conversation()
                self._power_off_pi()
            elif text == 'reboot':
                self._assistant.stop_conversation()
                self._reboot_pi()
            elif text == 'ip address':
                self._assistant.stop_conversation()
                self._say_ip()
            elif text == 'take a picture':
                self._assistant.stop_conversation()
                self._email_picture()

        elif event.type == EventType.ON_END_OF_UTTERANCE:
            status_ui.status('thinking')

        elif (event.type == EventType.ON_CONVERSATION_TURN_FINISHED
              or event.type == EventType.ON_CONVERSATION_TURN_TIMEOUT
              or event.type == EventType.ON_NO_RESPONSE):
            status_ui.status('ready')
            self._can_start_conversation = True

        elif event.type == EventType.ON_ASSISTANT_ERROR and event.args and event.args['is_fatal']:
            sys.exit(1)

    def _on_button_pressed(self):
        # Check if we can start a conversation. 'self._can_start_conversation'
        # is False when either:
        # 1. The assistant library is not yet ready; OR
        # 2. The assistant library is already in a conversation.
        if self._can_start_conversation:
            self._assistant.start_conversation()


def main():
    if platform.machine() == 'armv6l':
        print('Cannot run hotword demo on Pi Zero!')
        exit(-1)
    MyAssistant().start()


if __name__ == '__main__':
    main()
