import curses
import sys

class textEntry:
    cursor = 0
    start = 0
    focus = False
    x = 0
    y = 0
    width = 10
    value = ""

    def __init__(self, parent_window, value=""):
        self.w = parent_window
        self.value = value

    def setGeom(self,y,x,width):
        self.x = x
        self.y = y
        self.width = width

    def redraw(self):
        self.w.addnstr(self.y,self.x, self.value[self.start:]+" "*self.width, self.width)
        if self.focus:
            self.w.chgat(self.y, self.x, self.width, curses.A_UNDERLINE)
            curses.curs_set(1)

    def gainFocus(self):
        sys.stderr.write('I have focus!\n')
        self.focus = True
        self.mvCursor(+len(self.value))
        self.start = max(0,self.cursor-self.width) 
        self.redraw()

    def loseFocus(self):
        self.focus = False
        self.cursor = 0
        self.start = 0
        self.redraw()
    
    def mvCursor(self,delta):
        n = self.cursor + delta
        # make sure new position is legal
        n = max(n,0)
        n = min(n,len(self.value))
        self.cursor = n
        self.start = max(0,self.cursor-self.width+1) 
        self.redraw()
        col = self.x + self.cursor - self.start
        self.w.move(self.y,col)

    def insert(self,ch):
        c = self.cursor
        self.value = self.value[:c] +ch+  self.value[c:]
        self.mvCursor(+1)

    def backspace(self):
        if self.cursor>0:
            c = self.cursor
            self.value=self.value[:c-1] + self.value[c:]
            self.mvCursor(-1)

    def delete(self):
        c = self.cursor
        self.value = self.value[:c] + self.value[c+1:]
        self.mvCursor(0)

    def handle_input(self,ch):
        if ch==curses.KEY_LEFT:
            self.mvCursor(-1)
        elif ch==curses.KEY_HOME:
            self.mvCursor(-len(self.value))
        elif ch==curses.KEY_RIGHT:
            self.mvCursor(+1)
        elif ch==curses.KEY_END:
            self.mvCursor(+len(self.value))

        elif ch>=32 and ch<=126:
            self.insert(curses.keyname(ch))
        elif ch==curses.KEY_BACKSPACE:
            self.backspace()
        elif ch==curses.KEY_DC:
            self.delete()



class formWindow:
    mx = my = 0
    hl = 0
    bt = -1
    left = 0
    top = 2
    row = 2
    caption = "Form"
    blabel = "Done"
    labels = ["label1"]
    entries=[]

    commands = [('pU', 'top'),('pD', 'bottom'),('Es', 'cancel')]

    def clear(self):
        self.w.erase()
        self.w.refresh()

    def __init__(self,window,helpbar,book={}):
        self.w = window
        self.w.resize(len(self.labels)+6,50)
        self.hb = helpbar
        self.makeEntries()
        self.updateGeometry()
        self.updateEntries(book)

    def makeEntries(self):
        for e in range(len(self.labels)):
            self.entries.append(textEntry(self.w))

    def updateGeometry(self):
        (self.my, self.mx) = self.w.getmaxyx()
        self.left=0
        for l in self.labels:
            self.left = max(len(l),self.left)
        self.left += 4
        width = self.mx-self.left-2
        self.top = 2
        for r in range(len(self.entries)):
            self.entries[r].setGeom(r+self.top, self.left, width)
        # next, the buttons
        self.brow = self.top+len(self.labels)+1
        self.bcol = [self.mx-len(self.blabel)-14, self.mx-len(self.blabel)-4]
        self.bwidth = [8,len(self.blabel)+2]

    def updateEntries(self,book):
        e = 0
        for l in self.labels:
            sys.stderr.write('updating label: '+l+'\n')
            if l.lower() in book:
                sys.stderr.write('   '+l+' found\n')
                self.entries[e].value = str(book[l.lower()])
            else:
                sys.stderr.write('   '+l+' notfound\n')
                self.entries[e].value = ""
            e += 1 

    def redraw(self):
        self.w.box()
        self.w.addstr(0,(self.mx-len(self.caption))//2,self.caption)
        r=0
        for l in self.labels:
            c = self.left-len(l)-2
            self.w.addstr(r+self.top,c,l+":")
            self.entries[r].redraw()
            r+=1
        self.w.addstr(self.brow,self.bcol[0], "<cancel>  <"+self.blabel+">")
        self.w.refresh()

    def refresh(self):
        self.hb.commands = self.commands
        self.hb.refresh()
        self.updateGeometry()
        self.redraw()

    def highlightButton(self):
        self.w.chgat(self.brow, self.bcol[self.bt], self.bwidth[self.bt], curses.A_REVERSE)
        curses.curs_set(0)

    def unHighlightButton(self):
        self.w.chgat(self.brow,1,self.mx-2,curses.A_NORMAL)

    def mvFocus(self,delta):
        if self.bt==-1:
            self.entries[self.hl].loseFocus()
        else:
            self.unHighlightButton()
        new = self.hl+delta
        new = max(new,0)
        new = min(new,len(self.labels))   # the extra is for the buttons
        self.hl = new
        if new == len(self.labels):
            self.bt = 1
            self.bt = min(self.bt,1)
            self.highlightButton()
        else:
            self.bt=-1
            self.entries[self.hl].gainFocus()


    def returnValues(self):
        book = {}
        for k,e in zip(self.labels, self.entries):
            if v!="" and k.lower()!="publish date":
                book[k.lower()]=e.value
        return book

    def eventLoop(self):
        self.w.keypad(1)
        self.refresh()
        self.hl=0;
        self.entries[self.hl].gainFocus()

        ch = self.w.getch()
        while ch != 27:
            self.handleInput(ch)
            if ch==10 or ch==curses.KEY_ENTER:
                if self.bt==0:
                    return {}
                elif self.bt==1:
                    return self.returnValues()
                else:
                    self.mvFocus(+1)
            self.w.refresh()
            ch = self.w.getch()
        curses.curs_set(0)
        return {}


    def handleInput(self,ch):
        if ch==curses.KEY_UP:
            self.mvFocus(-1)
        elif ch==curses.KEY_PPAGE:
            self.mvFocus(-len(self.labels))
        elif ch==curses.KEY_DOWN:
            self.mvFocus(+1)
        elif ch==curses.KEY_NPAGE:
            self.mvFocus(+len(self.labels))
        elif ch==curses.KEY_LEFT:
            if self.bt==-1:
                self.entries[self.hl].handle_input(ch)
            else:
                self.unHighlightButton()
                self.bt=0
                self.highlightButton()
        elif ch==curses.KEY_HOME:
            if self.bt==-1:
                self.mvCursor(-len(self.entries[self.hl]))
        elif ch==curses.KEY_RIGHT:
            if self.bt==-1:
                self.entries[self.hl].handle_input(ch)
            else:
                self.unHighlightButton()
                self.bt=1
                self.highlightButton()
        else:
            if self.bt==-1:
                self.entries[self.hl].handle_input(ch)

        
        

class bookForm(formWindow):
    caption = "Add a Book"
    blabel = "Add"
    labels = ["ISBN", "LCCN", "Title", "Subtitle", "Authors", "Edition",
              "Publisher", "Publish Date", "Publish Year", "Publish Month", "Publish location",
              "Pages", "Pagination", "Weight"]
    

    # redefineable functions lookup is called when 'enter' is pressed on ISBN
    # and returns the looked-up book. Default returns nothing
    def lookup_isbn(self,isbn):
        return {'isbn':isbn}
    
    def lookup_lccn(self,lccn):
        return {'lccn':lccn}

    def returnBook(self):
        return self.returnValues()

    def handleInput(self,ch):
        if ch==10 or ch==curses.KEY_ENTER:
            if self.hl==0:          # lookup by isbn
                book = self.lookup_isbn(self.entries[0].value)
                if book != {}:
                    sys.stderr.write('updating entries\n')
                    self.updateEntries(book)
                self.refresh()
                self.mvFocus(+7)
            if self.hl==1:          # lookup by lccn
                book = self.lookup_lccn(self.entries[1].value)
                if book != {}:
                    self.updateEntries(book)
                self.refresh()
                self.mvFocus(+6)
        else:
            formWindow.handleInput(self,ch)

class categoryForm(formWindow):
    caption = "Add a Category"
    blabel = "Add"
    labels = ["Category"]

    def returnValues(self):
        return self.entries
