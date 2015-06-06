#!/usr/bin/python
# -*- coding: utf-8 -*-

from ScrolledText import ScrolledText
from Tkinter import *
from os import walk

BYTES_STATS_TEXT =  '  ____        _              _____ _        _       \n'
BYTES_STATS_TEXT += ' |  _ \      | |            / ____| |      | |      \n'
BYTES_STATS_TEXT += ' | |_) |_   _| |_ ___ ___  | (___ | |_ __ _| |_ ___ \n'
BYTES_STATS_TEXT += ' |  _ <| | | | __/ _ / __|  \___ \| __/ _` | __/ __|\n'
BYTES_STATS_TEXT += ' | |_) | |_| | ||  __\__ \  ____) | || (_| | |_\__ \\\n'
BYTES_STATS_TEXT += ' |____/ \__, |\__\___|___/ |_____/ \__\__,_|\__|___/\n'
BYTES_STATS_TEXT += '         __/ |                                      \n'
BYTES_STATS_TEXT += '        |___/                                      \n\n'
PACKETS_STATS_TEXT  = '  _____           _        _          _____ _        _       \n'
PACKETS_STATS_TEXT += ' |  __ \         | |      | |        / ____| |      | |      \n'
PACKETS_STATS_TEXT += ' | |__) __ _  ___| | _____| |_ ___  | (___ | |_ __ _| |_ ___ \n'
PACKETS_STATS_TEXT += ' |  ___/ _` |/ __| |/ / _ | __/ __|  \___ \| __/ _` | __/ __|\n'
PACKETS_STATS_TEXT += ' | |  | (_| | (__|   |  __| |_\__ \  ____) | || (_| | |_\__ \\\n'
PACKETS_STATS_TEXT += ' |_|   \__,_|\___|_|\_\___|\__|___/ |_____/ \__\__,_|\__|___/\n'
PACKETS_STATS_TEXT += '                                                             \n\n'

def task():
    first, last = s.yview()
    s.delete(1.0, 'end')
    quote = BYTES_STATS_TEXT
    for (dirpath, dirnames, filenames) in walk(path+'bytes_stats/'):
        for filename in filenames:
            if filename[0:3] == 'dp_':
                f = open(path+'bytes_stats/'+filename)
                quote += f.read() + '\n'
    quote += PACKETS_STATS_TEXT
    for (dirpath, dirnames, filenames) in walk(path+'packets_stats/'):
        for filename in filenames:
            if filename[0:3] == 'dp_':
                f = open(path+'packets_stats/'+filename)
                quote += f.read() + '\n'
    s.insert('end', quote)
    s.yview_moveto(first)
    root.after(1000,task)

root = Tk()
s=ScrolledText(root, width=140, height=40)
s.pack(fill='both', expand=1)
path = "/home/user/workspace/dreamer-ryu/ryu/app/port_stats/"
root.title("Traffic Monitor GUI")
root.after(1000,task)
root.mainloop()
