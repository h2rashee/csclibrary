import curses

class helpBar:
    # commands is in the form (key, command_name)
    commands = []
    mx=my=0
    x=y=0
    colWidth = 25
    numCols=1

    def __init__(self, window):
        self.w = window

    def updateGeometry(self):
        (self.my, self.mx) = self.w.getmaxyx()
        (self.y, self.x) = self.w.getbegyx()
        self.numCols = self.mx//self.colWidth
        numRows = len(self.commands)//self.numCols +1
        self.y += self.my - numRows
        self.my = numRows
        self.w.mvwin(0,0)
        self.w.resize(self.my,self.mx)
        self.w.mvwin(self.y,self.x)

    def refresh(self):
        self.clear()
        self.updateGeometry()
        r=0
        c=0
        for key,command in self.commands:
            self.w.addnstr(r,c,key+" "+command+" "*self.colWidth,
                           self.colWidth-1)
            self.w.chgat(r,c,2,curses.A_REVERSE)
            c+=self.colWidth
            if c > self.colWidth*self.numCols:
                c=0
                r+=1
        self.w.refresh()

    def clear(self):
        self.w.erase()
        self.w.refresh()

    def getSearch(self):
        self.clear()
        self.w.addstr(0,0,"/")
        string = ""
        done = False
        self.w.keypad(1)
        ch = self.w.getch()
        while (not done):
            if ch == curses.KEY_ENTER or ch == 10:
                return string
            elif ch == 27: # escape
                return ""
            elif ch == curses.KEY_BACKSPACE and string !="":
                self.w.addstr(0,1," "*len(string))
                string = string[0:len(string)-1]
                self.w.addstr(0,1,string)
            elif ch>=32 and ch<=126:
                char = curses.keyname(ch).decode('utf-8')
                string = string + char
                self.w.addstr(0,1,string)
            self.w.refresh()
            ch = self.w.getch()

    def display(self,string):
        self.clear()
        self.w.addstr(0,1,string)
        self.w.refresh()
