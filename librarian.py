#!/usr/bin/env python

import curses

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


#the final form for book data entry - takes caption and book info.
def bookForm(caption, book, buttonlabel):
    labels = ["ISBN", "LCCN", "Title", "Subtitle", "Authors", "Edition",
              "Publisher", "Publish Date", "Publish Year", "Publish Month", "Publish location",
              "Pages", "Pagination", "weight"]
    entries = []
    m = 0
    for l in labels:
        m = max(len(l),m)
        if l.lower() in book:
            entries.append(book[l.lower()])
        else:
            entries.append("")
    m+=4

    w=curses.newwin(34,50,1,10)
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
    ch = w.getch()
    while (ch!=113):
        if ch==curses.KEY_UP:
            if highlight == len(labels):
                w.chgat(r,bcol[b],bwidth[b],curses.A_NORMAL)
                highlight = len(labels)-1
                b = -1
                r=3+2*highlight
                w.chgat(r,m,x-m-2,curses.A_UNDERLINE)
                w.move(r,m+len(entries[highlight]))
                curses.curs_set(1)
            elif highlight!=0:
                w.chgat(r,m,x-m-2,curses.A_NORMAL)
                highlight -= 1
                r=3+2*highlight
                w.chgat(r,m,x-m-2,curses.A_UNDERLINE)
                w.move(r,m+len(entries[highlight]))
        if ch==curses.KEY_DOWN:
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
                w.move(r,m+len(entries[highlight]))
        if ch==10:
            if b != -1:
                if b == 0:
                    w.clear()
                    w.refresh()
                    return {}
                elif b == 1:
                    w.clear()
                    w.refresh()
                    return {"title": "I was 'added'"}
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
                w.move(r,m+len(entries[highlight]))


        w.refresh()
        ch = w.getch()

    curses.curs_set(0)
    w.clear()
    w.refresh()
    return {"title":"this is what I returned"}


def addForm():
    book = {"title":"A Book of Tests", "pages":"123"}
    book = bookForm("Add a book", book, "add")
    stdscr.getch()
    bookForm("View the book", book, "done")


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
     ("Add Book or other item", addForm),
     ("Modify/Update record", updateMenu),
     ("Remove book from catalogue", deleteMenu)]
curses.wrapper(menutest, m)
