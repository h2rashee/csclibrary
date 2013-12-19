import sqlite3

from  library import permissions

_catalogue_db_file = '/users/libcom/catalogue.db'
_book_table = 'books'
_book_category_table='book_categories'
_category_table = 'categories'

_checkout_db_file = '/users/libcom/checkout.db'
_checkout_table = 'checked_out'
_return_table = 'returned'

_checkout_table_creation = '''
CREATE TABLE IF NOT EXISTS checked_out
    (id INTEGER UNIQUE, uwid STRING, date_out DATETIME DEFAULT current_timestamp);

CREATE TABLE IF NOT EXISTS returned
    (id INTEGER, uwid STRING, date_out DATETIME, date_in DATETIME DEFAULT current_timestamp);
'''

_book_table_creation = '''
CREATE TABLE IF NOT EXISTS books
    (id INTEGER PRIMARY KEY AUTOINCREMENT, 
     isbn, lccn, title, subtitle, authors, edition, 
     publisher, publish_year, publish_month, publish_location, 
     pages, pagination, weight,
     last_updated DATETIME DEFAULT current_timestamp,
     deleted BOOLEAN DEFAULT 0);

CREATE TABLE IF NOT EXISTS categories
    (cat_id INTEGER PRIMARY KEY, category STRING UNIQUE ON CONFLICT IGNORE);

CREATE TABLE IF NOT EXISTS book_categories
    (id INTEGER, cat_id INTEGER);
'''

columns = ['id', 'isbn', 'lccn',
           'title', 'subtitle', 'authors', 'edition', 
           'publisher', 'publish year', 'publish month', 'publish location', 
           'pages', 'pagination', 'weight', 'last updated', 'deleted']

_book_trigger_creation = '''

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

CREATE TRIGGER IF NOT EXISTS insert_book_category_time AFTER INSERT
ON book_categories
BEGIN
    UPDATE books SET last_updated = DATETIME('NOW') WHERE id = new.id;
END;
'''

#################################
# character escaping, etc for sql queries
#################################
def _colify(s):
    return s.replace(" ","_").lower()

def _stringify(v):
    return '"' + str(v).strip().replace('"','""') + '"'

###################################
# book functions
##################################
@permissions.check_permissions(permissions.PERMISSION_LIBCOM)
def addBook(book):
    conn = sqlite3.connect(_catalogue_db_file)
    c = conn.cursor()
    cols = []
    vals = []
    for k,v in book.items():
        if v!="":
            cols.append(_colify(k))
            vals.append(_stringify(v))
    
    query = ("INSERT INTO "+_book_table+" ("+", ".join(cols)+") VALUES ("+
             ", ".join(vals)+");")
    c.execute(query)
    conn.commit()
    c.close()

@permissions.check_permissions(permissions.PERMISSION_LIBCOM)
def updateBook(book, bookID):
    '''
    Takes book attribute dictionary and a string representating the book ID
    number, and returns updates the book accordingly
    '''
    conn = sqlite3.connect(_catalogue_db_file)
    c = conn.cursor()
    updates=[]
    for k,v in book.items():
        updates.append(_colify(k)+"="+_stringify(v))
    query = ("UPDATE "+_book_table+" SET " +  ", ".join(updates)+" WHERE id = " +
             str(bookID)+";")
    c.execute(query)
    conn.commit()
    c.close()

def get_books():
    conn = sqlite3.connect(_catalogue_db_file)
    c = conn.cursor()
    query = "SELECT * FROM "+_book_table+" WHERE deleted=0;"
    c.execute(query)
    books = [_query_to_book(b) for b in c]
    c.close()
    return books

def getBooksByCategory(cat):
    '''
    Takes a string representating the category ID number, and returns
    non-deleted books in that category
    '''
    conn = sqlite3.connect(_catalogue_db_file)
    c = conn.cursor()
    query = ("SELECT "+",".join(map(_colify,columns))+" FROM "+_book_table+
             " JOIN "+_book_category_table+
             " USING (id) WHERE cat_id = :id AND deleted=0;")
    c.execute(query,cat)
    books = [_query_to_book(b) for b in c]
    c.close()
    return books

def getRemovedBooks():
    conn = sqlite3.connect(_catalogue_db_file)
    c = conn.cursor()
    query = "SELECT * FROM "+_book_table+" WHERE DELETED=1;"
    c.execute(query)
    books = [_query_to_book(b) for b in c]
    c.close()
    return books

def get_book(bookid):
    conn = sqlite3.connect(_catalogue_db_file)
    c = conn.cursor()
    query = "SELECT * FROM "+_book_table+" WHERE id = "+str(bookid)+";"
    c.execute(query)
    book = _query_to_book(c.fetchone())
    c.close()
    return book

# removes book from catalogue
@permissions.check_permissions(permissions.PERMISSION_LIBCOM)
def removeBook(bookid):
    conn = sqlite3.connect(_catalogue_db_file)
    c = conn.cursor()
    query = "UPDATE " +_book_table+ " SET deleted=1 WHERE id = "+str(bookid)+";"
    c.execute(query)
    conn.commit()
    c.close()

@permissions.check_permissions(permissions.PERMISSION_LIBCOM)
def removeBooks(books):
    conn = sqlite3.connect(_catalogue_db_file)
    c = conn.cursor()
    query1 = "UPDATE " +_book_table+ " SET deleted=1 WHERE id = :id;"
    for book in books:
        c.execute(query1, book)
    conn.commit()
    c.close()

# restores trashed books
@permissions.check_permissions(permissions.PERMISSION_LIBCOM)
def restoreBooks(books):
    conn = sqlite3.connect(_catalogue_db_file)
    c = conn.cursor()
    query1 = "UPDATE " +_book_table+ " SET deleted=0 WHERE id = :id;"
    for book in books:
        c.execute(query1,book)
    conn.commit()
    c.close()

# fully deletes book from books table
@permissions.check_permissions(permissions.PERMISSION_LIBCOM)
def deleteBook(bookid):
    conn = sqlite3.connect(_catalogue_db_file)
    c = conn.cursor()
    query = "DELETE FROM " +_book_table+ " WHERE id = "+str(bookid)+";"
    c.execute(query)
    conn.commit()
    c.close()

@permissions.check_permissions(permissions.PERMISSION_LIBCOM)
def deleteBooks(books):
    conn = sqlite3.connect(_catalogue_db_file)
    c = conn.cursor()
    query = "DELETE FROM " +_book_table+ " WHERE id = :id;"
    for book in books:
        c.execute(query, book)
    conn.commit()
    c.close()

def _query_to_book(book_query):
    # Make a dict out of column name and query results.
    # Empty entries return None, which are removed from the dict.
    return dict(filter(lambda t:t[1], zip(columns,book_query)))

def _query_to_book_checkout(book_query):
    # Make a dict out of column name and query results.
    # Empty entries return None, which are removed from the dict.
    b = _query_to_book(book_query)
    b['uwid'] = book_query[-2]
    b['date'] = book_query[-1]
    return b

#########################################
# Category related functions
########################################
def getBookCategories(book):
    conn = sqlite3.connect(_catalogue_db_file)
    c = conn.cursor()
    query = ("SELECT id,cat_id,category FROM "+_book_category_table+" JOIN "+
             _category_table+" USING (cat_id) WHERE id = :id ;")
    c.execute(query,book)
    cats = []
    for book_id,cat_id,cat_name in c:
        cats.append({'id':book_id, 'cat_id':cat_id, 'category':cat_name})
    c.close()
    return cats

@permissions.check_permissions(permissions.PERMISSION_LIBCOM)
def categorizeBook(book, cats):
    conn = sqlite3.connect(_catalogue_db_file)
    c = conn.cursor()
    query = ("INSERT OR IGNORE INTO "+_book_category_table+
             " (id,cat_id) VALUES (?, ?);")
    for cat in cats:
        args = (book['id'],cat['id'])
        c.execute(query,args)
    conn.commit()
    c.close()

@permissions.check_permissions(permissions.PERMISSION_LIBCOM)
def uncategorizeBook(book, cats):
    conn = sqlite3.connect(_catalogue_db_file)
    c = conn.cursor()
    query = "DELETE FROM "+_book_category_table+" WHERE (id = ? AND cat_id = ?);"
    for cat in cats:
        args = (book['id'],cat['id'])
        c.execute(query,args)
    conn.commit()
    c.close()

def getCategories():
    conn = sqlite3.connect(_catalogue_db_file)
    c = conn.cursor()
    query = "SELECT cat_id, category FROM "+_category_table+";"
    c.execute(query)
    cats = []
    for cat_id,cat in c:
        cats.append({'id':cat_id, 'category':cat})
    c.close()
    return cats

@permissions.check_permissions(permissions.PERMISSION_LIBCOM)
def addCategory(cat):
    conn = sqlite3.connect(_catalogue_db_file)
    c = conn.cursor()
    query = ("INSERT OR IGNORE INTO "+_category_table+" (category) VALUES ("
             +_stringify(cat)+");")
    c.execute(query)
    conn.commit()
    c.close()

@permissions.check_permissions(permissions.PERMISSION_LIBCOM)
def deleteCategories(cats):
    conn = sqlite3.connect(_catalogue_db_file)
    c = conn.cursor()
    query1 = "DELETE FROM " +_category_table+ " WHERE cat_id = :id;"
    for cat in cats:
        c.execute(query1, cat)
    conn.commit()
    c.close()

#########################################
# Book Checkout functions
#########################################
@permissions.check_permissions(permissions.PERMISSION_OFFICE)
def checkout_book(book_id, uwid):
    conn = sqlite3.connect(_checkout_db_file)
    c = conn.cursor()
    query = "INSERT INTO " + _checkout_table + " (id, uwid) VALUES (?, ?);"
    c.execute(query, (book_id, uwid))
    conn.commit()
    c.close()

@permissions.check_permissions(permissions.PERMISSION_OFFICE)
def return_book(book_id):
    conn = sqlite3.connect(_checkout_db_file)
    c = conn.cursor()
    query = "SELECT uwid,date_out FROM "+ _checkout_table + " WHERE id = :id ;"
    c.execute(query, {"id": book_id})
    tmp = c.fetchone()
    uwid = tmp[0]
    date_out = tmp[1]
    query = "INSERT INTO " + _return_table + " (id, uwid, date_out) VALUES (?, ?, ?);"
    query2 = "DELETE FROM " + _checkout_table + " WHERE id= :id ;"
    c.execute(query, (book_id, uwid, date_out))
    c.execute(query2, {"id": book_id});
    conn.commit()
    c.close()

def get_checkedout_books():
    '''
    retrieves checked out books. The returned books also have the fields
    uwid: ID of person who signed out the book, and
    date: date when the book was checked out
    '''
    conn = sqlite3.connect(_catalogue_db_file)
    c = conn.cursor()
    query = 'ATTACH "' + _checkout_db_file + '" AS co'
    c.execute(query)
    query = ("SELECT "+",".join(map(_colify,columns))+",uwid,date_out FROM "+_book_table+
             " JOIN co."+_checkout_table+
             " USING (id) ;")
    c.execute(query)
    books = [_query_to_book_checkout(b) for b in c]
    c.close()
    return books

def get_onshelf_books():
    '''
    retrieves checked out books. The returned books also have the fields
    uwid: ID of person who signed out the book, and
    date: date when the book was checked out
    '''
    conn = sqlite3.connect(_catalogue_db_file)
    c = conn.cursor()
    query = 'ATTACH "' + _checkout_db_file + '" AS co'
    c.execute(query)
    query = ("SELECT "+",".join(map(_colify,columns))+" FROM "+_book_table+
             " LEFT JOIN co."+_checkout_table+
             " USING (id) WHERE uwid ISNULL;")
    c.execute(query)
    books = [_query_to_book(b) for b in c]
    c.close()
    return books

#########################################
# Database initialization
#########################################
def _createBooksTable():
    conn = sqlite3.connect(_catalogue_db_file)
    c = conn.cursor()
    c.executescript(_book_table_creation)
    conn.commit()
    c.close()

def _createTriggers():
    conn = sqlite3.connect(_catalogue_db_file)
    c = conn.cursor()
    c.executescript(_book_trigger_creation)
    conn.commit()
    c.close()

def _create_checkout_table():
    conn = sqlite3.connect(_checkout_db_file)
    c = conn.cursor()
    c.executescript(_checkout_table_creation)
    conn.commit()
    c.close()

def initializeDatabase():
    _createBooksTable()
    _createTriggers()
    _create_checkout_table()
