from urllib2 import urlopen,URLError
from json import load,dumps

""" Library Book Type Description:
The book is a dictionary of the form { string : a, ... }

Keys:
  required: (ideally)
    title - Book/Article title
    publisher - string containing semi-colon separated list eg. "UW Press; CSC, inc."
    authors - as above. each name is of the form "First Initials. Last" eg. "Calum T. Dalek; Conan T.B. Ladan"
  optional:
    subtitle - string
    edition - integer
    isbn - integer (it's preferred to use the isbn-13 rather than isbn-10)
    lccn - integer: library of congress catalogue number
    publish date - string of date (to make things easier to code/catalogue (won't be stored)
    publish year - int (this kind of thing will have to be confirmed by cataloguer)
    publish month - int
    publish location - like publisher
    
    pages - integer - just the number of pages
    pagination - string eg. "xviii, 1327-1850"
    weight - string (purely for interest's sake eg. "3lb." or "3 pounds"
    categories - list of strings?
"""


# look up data from openlibrary.org using isbn
def openLibrary_isbn(ISBN):
    isbn = str(ISBN)
    try:
        jsondata = urlopen("http://openlibrary.org/api/books?format=json&jscmd=data&bibkeys=ISBN:"+isbn, timeout=3)
    except URLError:
        return {}
    openBook = load(jsondata)
    if "ISBN:"+isbn not in openBook:
        return {'isbn':isbn,'title':'Book not found'}
    openBook = openBook["ISBN:"+isbn]
    # create my custom dict for books with the info we want.
    book = {"isbn" : isbn}
    book["title"]=openBook["title"]
    book["authors"]=""
    if "authors" in openBook:
        for v in openBook["authors"]:
            book['authors'] += "; " + v['name']
        book['authors'] = book['authors'][2:]
    book["publisher"]=""
    if "publishers" in openBook:
        for v in openBook["publishers"]:
            book["publisher"] += "; " + v['name']
        book['publisher'] = book['publisher'][2:]
    if "publish_places" in openBook:
        book["publish location"]=""
        for v in openBook["publish_places"]:
            book["publish location"] += "; " + v['name']
        book['publish location'] = book['publish location'][2:]

    # for lccn, there maybe be multiple values in the query. I'm just taking the first, but the full list may be useful
    if "lccn" in openBook['identifiers']:
        book["lccn"]=int(openBook['identifiers']['lccn'][0])
    if "publish_date" in openBook:
        book['publish date']=openBook['publish_date']
        #code to pull out year and month (hopefully)
    if "number_of_pages" in openBook:
        book["pages"]=openBook["number_of_pages"]
    if "pagination" in openBook:
        book["pagination"]=openBook["pagination"]
    if "weight" in openBook:
        book["weight"]=openBook["weight"]
    if "subtitle" in openBook:
        book["subtitle"]=openBook["subtitle"]
    return book

# look up data from openlibrary.org using lccn
def openLibrary_lccn(LCCN):
    lccn = str(LCCN)
    try:
        jsondata = urlopen("http://openlibrary.org/api/books?format=json&jscmd=data&bibkeys=lccn:"+lccn, timeout=3)
    except URLError:
        return {}
    openBook = load(jsondata)
    if "lccn:"+lccn not in openBook:
        return {'lccn':lccn,'title':'Book not found'}
    openBook = openBook["lccn:"+lccn]
    # create my custom dict for books with the info we want.
    book = {"lccn" : lccn}
    book["title"]=openBook["title"]
    book["authors"]=""
    if "authors" in openBook:
        for v in openBook["authors"]:
            book['authors'] += "; " + v['name']
        book['authors'] = book['authors'][2:]
    book["publisher"]=""
    if "publishers" in openBook:
        for v in openBook["publishers"]:
            book["publisher"] += "; " + v['name']
        book['publisher'] = book['publisher'][2:]
    if "publish_places" in openBook:
        book["publish location"]=""
        for v in openBook["publish_places"]:
            book["publish location"] += "; " + v['name']
        book['publish location'] = book['publish location'][2:]

    # for isbn, there maybe be multiple values in the query. I'm just taking the first, but the full list may be useful
    if "isbn_10" in openBook['identifiers']:
        book["isbn"]=int(openBook['identifiers']['isbn_10'][0])
    if "isbn_13" in openBook['identifiers']:
        book["isbn"]=int(openBook['identifiers']['isbn_13'][0])
    if "publish_date" in openBook:
        book['publish date']=openBook['publish_date']
        #code to pull out year and month (hopefully)
    if "number_of_pages" in openBook:
        book["pages"]=openBook["number_of_pages"]
    if "pagination" in openBook:
        book["pagination"]=openBook["pagination"]
    if "weight" in openBook:
        book["weight"]=openBook["weight"]
    if "subtitle" in openBook:
        book["subtitle"]=openBook["subtitle"]
    return book

