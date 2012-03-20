import curses





class bookForm:
    mx = my = 0
    hl = 0
    topline = 0
    cursor = 0
    left = 0
    top = 2
    caption = "Add a Book"
    blabel = "Add"
    labels = ["ISBN", "LCCN", "Title", "Subtitle", "Authors", "Edition",
              "Publisher", "Publish Date", "Publish Year", "Publish Month", "Publish location",
              "Pages", "Pagination", "Weight"]
    entries = []

    def __init__(self,window):
        self.w = window
        self.w.resize(len(self.labels)+6,50)
        self.updateEntries({})
        self.updateGeometry()

    def updateGeometry(self):
        (self.my, self.mx) = self.w.getmaxyx()
        for l in self.labels:
            self.left = max(len(l),self.left)
        self.left += 4
        self.width = self.mx-self.left-2
        self.top = 2
        # next, the buttons
        self.bcol = [self.mx-len(self.blabel)-14, self.mx-len(self.blabel)-4]
        self.bwidth = [8,len(self.blabel)+2]

    def updateEntries(self,book)
        self.entries=[]
        for l in self.labels:
            if l.lower() in book:
                self.entries.append(book[l.lower()])
            else:
                self.entries.append("")


    def highlight(self):
        if bt = -1:
            self.w.chgat(self.row, self.left, self.width, curses.A_UNDERLINE)
        else:
            self.w.chgat(self.row, self.bcol[self.bt], self.bwidth[self.bt], curses.A_REVERSE)

        
        cursor = len(entries[highlight])
        w.move(r,m+cursor)
        curses.curs_set(1)
        row = self.hl-self.topline+self.top
        if row > 1 and row < self.my:
            self.w.chgat(row,0,self.mx,curses.A_REVERSE)

    def unHighlight(self):
        row = self.hl-self.topline+self.top
        if row > 1 and row < self.my:
            self.w.chgat(row,0,self.mx,curses.A_NORMAL)

    def mvHighlight(self,delta):
        new = self.hl+delta
        if self.hl = len(self.labels)+1:    # skip cancel button when going up
            new -= 1
        new = max(new,0)
        new = min(new,len(self.labels)+1)   # there are two buttons, so add 2 to length
        self.unHighlight()
        self.hl = new
        self.row = self.hl + self.top
        self.highlight()
    

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
