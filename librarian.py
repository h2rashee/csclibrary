#!/usr/bin/env python3

import curses
import db_layer as db
import browser
import form
import help_bar as helpBar

import book_data

import checkout as co


stdscr=0
hb=0

menu_commands = [(' q','quit')]

def menutest(s, l):
    global stdscr
    global hb
    stdscr=s
    curses.curs_set(0)
    (rows,cols)=stdscr.getmaxyx()
    # set the default for the browser windows
    browser.browserWindow._default_height = rows-10
    browser.browserWindow._default_width = cols-10
    bar = curses.newwin(1,cols-2,rows-1,1)
    hb = helpBar.helpBar(bar)
    hb.command=menu_commands
    hb.refresh()
    w = curses.newwin(15,40,(rows-10)//2, (cols-40)//2)

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
    bf = form.BookForm(w,hb,width=mx-20)
    (r,c)=w.getmaxyx()
    w.mvwin((my-r)//2,(mx-c)//2)
    bf.lookup_isbn=book_data.openLibrary_isbn
    bf.lookup_lccn=book_data.openLibrary_lccn
    bf.caption='Add a Book'
    bf.blabel = 'Add'
    book = bf.event_loop()
    bf.clear()
    if len(book)!=0:
        db.addBook(book)

def browseMenu():
    w=curses.newwin(3,5)
    b = browser.bookBrowser(w,hb)
    (r,c) = w.getmaxyx()
    (my,mx)=stdscr.getmaxyx()
    w.mvwin((my-r)//2 -2, (mx-c)//2)
    b.refreshBooks()
    b.eventLoop()
    b.clear()

def trashMenu():
    w=curses.newwin(3,5)
    b = browser.trashBrowser(w,hb)
    (r,c) = w.getmaxyx()
    (my,mx)=stdscr.getmaxyx()
    w.mvwin((my-r)//2 -2, (mx-c)//2)
    b.refreshBooks()
    b.eventLoop()
    b.clear()

def checkedout_menu():
    w=curses.newwin(3,5)
    b = browser.bookBrowser(w,hb)
    (r,c) = w.getmaxyx()
    (my,mx)=stdscr.getmaxyx()
    w.mvwin((my-r)//2 -2, (mx-c)//2)
    b.load_data(db.get_checkedout_books())
    b.columnDefs = [("id",0,3),
                    ("uwid",0,8),
                    ("date",0,10),
                    ("title",100,None)]
    b.calcColWidths()
    b.eventLoop()
    b.clear()

def onshelf_menu():
    w=curses.newwin(3,5)
    b = browser.bookBrowser(w,hb)
    (r,c) = w.getmaxyx()
    (my,mx)=stdscr.getmaxyx()
    w.mvwin((my-r)//2 -2, (mx-c)//2)
    b.load_data(db.get_onshelf_books())
    b.eventLoop()
    b.clear()

def co_menu():
    w=curses.newwin(1,1)
    (my,mx)=stdscr.getmaxyx()
    co.checkout_procedure(w,hb,my//2,mx//2,mx) 

def return_menu():
    w=curses.newwin(1,1)
    (my,mx)=stdscr.getmaxyx()
    co.return_procedure(w,hb,my//2,mx//2,mx) 

def catMenu():
    (my,mx)=stdscr.getmaxyx()
    w=curses.newwin(3,5)
    cat = browser.categoryBrowser(w,hb, 10,40)
    (r,c) = w.getmaxyx()
    w.mvwin((my-r)//2 -2, (mx-c)//2)
    cat.refreshCategories()
    cat.sortByColumn('category')
    cat.eventLoop()
    cat.clear()


if __name__ == "__main__":
    db.initializeDatabase()
    m = [("Browse Library", browseMenu),
         ("Add Book", addForm),
         ("Categories", catMenu),
         ("View Trash", trashMenu),
         ("",exit),
         ("Check Out a Book", co_menu),
         ("Return a Book", return_menu),
         ("",exit),
         ("View Checked Out Books", checkedout_menu),
         ("View On Shelf Books", onshelf_menu),
         ("",exit),
         ("Exit", exit)]
    curses.wrapper(menutest, m)


