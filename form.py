import curses
import sys


class TextEntry:

    """A part of a window that handles text entry.
    Properties:
        value holds the string that was entered
    
    Public Methods:
        set_geom(row,column,width)  Sets the geometry in the window
        set_value(string)           Set the value and redraw
        gain_focus()                Gives it focus, moving cursor and changing the drawing
        lose_focus()                Takes focus, moving cursor to start, changing drawing
        handle_input(ch)            Pass this the ncurses key, and it manages input
        redraw()                    Redraw the text entry (should never need to do this
        """

    # Public
    value = ""  # Use the set_value function to set, but retrieve with value

    # Should be Private
    cursor = 0
    start = 0
    focus = False
    x = 0
    y = 0
    width = 10

    # Public methods
    def __init__(self, parent_window, value=""):
        self.w = parent_window
        self.value = value

    def set_geom(self,y,x,width):
        self.x = x
        self.y = y
        self.width = width

    def set_value(self,v):
        self.value=v
        self.cursor=len(v)
        self.redraw()

    def gain_focus(self):
        #sys.stderr.write('I have focus!\n')
        self.focus = True
        self._mv_cursor(+len(self.value))
        self.start = max(0,self.cursor-self.width) 
        self.redraw()

    def lose_focus(self):
        self.focus = False
        self.cursor = 0
        self.start = 0
        self.redraw()
    
    def handle_input(self,ch):
        if ch==curses.KEY_LEFT:
            self._mv_cursor(-1)
        elif ch==curses.KEY_HOME:
            self._set_cursor(0)
        elif ch==curses.KEY_RIGHT:
            self._mv_cursor(+1)
        elif ch==curses.KEY_END:
            self._set_cursor(len(self.value))
        elif ch>=32 and ch<=126:
            self._insert(curses.keyname(ch).decode('utf-8'))
        elif ch==curses.KEY_BACKSPACE:
            self._backspace()
        elif ch==curses.KEY_DC:
            self._delete()

    def redraw(self):
        self.w.addnstr(self.y,self.x, self.value[self.start:]+" "*self.width, self.width)
        if self.focus:
            self.w.chgat(self.y, self.x, self.width, curses.A_UNDERLINE)
            curses.curs_set(1)

    # Private functions
    def _mv_cursor(self,delta):
        self._set_cursor(self.cursor + delta)
    
    def _set_cursor(self, new_c):
        self.cursor = max(0, min(len(self.value), new_c))
        self.start = max(0,self.cursor-self.width+1) 
        self.redraw()
        # Place the drawn cursor in the correct spot
        col = self.x + self.cursor - self.start
        self.w.move(self.y,col)

    def _insert(self,ch):
        c = self.cursor
        self.value = self.value[:c] +ch+  self.value[c:]
        self._mv_cursor(+1)

    def _backspace(self):
        if self.cursor>0:
            c = self.cursor
            self.value=self.value[:c-1] + self.value[c:]
            self._mv_cursor(-1)

    def _delete(self):
        c = self.cursor
        self.value = self.value[:c] + self.value[c+1:]
        self._mv_cursor(0)



class FormWindow:

    """General class for a Form Window.
    
    To use, make the window for it, call the constructor, then call event_loop.
    """

    # Private variables
    mx = my = 0
    hl = 0
    bt = -1
    left = 0
    top = 2
    row = 2
    caption = "Form"
    blabel = "Done"
    labels = ["label1"]

    commands = [('pU', 'top'),('pD', 'bottom'),('Es', 'cancel')]


    # Public functions
    def __init__(self,window,helpbar,book={}, width=50):
        self.w = window
        self.w.resize(len(self.labels)+6,width)
        self.hb = helpbar
        self._make_entries()
        self._update_geometry()
        self._set_entries(book)

    def clear(self):
        self.w.erase()
        self.w.refresh()

    def event_loop(self):
        self.w.keypad(1)
        self.refresh()
        self.hl=0;
        self.entries[self.hl].gain_focus()

        ch = self.w.getch()
        while ch != 27:
            #sys.stderr.write(curses.keyname(ch).decode('utf-8'))
            self.handle_input(ch)
            if ch==10 or ch==curses.KEY_ENTER:
                if self.bt==0:
                    return {}
                elif self.bt==1:
                    return self.return_values()
                else:
                    self._mv_focus(+1)
            self.w.refresh()
            ch = self.w.getch()
        curses.curs_set(0)
        return {}

    def _make_entries(self):
        self.entries = []
        for e in range(len(self.labels)):
            self.entries.append(TextEntry(self.w))

    def _update_geometry(self):
        (self.my, self.mx) = self.w.getmaxyx()
        self.left=0
        for l in self.labels:
            self.left = max(len(l),self.left)
        self.left += 4
        width = self.mx-self.left-2
        self.top = 2
        for r in range(len(self.entries)):
            self.entries[r].set_geom(r+self.top, self.left, width)
        # next, the buttons
        self.brow = self.top+len(self.labels)+1
        self.bcol = [self.mx-len(self.blabel)-14, self.mx-len(self.blabel)-4]
        self.bwidth = [8,len(self.blabel)+2]

    def _set_entries(self,book):
        e = 0
        for l in self.labels:
            #sys.stderr.write('updating label: '+l+'\n')
            if l.lower() in book:
                #sys.stderr.write('   '+l+' found\n')
                self.entries[e].value = str(book[l.lower()])
            else:
                #sys.stderr.write('   '+l+' notfound\n')
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
        self._update_geometry()
        self.redraw()

    def _highlight_button(self):
        self.w.chgat(self.brow, self.bcol[self.bt], self.bwidth[self.bt], curses.A_REVERSE)
        curses.curs_set(0)

    def _unhighlight_button(self):
        self.w.chgat(self.brow,1,self.mx-2,curses.A_NORMAL)

    def _mv_focus(self,delta):
        if self.bt==-1:
            self.entries[self.hl].lose_focus()
        else:
            self._unhighlight_button()
        new = self.hl+delta
        new = max(0, min(len(self.labels), new))   # the extra is for the buttons
        self.hl = new
        if new == len(self.labels):
            self.bt = 1
            self.bt = min(self.bt,1)
            self._highlight_button()
        else:
            self.bt=-1
            self.entries[self.hl].gain_focus()


    def _return_values(self):
        book = {}
        for k,e in zip(self.labels, self.entries):
            if v!="" and k.lower()!="publish date":
                book[k.lower()]=e.value
        return book


    def handle_input(self,ch):
        if ch==curses.KEY_UP:
            self._mv_focus(-1)
        elif ch==curses.KEY_PPAGE:
            self._mv_focus(-len(self.labels))
        elif ch==curses.KEY_DOWN:
            self._mv_focus(+1)
        elif ch==curses.KEY_NPAGE:
            self._mv_focus(+len(self.labels))
        elif ch==curses.KEY_LEFT:
            if self.bt==-1:
                self.entries[self.hl].handle_input(ch)
            else:
                self._unhighlight_button()
                self.bt=0
                self._highlight_button()
        elif ch==curses.KEY_HOME:
            if self.bt==-1:
                self._mv_cursor(-len(self.entries[self.hl]))
        elif ch==curses.KEY_RIGHT:
            if self.bt==-1:
                self.entries[self.hl].handle_input(ch)
            else:
                self._unhighlight_button()
                self.bt=1
                self._highlight_button()
        else:
            if self.bt==-1:
                self.entries[self.hl].handle_input(ch)

        
        

class BookForm(FormWindow):
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

    def return_book(self):
        return self.return_values()

    def handle_input(self,ch):
        if ch==10 or ch==curses.KEY_ENTER:
            if self.hl==0:          # lookup by isbn
                book = self.lookup_isbn(self.entries[0].value)
                if book != {}:
                    #sys.stderr.write('updating entries\n')
                    self._set_entries(book)
                self.refresh()
                self._mv_focus(+7)
            if self.hl==1:          # lookup by lccn
                book = self.lookup_lccn(self.entries[1].value)
                if book != {}:
                    self._set_entries(book)
                self.refresh()
                self._mv_focus(+6)
        else:
            FormWindow.handle_input(self,ch)

class CategoryForm(FormWindow):
    caption = "Add a Category"
    blabel = "Add"
    labels = ["Category"]

    def return_values(self):
        return self.entries
