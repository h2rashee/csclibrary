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
            f()
        w.refresh()
        ch = w.getch()

# items is a list of (label, value) pairs
def drawForm(w, title, items, highlight):
    w.addstr(1,1,title)
    r=3;
    m=0;
    for l, v in items:
        m = max(len(l),m)
    m+=3
    for l, v in items:
        c = m-len(l)-2
        w.addstr(r,c,l+":")
        w.addstr(r,m,v)
        r+=2
    return m


def addMenu():
    formdata = [("ISBN","112733"),
                ("Title", "Poo"),
                ("Author","")]
    w=curses.newwin(10,50,10,10)
    (y,x)=w.getmaxyx()
    w.border()
    w.keypad(1)
    curses.curs_set(1)
    highlight=0
    r=3
    m = drawForm(w,"Add a Book", formdata, highlight)
    w.chgat(r,m,x-m-2,curses.A_UNDERLINE)
    w.move(r,m+len(formdata[highlight][1]))
    ch = w.getch()
    while (ch!=113):
        if ch==curses.KEY_UP:
            if highlight!=0:
                w.chgat(r,m,x-m-2,curses.A_NORMAL)
                highlight -= 1
                r=3+2*highlight
                w.chgat(r,m,x-m-2,curses.A_UNDERLINE)
                w.move(r,m+len(formdata[highlight][1]))
        if ch==curses.KEY_DOWN:
            if highlight != len(formdata) -1:
                w.chgat(r,m,x-m-2,curses.A_NORMAL)
                highlight += 1
                r=3+2*highlight
                w.chgat(r,m,x-m-2,curses.A_UNDERLINE)
                w.move(r,m+len(formdata[highlight][1]))
        w.refresh()
        ch = w.getch()

    curses.curs_set(0)
    w.refresh()

def updateMenu():
    w=curses.newwin(1,50,10,10)
    w.addstr("I will be used to update or modify book records")
    w.refresh()

def deleteMenu():
    w=curses.newwin(1,50,10,10)
    w.addstr("I will be used to delete book records")
    w.refresh()

def browseMenu():
    w=curses.newwin(1,50,10,10)
    w.addstr("I will be used to browse book records")
    w.refresh()

m = [("Browse Library", browseMenu),
     ("Add Book or other item", addMenu),
     ("Modify/Update record", updateMenu),
     ("Remove book from catalogue", deleteMenu)]
curses.wrapper(menutest, m)
