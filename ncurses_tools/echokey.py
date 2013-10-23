#!/usr/bin/env python

import curses

def echokey(w):
    curses.noecho()
    w.keypad(1)
    curses.cbreak()
    w.addstr(19,20, "value")
    w.addstr(19,40, "name")
    ch=w.getch()
    while (1==1):
        w.addstr(20,20,str(ch))
        w.addstr(20,40,curses.keyname(ch))
        ch = w.getch()
        w.deleteln()


curses.wrapper(echokey)
