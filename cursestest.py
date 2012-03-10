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

def menutest(stdscr, l):
    curses.curs_set(0)
    (rows,cols)=stdscr.getmaxyx()
    w = curses.newwin(10,40,(rows-10)/2, (cols-40)/2)
    w.keypad(1)
    i=0
    for mitem in l:
        w.addstr(i,0,mitem)
        i+=1

    highlight=0
    w.chgat(highlight,0, curses.A_REVERSE)
    w.refresh()
    ch=w.getch()
    while (ch!=113): # leave on q
        if ch==curses.KEY_UP:
            if highlight!=0:
                w.chgat(highlight,0, 0)
                highlight -= 1
                w.chgat(highlight,0, curses.A_REVERSE)
        if ch==curses.KEY_DOWN:
            if highlight!=len(l)-1:
                w.chgat(highlight,0, 0)
                highlight += 1
                w.chgat(highlight,0, curses.A_REVERSE)
        w.refresh()
        ch = w.getch()
    
    curses.curs_set(1)


menu = ["item 1", "poo", "add book/article/stuff", "update", "remove"]
curses.wrapper(menutest, menu)
