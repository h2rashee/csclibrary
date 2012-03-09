#!/usr/bin/env python

import curses


def showBold(stdscr):
    stdscr.addstr("Type any character to see it in bold\n")
    ch = stdscr.getch()

    if (ch==curses.KEY_F1):
        stdscr.addstr("F1 Key pressed")

    else:
        stdscr.addstr("The key pressed is ")
        stdscr.addch(ch, curses.A_BOLD)

        stdscr.refresh()
        stdscr.getch()

curses.wrapper(showBold)
