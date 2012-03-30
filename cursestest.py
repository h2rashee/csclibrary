#!/usr/bin/env python

import curses

def windowLayout(stdscr):
    w = curses.newwin(5,10,10,10)
    w.box()
    w.refresh()
    w.getch()
    w2 = w.derwin(2,7,2,2)
    w2.box()
    w2.refresh()
    w2.getch()

curses.wrapper(windowLayout)
