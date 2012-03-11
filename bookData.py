from urllib2 import urlopen
from json import load,dumps

def openLibrary(isbn):
    jsondata = urlopen("http://openlibrary.org/api/books?format=json&jscmd=data&bibkeys=ISBN:"+isbn)
    openBook = load(jsondata)
    if "ISBN:"+isbn not in openBook:
        return openBook
    openBook = openBook["ISBN:"+isbn]
    # create my custom dict for books with the info we want.
    book = {"isbn" : isbn}
    book['title']=openbook['title']
    # continue with the rest later

book = openLibrary("9780521714723")
print dumps(book, indent=2)
book = openLibrary("9780521565431")
print dumps(book, indent=2)
book = openLibrary("689145728392")
print dumps(book, indent=2)
book = openLibrary("9780321468932")
print dumps(book, indent=2)
book = openLibrary("9781555580414")
print dumps(book, indent=2)
