#!/usr/bin/env python

import curses
import dbLayer as db
import browser
import bookForm
import bookData

stdscr=0

def menutest(s, l):
    global stdscr
    stdscr=s
    curses.curs_set(0)
    (rows,cols)=stdscr.getmaxyx()
    w = curses.newwin(10,40,(rows-10)/2, (cols-40)/2)

    menu(w, l)
    
    curses.curs_set(1)

# item is a list of (string, callable) tuples
def menu(w, items):
    w.keypad(1)
    highlight=0
    redrawMenu(w,items,highlight)

    w.refresh()
    ch=w.getch()
    while (ch!=113 and ch!=27): # leave on q or ESC
        if ch==curses.KEY_UP:
            if highlight!=0:
                w.chgat(highlight,0, 0)
                highlight -= 1
                while(items[highlight][0]==""):
                    highlight -=1
                w.chgat(highlight,0, curses.A_REVERSE)
        if ch==curses.KEY_DOWN:
            if highlight!=len(items)-1:
                w.chgat(highlight,0, 0)
                highlight += 1
                while(items[highlight][0]==""):
                    highlight +=1
                w.chgat(highlight,0, curses.A_REVERSE)
        if ch==curses.KEY_PPAGE:
            w.chgat(highlight,0, 0)
            highlight = 0
            w.chgat(highlight,0, curses.A_REVERSE)
        if ch==curses.KEY_NPAGE:
            w.chgat(highlight,0, 0)
            highlight = len(items)-1
            w.chgat(highlight,0, curses.A_REVERSE)
        if ch==114 or ch==10:
            (s,f)=items[highlight]
            f()
            redrawMenu(w,items,highlight)
        w.refresh()
        ch = w.getch()

def redrawMenu(w,items,highlight):
    i=0
    for (mitem,fun) in items:
        w.addstr(i,0, mitem)
        i +=1
    w.chgat(highlight, 0, curses.A_REVERSE)
    w.refresh()


def addForm():
    w=curses.newwin(1,1,20,20)
    bf = bookForm.bookForm(w)
    bf.lookup=bookData.openLibrary
    bf.caption='Add a Book'
    bf.blabel = 'Add'
    book = bf.eventLoop()
    bf.clear()
    if len(book)!=0:
        db.addBook(book)


def updateMenu():
    w=curses.newwin(1,50,10,10)
    w.addstr("I will be used to update or modify book records")
    w.refresh()

def deleteMenu():
    w=curses.newwin(1,50,10,10)
    w.addstr("I will be used to delete book records")
    w.refresh()

def browseMenu():
    w=curses.newwin(30,80,20,20)
    b = browser.browserWindow(w)
    b.startBrowser()
    b.clear()


m = [("Browse Library", browseMenu),
     ("Add Book or other item", addForm),
     ("Modify/Update record", updateMenu),
     ("Remove book from catalogue", deleteMenu),
     ("",exit),
     ("Exit", exit)]
curses.wrapper(menutest, m)
