#!/usr/bin/env python

import curses

def menutest(stdscr, l):
    curses.curs_set(0)
    (rows,cols)=stdscr.getmaxyx()
    w = curses.newwin(10,40,(rows-10)/2, (cols-40)/2)

    menu(w, l)
    
    curses.curs_set(1)

# item is a list of (string, callable) tuples
def menu(w, items):
    w.keypad(1)
    highlight=0
    for (mitem,fun) in items:
        w.addstr(highlight,0, mitem)
        highlight +=1

    highlight=0
    w.chgat(highlight, 0, curses.A_REVERSE)
    w.refresh()
    ch=w.getch()
    while (ch!=113): # leave on q
        if ch==curses.KEY_UP:
            if highlight!=0:
                w.chgat(highlight,0, 0)
                highlight -= 1
                w.chgat(highlight,0, curses.A_REVERSE)
        if ch==curses.KEY_DOWN:
            if highlight!=len(items)-1:
                w.chgat(highlight,0, 0)
                highlight += 1
                w.chgat(highlight,0, curses.A_REVERSE)
        if ch==114 or ch==10:
            (s,f)=items[highlight]
            win=curses.newwin(1,40,10,10)
            f(win)
        w.refresh()
        ch = w.getch()

def poo(w):
    w.addstr("POOOOOOOO!")
    w.refresh()

def other(w):
    w.addstr("I am not poo")
    w.refresh()

m = [("item 1", other),
     ("poo", poo),
     ("add book/article/stuff", other),
     ("update", other),
     ("remove", other)]
curses.wrapper(menutest, m)
