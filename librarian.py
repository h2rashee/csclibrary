#!/usr/bin/env python

import curses
import dbLayer as db
import browser

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

# items is a list of (label, value) pairs
def redrawForm(w, caption, items, buttonlabel, m):
    (y,x)=w.getmaxyx()
    w.border()
    curses.curs_set(1)
    w.addstr(1,1,caption)
    r=3
    for l,v in items:
        c = m-len(l)-2
        w.addstr(r,c,l+":")
        w.addstr(r,m,v)
        r+=2
    w.addstr(r,x-len(buttonlabel)-len("<cancel>")-6, "<cancel>  <"+buttonlabel+">")
    w.refresh()

def lists_to_dict(l1, l2):
    book = {}
    for k,v in zip(l1,l2):
        if v!="" and k.lower()!="publish date":
            book[k.lower()]=v
    return book


#the final form for book data entry - takes caption and book info.
def bookForm(caption, book, buttonlabel):
    labels = ["ISBN", "LCCN", "Title", "Subtitle", "Authors", "Edition",
              "Publisher", "Publish Date", "Publish Year", "Publish Month", "Publish location",
              "Pages", "Pagination", "Weight"]
    entries = []
    m = 0
    for l in labels:
        m = max(len(l),m)
        if l.lower() in book:
            entries.append(book[l.lower()])
        else:
            entries.append("")
    m+=4

    w=curses.newwin(34,70,1,10)
    (y,x)=w.getmaxyx()
    w.keypad(1)
    redrawForm(w,caption,zip(labels,entries),buttonlabel,m)
    bcol = [x-len(buttonlabel)-len("<cancel>")-6, x-len(buttonlabel)-4]
    bwidth = [8,len(buttonlabel)+2]
    
    highlight=0
    b = -1
    r=3
    w.chgat(r,m,x-m-2,curses.A_UNDERLINE)
    w.move(r,m+len(entries[highlight]))
    cursor = len(entries[highlight])
    ch = w.getch()
    while (1==1):
        if ch==27: #escape key
            curses.curs_set(0)
            w.clear()
            w.refresh()
            return {}
        if ch==curses.KEY_UP:
            if highlight == len(labels):
                w.chgat(r,bcol[b],bwidth[b],curses.A_NORMAL)
                highlight = len(labels)-1
                b = -1
                r=3+2*highlight
                w.chgat(r,m,x-m-2,curses.A_UNDERLINE)
                cursor = len(entries[highlight])
                w.move(r,m+cursor)
                curses.curs_set(1)
            elif highlight!=0:
                w.chgat(r,m,x-m-2,curses.A_NORMAL)
                highlight -= 1
                r=3+2*highlight
                w.chgat(r,m,x-m-2,curses.A_UNDERLINE)
                cursor = len(entries[highlight])
                w.move(r,m+cursor)
        elif ch==curses.KEY_PPAGE:
            w.chgat(r,m,x-m-2,curses.A_NORMAL)
            highlight=0
            b=-1
            r=3+2*highlight
            w.chgat(r,m,x-m-2,curses.A_UNDERLINE)
            cursor = len(entries[highlight])
            w.move(r,m+cursor)
            curses.curs_set(1)
        elif ch==curses.KEY_DOWN:
            if highlight >= len(labels) -1:
                highlight = len(labels)
                b += 1
                b = min(b,1)
                curses.curs_set(0)
                w.chgat(r,m,x-m-2,curses.A_NORMAL)
                r = y-3
                w.chgat(r,bcol[b],bwidth[b],curses.A_REVERSE)
            else:
                w.chgat(r,m,x-m-2,curses.A_NORMAL)
                highlight += 1
                r=3+2*highlight
                w.chgat(r,m,x-m-2,curses.A_UNDERLINE)
                cursor = len(entries[highlight])
                w.move(r,m+cursor)
        elif ch==curses.KEY_NPAGE:
            if highlight!=len(labels):
                highlight = len(labels)
                b += 1
                b = min(b,1)
                curses.curs_set(0)
                w.chgat(r,m,x-m-2,curses.A_NORMAL)
                r = y-3
                w.chgat(r,bcol[b],bwidth[b],curses.A_REVERSE)
        elif ch==curses.KEY_LEFT:
            if highlight == len(labels):
                w.chgat(r,bcol[b],bwidth[b],curses.A_NORMAL)
                b=0
                w.chgat(r,bcol[b],bwidth[b],curses.A_REVERSE)
            else:
                if cursor>0:
                    cursor-=1
                    w.move(r,m+cursor)
        elif ch==curses.KEY_RIGHT:
            if highlight == len(labels):
                w.chgat(r,bcol[b],bwidth[b],curses.A_NORMAL)
                b=1
                w.chgat(r,bcol[b],bwidth[b],curses.A_REVERSE)
            else:
                if cursor < len(entries[highlight]):
                    cursor+=1
                    w.move(r,m+cursor)
        elif ch>31 and ch<127:
            if highlight != len(labels):
                entries[highlight]=entries[highlight][:cursor] + curses.keyname(ch) + entries[highlight][cursor:]
                cursor+=1
                w.addnstr(r,m, entries[highlight]+(" "*40), x-m-2)
                w.chgat(r,m,x-m-2,curses.A_UNDERLINE)
                w.move(r,m+cursor)
        elif ch==curses.KEY_BACKSPACE:
            if highlight != len(labels) and cursor!=0:
                cursor-=1
                entries[highlight]=entries[highlight][:cursor] + entries[highlight][cursor+1:]
                w.addnstr(r,m, entries[highlight]+(" "*40), x-m-2)
                w.chgat(r,m,x-m-2,curses.A_UNDERLINE)
                w.move(r,m+cursor)
        elif ch==curses.KEY_DC:
            if highlight != len(labels):
                entries[highlight]=entries[highlight][:cursor] + entries[highlight][cursor+1:]
                w.addnstr(r,m, entries[highlight]+(" "*40), x-m-2)
                w.chgat(r,m,x-m-2,curses.A_UNDERLINE)
                w.move(r,m+cursor)
        elif ch==curses.KEY_HOME:
            if highlight != len(labels):
                cursor=0
                w.move(r,m+cursor)
        elif ch==curses.KEY_END:
            if highlight != len(labels):
                cursor=len(entries[highlight])
                w.move(r,m+cursor)
        elif ch==10:
            if b != -1:
                if b == 0:
                    w.clear()
                    w.refresh()
                    return {}
                elif b == 1:
                    w.clear()
                    w.refresh()
                    return lists_to_dict(labels,entries)
            elif highlight == len(labels)-1:
                highlight = len(labels)
                b=0
                curses.curs_set(0)
                w.chgat(r,m,x-m-2,curses.A_NORMAL)
                r = y-3
                w.chgat(r,bcol[b],bwidth[b],curses.A_REVERSE)
            else:
                w.chgat(r,m,x-m-2,curses.A_NORMAL)
                highlight += 1
                r=3+2*highlight
                w.chgat(r,m,x-m-2,curses.A_UNDERLINE)
                cursor = len(entries[highlight])
                w.move(r,m+cursor)


        w.refresh()
        ch = w.getch()

    curses.curs_set(0)
    w.clear()
    w.refresh()
    return {}


def addForm():
    book = {"title":"A Book of Tests", "pages":"123"}
    book = bookForm("Add a book", book, "add")
    #bookForm("View the book", book, "done")
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
    w=curses.newwin(10,80,20,20)
    b = browser.browserWindow(w)
    b.startBrowser()
    w.box()
    w.refresh()
    w.getch()


m = [("Browse Library", browseMenu),
     ("Add Book or other item", addForm),
     ("Modify/Update record", updateMenu),
     ("Remove book from catalogue", deleteMenu),
     ("",exit),
     ("Exit", exit)]
curses.wrapper(menutest, m)
