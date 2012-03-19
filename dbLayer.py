import sqlite3

dbFile = 'sqLibrary.db'
bookTable = 'books'

bookTableCreation = '''
CREATE TABLE IF NOT EXISTS books
    (id INTEGER PRIMARY KEY, 
     isbn, lccn, title, subtitle, authors, edition, 
     publisher, publish_year, publish_month, publish_location, 
     pages, pagination, weight)
'''

def colify(s):
    return s.replace(" ","_").lower()

# escapes strings and such
def stringify(v):
    return '"' + str(v).strip().replace('"','""') + '"'

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

def createBooksTable():
    conn = sqlite3.connect(dbFile)
    c = conn.cursor()
    c.execute(bookTableCreation)
    conn.commit()
    c.close()

createBooksTable()
