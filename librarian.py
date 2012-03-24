#!/usr/bin/env python

import curses
import dbLayer as db
import browser
import bookForm
import helpBar

import bookData


stdscr=0
hb=0

menu_commands = [(' q','quit')]
browser_commands = [(' u','update'), (' d','delete'), (' q','quit')]

def menutest(s, l):
    global stdscr
    global hb
    stdscr=s
    curses.curs_set(0)
    (rows,cols)=stdscr.getmaxyx()
    bar = curses.newwin(1,cols-2,rows-1,1)
    hb = helpBar.helpBar(bar)
    hb.command=menu_commands
    hb.refresh()
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
        if ch==curses.KEY_UP or ch==107 or ch==16:
            if highlight!=0:
                w.chgat(highlight,0, 0)
                highlight -= 1
                while(items[highlight][0]==""):
                    highlight -=1
                w.chgat(highlight,0, curses.A_REVERSE)
        if ch==curses.KEY_DOWN or ch==106 or ch==14:
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
    hb.commands=menu_commands
    hb.refresh()


def addForm():
    w=curses.newwin(1,1)
    (my,mx)=stdscr.getmaxyx()
    (r,c)=w.getmaxyx()
    w.mvwin((my-r)/2,(mx-c)/2)
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
    (my,mx)=stdscr.getmaxyx()
    w=curses.newwin(20,80,(my-20)/2,(mx-80)/2)
    b = browser.bookBrowser(w)
    b.refreshBooks()
    hb.commands=browser_commands
    hb.refresh()
    b.eventLoop()
    b.clear()

def catMenu():
    (my,mx)=stdscr.getmaxyx()
    w=curses.newwin(10,40,(my-10)/2,(mx-40)/2)
    c = browser.categoryBrowser(w)
    c.refreshCategories()
    c.sortByColumn('category')
    hb.commands=browser_commands
    hb.refresh()
    c.eventLoop()
    c.clear()


m = [("Browse Library", browseMenu),
     ("Add Book or other item", addForm),
     ("View the categories", catMenu),
     ("Remove book from catalogue", deleteMenu),
     ("",exit),
     ("Exit", exit)]
curses.wrapper(menutest, m)
