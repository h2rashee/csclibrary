import curses
from library.interface.form import FormWindow,BookForm
import library.database as db


class BookIDForm(FormWindow):
    caption = "Enter the book ID"
    blabel = "Check"
    labels = ["Book ID"]

    def _return_values(self):
        if self._confirm_book():
            return self.entries[0].value
        else:
            return False

    def _confirm_book(self):
        self.clear()
        bookid = self.entries[0].value
        book = db.get_book(bookid)
        bf = BookForm(self.w, self.hb, book, width=self.mx-10)
        (y,x) = self.w.getbegyx()
        (r,c) = self.w.getmaxyx()
        self.w.mvwin( y+(self.my-r)//2,x+(self.mx-c)//2)
        bf.caption='Confirm the Book '+str(bookid)
        bf.blabel='Correct'
        result = bf.event_loop()
        bf.clear()
        if result:
            return True


class UWIDForm(FormWindow):
    caption = "Enter the Patron's username"
    blabel = "Next"
    labels = ["Username"]

    def _return_values(self):
        return self.entries[0].value

class FinalCheck(FormWindow):
    caption = "Is this information correct?"
    blabel = "Check Out"
    labels = ["Username", "Book ID"]

    def _return_values(self):
        return True

def checkout_procedure(w, hb, cy, cx, mx):
    """Procedure to check out a book

    w:      ncurses window for the routine
    cy,cx:  centre coordinates of the screen
    mx:     max width of screen
    """
    # Get the book ID
    step1 = BookIDForm(w,hb,width=mx-20)
    (r,c)=w.getmaxyx()
    w.mvwin(cy-r//2,cx-c//2)
    book_id = step1.event_loop()
    step1.clear()
    if not(book_id):
        return

    # Get the uwid
    step2 = UWIDForm(w,hb,width=mx-20)
    (r,c)=w.getmaxyx()
    w.mvwin(cy-r//2,cx-c//2)
    username = step2.event_loop()
    step2.clear()
    if not(username):
        return

    # Confirm the result
    step3 = FinalCheck(w,hb,book={"username":username,"book id":book_id}, width=mx-20)
    (r,c)=w.getmaxyx()
    w.mvwin(cy-r//2,cx-c//2)
    correct = step3.event_loop()
    step3.clear()
    if correct:
        db.checkout_book(book_id,username)

def return_procedure(w, hb, cy, cx, mx):
    """Procedure to return a book

    w:      ncurses window for the routine
    cy,cx:  centre coordinates of the screen
    mx:     max width of screen
    """
    # Get the book ID
    step1 = BookIDForm(w,hb,width=mx-20)
    (r,c)=w.getmaxyx()
    w.mvwin(cy-r//2,cx-c//2)
    book_id = step1.event_loop()
    step1.clear()
    if book_id:
        db.return_book(book_id)
    
