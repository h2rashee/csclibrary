import curses

class bookForm:
    mx = my = 0
    hl = 0
    bt = -1
    cursor = 0
    textStart = 0
    left = 0
    top = 2
    row = 2
    caption = "Add a Book"
    blabel = "Add"
    labels = ["ISBN", "LCCN", "Title", "Subtitle", "Authors", "Edition",
              "Publishers", "Publish Date", "Publish Year", "Publish Month", "Publish location",
              "Pages", "Pagination", "Weight"]
    entries = []

    # redefineable functions lookup is called when 'enter' is pressed on ISBN
    # and returns the looked-up book. Default returns nothing
    def lookup(self,isbn):
        return {'isbn':isbn}

    def __init__(self,window,book={}):
        self.w = window
        self.w.resize(len(self.labels)+6,50)
        self.updateEntries(book)
        self.updateGeometry()

    def updateGeometry(self):
        (self.my, self.mx) = self.w.getmaxyx()
        self.left=0
        for l in self.labels:
            self.left = max(len(l),self.left)
        self.left += 4
        self.width = self.mx-self.left-2
        self.top = 2
        # next, the buttons
        self.bcol = [self.mx-len(self.blabel)-14, self.mx-len(self.blabel)-4]
        self.bwidth = [8,len(self.blabel)+2]

    def updateEntries(self,book):
        self.entries=[]
        for l in self.labels:
            if l.lower() in book:
                self.entries.append(str(book[l.lower()]))
            else:
                self.entries.append("")

    def refresh(self):
        self.updateGeometry()
        self.w.box()
        self.w.addstr(0,(self.mx-len(self.caption))/2,self.caption)
        r=self.top
        for l in self.labels:
            c = self.left-len(l)-2
            self.w.addstr(r,c,l+":")
            self.drawRow(r-self.top)
            r+=1
        self.w.addstr(r+1,self.bcol[0], "<cancel>  <"+self.blabel+">")
        self.w.refresh()

    def drawRow(self,row):
        r = self.top + row
        self.w.addnstr(r,self.left, self.entries[row]+" "*self.width, self.width)

    def highlight(self):
        if self.bt == -1:
            self.w.chgat(self.row, self.left, self.width, curses.A_UNDERLINE)
            self.w.move(self.row, self.left+self.cursor)
            curses.curs_set(1)
        else:
            self.w.chgat(self.row, self.bcol[self.bt], self.bwidth[self.bt], curses.A_REVERSE)
            curses.curs_set(0)

    def unHighlight(self):
        self.w.chgat(self.row,1,self.mx-2,curses.A_NORMAL)

    def mvHighlight(self,delta):
        self.unHighlight()
        new = self.hl+delta
        new = max(new,0)
        new = min(new,len(self.labels))   # the extra is for the buttons
        self.hl = new
        self.row = self.hl + self.top
        if new == len(self.labels):
            self.bt+=1
            self.bt = min(self.bt,1)
            self.row+=1
        else:
            self.mvCursor(+len(self.entries[self.hl]))
            self.bt=-1
        self.highlight()

    def mvCursor(self,delta):
        n = self.cursor + delta
        n = max(n,0)
        n = min(n,len(self.entries[self.hl]))
        self.cursor = n
        col = self.left + self.cursor - self.textStart
        if col >= self.left and col < self.left+self.width:
            self.w.move(self.row,col)

    def insert(self,ch):
        c = self.cursor
        self.entries[self.hl]=self.entries[self.hl][:c] +ch+  self.entries[self.hl][c:]
        self.drawRow(self.hl)
        self.highlight()
        self.mvCursor(+1)

    def backspace(self):
        if self.cursor>0:
            self.entries[self.hl]=self.entries[self.hl][:self.cursor-1] + self.entries[self.hl][self.cursor:]
            self.drawRow(self.hl)
            self.highlight()
            self.mvCursor(-1)

    def delete(self):
        c = self.cursor
        self.entries[self.hl]=self.entries[self.hl][:c] + self.entries[self.hl][c+1:]
        self.drawRow(self.hl)
        self.highlight()


    def returnBook():
        book = {}
        for k,v in zip(self.labels, self.entries):
            if v!="" and k.lower()!="publish date":
                book[k.lower()]=v
        return book

    def eventLoop(self):
        self.w.keypad(1)
        self.refresh()
        self.highlight()

        ch = self.w.getch()
        while ch != 27:
            if ch==curses.KEY_UP:
                self.mvHighlight(-1)
            elif ch==curses.KEY_PPAGE:
                self.mvHighlight(-len(self.labels))
            elif ch==curses.KEY_DOWN:
                self.mvHighlight(+1)
            elif ch==curses.KEY_NPAGE:
                self.mvHighlight(+len(self.labels))

            elif ch==curses.KEY_LEFT:
                if self.bt==-1:
                    self.mvCursor(-1)
                else:
                    self.bt=0
            elif ch==curses.KEY_HOME:
                if self.bt==-1:
                    self.mvCursor(-len(self.entries[self.hl]))
            elif ch==curses.KEY_RIGHT:
                if self.bt==-1:
                    self.mvCursor(+1)
                else:
                    self.bt=1
            elif ch==curses.KEY_END:
                if self.bt==-1:
                    self.mvCursor(+len(self.entries[self.hl]))

            elif ch>=32 and ch<=126:
                if self.bt==-1:
                    self.insert(curses.keyname(ch))
            elif ch==curses.KEY_BACKSPACE:
                if self.bt==-1:
                    self.backspace()
            elif ch==curses.KEY_DC:
                if self.bt==-1:
                    self.delete()
            
            elif ch==10 or ch==curses.KEY_ENTER:
                if self.hl==0:
                    book = self.lookup(self.entries[0])
                    self.updateEntries(book)
                    self.refresh()
                elif self.bt==0:
                    return {}
                elif self.bt==1:
                    return self.returnBook()
                self.mvHighlight(+1)
            self.w.refresh()
            ch = self.w.getch()
        
