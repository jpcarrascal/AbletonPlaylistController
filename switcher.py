#!/usr/bin/env python
#
# midiin_callback.py
#
# Dependencies:
# https://github.com/SpotlightKid/python-rtmidi

"""Show how to receive MIDI input by setting a callback function."""

from __future__ import print_function
import subprocess
import json
import logging
import sys
import time
import rtmidi
import random
from rtmidi.midiutil import open_midiinput
from rtmidi.midiconstants import (NOTE_ON, NOTE_OFF)



log = logging.getLogger('midiin_callback')
logging.basicConfig(level=logging.CRITICAL)

print("--- Loading playlist... ---")
count = 0
with open('playlist.json', 'r') as playlist_file:
    playlist = json.load(playlist_file)
    for key, value in playlist.items():
        for k, v in value.items():
            if(k == "file" and v != ""):
                print(" - ",value["name"])
                count += 1
print("---", count, " songs in the playlist ---")


def songToLoad(index, data):
    for key, value in data.items():
        for k, v in value.items():
            if(k == "PCnumber" and v == index):
                return value
    return 0


class MidiInputHandler(object):
    def __init__(self, port):
        self.port = port
        self._wallclock = time.time()
        self.midiout = rtmidi.MidiOut()
        available_ports = self.midiout.get_ports()
        if available_ports:
            try:
                index = available_ports.index("IAC Driver Bus 1")
            except ValueError:
                index = -1
            print ("IAC driver found: ",index)
            self.midiout.open_port(1)
        else:
            self.midiout.open_virtual_port("A virtual port")

    def __call__(self, event, data=None):
        message, deltatime = event
        self._wallclock += deltatime
#        print("[%s] @%0.6f %r" % (self.port, self._wallclock, message))
        if message[0] == 203:
#            with self.midiout:
            note = 13 # Stop note
            channel = 1
            note_on = [NOTE_ON | channel, note, 100]
            note_off = [NOTE_OFF | channel, note, 0]
            self.midiout.send_message(note_on)
            time.sleep(0.1)
            self.midiout.send_message(note_off)
            time.sleep(0.1)
            print ("Program change received: ",message[1])
            song = songToLoad(message[1],playlist)
            if song == 0 or song["file"] == "":
                print("Nothing to load")
            else:
                print("Loading ",song["name"])
                subprocess.call(['open', song["file"]])

# Prompts user for MIDI input port, unless a valid port number or name
# is given as the first argument on the command line.
# API backend defaults to ALSA on Linux.
midi_device = "Arduino Micro"ß
port = sys.argv[1] if len(sys.argv) > 1 else midi_device

try:
    midiin, port_name = open_midiinput(port)
except (EOFError, KeyboardInterrupt):
    sys.exit()

print("Attaching MIDI input callback handler.")
midiin.set_callback(MidiInputHandler(port_name))

print("Entering main loop. Press Control-C to exit.")
try:
    # Just wait for keyboard interrupt,
    # everything else is handled via the input callback.
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print('')
finally:
    print("Exit.")
    midiin.close_port()
    del midiin
