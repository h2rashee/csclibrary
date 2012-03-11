from urllib2 import urlopen
from json import load,dumps

def openLibrary(isbn):
    jsondata = urlopen("http://openlibrary.org/api/books?format=json&jscmd=data&bibkeys=ISBN:"+isbn)
    book = load(jsondata)
    if len(book)==0:
        return book
    else:
        return book["ISBN:"+isbn]

book = openLibrary("9780521714723")
if "title" in book: print book["title"]
if "subjects" in book: print dumps(book["subjects"], indent=2)
book = openLibrary("9780521565431")
if "title" in book: print book["title"]
if "subjects" in book: print dumps(book["subjects"], indent=2)
book = openLibrary("689145728392")
if "title" in book: print book["title"]
if "subjects" in book: print dumps(book["subjects"], indent=2)
book = openLibrary("9780321468932")
if "title" in book: print book["title"]
if "subjects" in book: print dumps(book["subjects"], indent=2)
book = openLibrary("9781555580414")
if "title" in book: print book["title"]
if "subjects" in book: print dumps(book["subjects"], indent=2)
