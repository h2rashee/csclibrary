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

def simplePrintw(stdscr):
    mesg = "Just a string"

    (row,col) = stdscr.getmaxyx()
    stdscr.addstr(row/2, (col-len(mesg))/2, mesg)
    stdscr.addstr(row-2, 0, "This screen has " +str(row)+ " rows and " +str(col)+ " columns\n")

    stdscr.addstr("Try resizing window and running it again")
    stdscr.refresh()
    stdscr.getch()

curses.wrapper(simplePrintw)
