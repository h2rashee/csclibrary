import sys
import sqlite3

dbFile = 'sqLibrary.db'
bookTable = 'books'
bookCategoryTable='book_categories'
categoryTable = 'categories'


bookTableCreation = '''
CREATE TABLE IF NOT EXISTS books
    (id INTEGER PRIMARY KEY AUTOINCREMENT, 
     isbn, lccn, title, subtitle, authors, edition, 
     publisher, publish_year, publish_month, publish_location, 
     pages, pagination, weight, last_updated DATETIME DEFAULT current_timestamp, deleted BOOLEAN DEFAULT 0);

CREATE TABLE IF NOT EXISTS categories
    (cat_id INTEGER PRIMARY KEY, category STRING UNIQUE ON CONFLICT IGNORE);

CREATE TABLE IF NOT EXISTS book_categories
    (id INTEGER, cat_id INTEGER);
'''

columns = ['id', 'isbn', 'lccn',
           'title', 'subtitle', 'authors', 'edition', 
           'publisher', 'publish year', 'publish month', 'publish location', 
           'pages', 'pagination', 'weight', 'last updated', 'deleted']

bookTriggerCreation = '''

CREATE TRIGGER IF NOT EXISTS update_books_time AFTER UPDATE ON books
BEGIN
    UPDATE books SET last_updated = DATETIME('NOW') WHERE rowid = new.rowid;
END;

CREATE TRIGGER IF NOT EXISTS delete_book AFTER DELETE ON books
BEGIN
    DELETE FROM book_categories WHERE id = old.rowid;
END;

CREATE TRIGGER IF NOT EXISTS delete_category AFTER DELETE ON categories
BEGIN
    DELETE FROM book_categories WHERE cat_id = old.cat_id;
END;

CREATE TRIGGER IF NOT EXISTS insert_book_category_time AFTER INSERT ON book_categories
BEGIN
    UPDATE books SET last_updated = DATETIME('NOW') WHERE id = new.id;
END;
'''

################################3
# character escaping, etc for sql queries
#################################
def colify(s):
    return s.replace(" ","_").lower()

def stringify(v):
    return '"' + str(v).strip().replace('"','""') + '"'

###################################
# book functions
##################################
def addBook(book):
    conn = sqlite3.connect(dbFile)
    c = conn.cursor()
    cols = []
    vals = []
    for k,v in book.items():
        if v!="":
            cols.append(colify(k))
            vals.append(stringify(v))
    
    query = "INSERT INTO "+bookTable+" ("+", ".join(cols)+") VALUES ("+", ".join(vals)+");"
    c.execute(query)
    conn.commit()
    c.close()

def updateBook(book, bookID):
    conn = sqlite3.connect(dbFile)
    c = conn.cursor()
    updates=[]
    for k,v in book.items():
        updates.append(colify(k)+"="+stringify(v))
    query = "UPDATE "+bookTable+" SET " +  ", ".join(updates)+" WHERE id = " +str(bookID)+";"
    c.execute(query)
    conn.commit()
    c.close()

def getBooks():
    conn = sqlite3.connect(dbFile)
    c = conn.cursor()
    query = "SELECT * FROM "+bookTable+" WHERE deleted=0;"
    c.execute(query)
    books = [_query_to_book(b) for b in c]
    c.close()
    return books

def getBooksByCategory(cat):
    conn = sqlite3.connect(dbFile)
    c = conn.cursor()
    query = "SELECT "+",".join(map(colify,columns))+" FROM "+bookTable+" JOIN "+bookCategoryTable+" USING (id) WHERE cat_id = :id AND deleted=0;"
    c.execute(query,cat)
    books = [_query_to_book(b) for b in c]
    c.close()
    return books

def getRemovedBooks():
    conn = sqlite3.connect(dbFile)
    c = conn.cursor()
    query = "SELECT * FROM "+bookTable+" WHERE DELETED=1;"
    c.execute(query)
    books = [_query_to_book(b) for b in c]
    c.close()
    return books

def getBookByID(bookid):
    conn = sqlite3.connect(dbFile)
    c = conn.cursor()
    query = "SELECT * FROM "+bookTable+" WHERE id = "+str(bookid)+";"
    c.execute(query)
    book = _query_to_book(c.fetchone())
    c.close()
    return book

# removes book from catalogue
def removeBook(bookid):
    conn = sqlite3.connect(dbFile)
    c = conn.cursor()
    query = "UPDATE " +bookTable+ " SET deleted=1 WHERE id = "+str(bookid)+";"
    c.execute(query)
    conn.commit()
    c.close()

def removeBooks(books):
    conn = sqlite3.connect(dbFile)
    c = conn.cursor()
    query1 = "UPDATE " +bookTable+ " SET deleted=1 WHERE id = :id;"
    for book in books:
        c.execute(query1, book)
    conn.commit()
    c.close()

# restores trashed books
def restoreBooks(books):
    conn = sqlite3.connect(dbFile)
    c = conn.cursor()
    query1 = "UPDATE " +bookTable+ " SET deleted=0 WHERE id = :id;"
    for book in books:
        c.execute(query1,book)
    conn.commit()
    c.close()

# fully deletes book from removedBooks table
def deleteBook(bookid):
    conn = sqlite3.connect(dbFile)
    c = conn.cursor()
    query = "DELETE FROM " +bookTable+ " WHERE id = "+str(bookid)+";"
    c.execute(query)
    conn.commit()
    c.close()

def deleteBooks(books):
    conn = sqlite3.connect(dbFile)
    c = conn.cursor()
    query = "DELETE FROM " +bookTable+ " WHERE id = :id;"
    for book in books:
        c.execute(query, book)
    conn.commit()
    c.close()

def _query_to_book(book_query):
    # Make a dict out of column name and query results.
    # Empty entries return None, which are removed from the dict.
    return dict(filter(lambda t:t[1], zip(columns,book_query)))

#########################################
# Category related functions
########################################
def getBookCategories(book):
    conn = sqlite3.connect(dbFile)
    c = conn.cursor()
    query = "SELECT id,cat_id,category FROM "+bookCategoryTable+" JOIN "+categoryTable+" USING (cat_id) WHERE id = :id ;"
    c.execute(query,book)
    cats = []
    for book_id,cat_id,cat_name in c:
        cats.append({'id':book_id, 'cat_id':cat_id, 'category':cat_name})
    c.close()
    return cats

def categorizeBook(book, cats):
    conn = sqlite3.connect(dbFile)
    c = conn.cursor()
    query = "INSERT OR IGNORE INTO "+bookCategoryTable+" (id,cat_id) VALUES (?, ?);"
    for cat in cats:
        args = (book['id'],cat['id'])
        c.execute(query,args)
    conn.commit()
    c.close()

def uncategorizeBook(book, cats):
    conn = sqlite3.connect(dbFile)
    c = conn.cursor()
    query = "DELETE FROM "+bookCategoryTable+" WHERE (id = ? AND cat_id = ?);"
    for cat in cats:
        args = (book['id'],cat['id'])
        c.execute(query,args)
    conn.commit()
    c.close()

def getCategories():
    conn = sqlite3.connect(dbFile)
    c = conn.cursor()
    query = "SELECT cat_id, category FROM "+categoryTable+";"
    c.execute(query)
    cats = []
    for cat_id,cat in c:
        cats.append({'id':cat_id, 'category':cat})
    c.close()
    return cats

def addCategory(cat):
    conn = sqlite3.connect(dbFile)
    c = conn.cursor()
    query = "INSERT OR IGNORE INTO "+categoryTable+" (category) VALUES ("+stringify(cat)+");"
    c.execute(query)
    conn.commit()
    c.close()

def deleteCategories(cats):
    conn = sqlite3.connect(dbFile)
    c = conn.cursor()
    query1 = "DELETE FROM " +categoryTable+ " WHERE cat_id = :id;"
    for cat in cats:
        c.execute(query1, cat)
    conn.commit()
    c.close()

#########################################
# Database initialization
#########################################
def createBooksTable():
    conn = sqlite3.connect(dbFile)
    c = conn.cursor()
    c.executescript(bookTableCreation)
    conn.commit()
    c.close()

def createTriggers():
    conn = sqlite3.connect(dbFile)
    c = conn.cursor()
    c.executescript(bookTriggerCreation)
    conn.commit()
    c.close()


createBooksTable()
createTriggers()