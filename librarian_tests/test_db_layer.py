import contextlib
import os
import sqlite3
import unittest

import db_layer
import exceptions
import permissions

class TestDBSetup(unittest.TestCase):
    def tearDown(self):
        try:
            os.remove(db_layer.dbFile)
        except FileNotFoundError:
            pass

    def test_db_setup(self):
        conn = sqlite3.connect(db_layer.dbFile)

        with self.assertRaises(sqlite3.OperationalError):
            with contextlib.closing(conn.cursor()) as c:
                c.execute('SELECT * FROM books;')

        db_layer.initializeDatabase()

        with contextlib.closing(conn.cursor()) as c:
            c.execute('SELECT * FROM books;')

    def test_existing_db_file(self):
        conn = sqlite3.connect(db_layer.dbFile)
        db_layer.initializeDatabase()
        with contextlib.closing(conn.cursor()) as c:
            c.execute('INSERT INTO books (isbn) VALUES (1111111111);')
        conn.commit()

        db_layer.initializeDatabase()
        with contextlib.closing(conn.cursor()) as c:
            c.execute('SELECT isbn FROM books;')
            rows = list(c)

        self.assertEqual([1111111111], [row[0] for row in rows])

class TestDBFunctions(unittest.TestCase):
    maxDiff = None

    def assertISBNs(self, expected_isbns, book_dicts):
        expected_isbns = frozenset(expected_isbns)
        actual_isbns = frozenset(book.get('isbn') for book in book_dicts)
        self.assertEqual(expected_isbns, actual_isbns)

    def assertCategories(self, expected_categories, book_dicts):
        expected_categories = frozenset(expected_categories)
        actual_categories = frozenset(book['category'] for book in book_dicts)
        self.assertEqual(expected_categories, actual_categories)

    def setUp(self):
        db_layer.initializeDatabase()
        permissions._CURRENT_GROUPS_GETTER = lambda: ["office", "libcom"]

        conn = sqlite3.connect(db_layer.dbFile)

        with contextlib.closing(conn.cursor()) as c:
            c.execute('''
INSERT INTO books (isbn, lccn, title, subtitle, authors, edition, publisher,
                   publish_year, publish_month, publish_location, pages,
                   pagination, weight)
VALUES
(1111111111111, 2222222222, 'Attack of the bad code', 'Return of the GOTO',
 'cdchawthorne', '1st', 'CSC Publishing', '1992', 'June', 'Waterloo, Canada',
 '496', 'xxvi, 493 p', '1 kg'),
(3333333333333, 4444444444, 'Star Wars VI--Return of the Jedi', 'Now in text!',
 'George Lucas', '2nd', 'Lucas Film', '2013', 'November', 'Somewhere, USA',
 '8128', 'xx, 8100 p', '10 kg');
            ''')

        with contextlib.closing(conn.cursor()) as c:
            c.execute('''
INSERT INTO books (isbn, lccn, deleted) VALUES
(5555555555555, NULL, 0), (NULL, 6666666666, 0), (7777777777777, NULL, 1);
            ''')

        with contextlib.closing(conn.cursor()) as c:
            c.execute('''
INSERT INTO categories (category)
VALUES ('My special category'), ('My second special category');
            ''')

        with contextlib.closing(conn.cursor()) as c:
            c.execute('''SELECT rowid, isbn, lccn, last_updated FROM books;''')
            for row in c:
                if row[1] == 1111111111111:
                    self.book0_id = row[0]
                    self.book0_last_updated = row[3]
                elif row[1] == 3333333333333:
                    self.book1_id = row[0]
                    self.book1_last_updated = row[3]
                elif row[1] == 5555555555555:
                    self.book2_id = row[0]
                    self.book2_last_updated = row[3]
                elif row[2] == 6666666666:
                    self.book3_id = row[0]
                    self.book3_last_updated = row[3]
                elif row[1] == 7777777777777:
                    self.book4_id = row[0]
                    self.book4_last_updated = row[3]
                else:
                    self.assertTrue(False,
                                    "Unexpected data in DB during setup")

        with contextlib.closing(conn.cursor()) as c:
            c.execute('''SELECT rowid, category FROM categories;''')
            for row in c:
                if row[1] == 'My special category':
                    self.category0_id = row[0]
                elif row[1] == 'My second special category':
                    self.category1_id = row[0]

        with contextlib.closing(conn.cursor()) as c:
            c.execute('''
INSERT INTO book_categories (id, cat_id) VALUES (?, ?), (?, ?), (?, ?), (?, ?);
            ''',
                      (self.book1_id, self.category0_id,
                       self.book1_id, self.category1_id,
                       self.book0_id, self.category1_id,
                       self.book2_id, self.category1_id,
                      )
            )

        conn.commit()

    def tearDown(self):
        try:
            os.remove(db_layer.dbFile)
        except FileNotFoundError:
            pass

    def test_getBooks(self):
        books = db_layer.getBooks()

        expected_book0 = {
                'id': self.book0_id,
                'isbn': 1111111111111,
                'lccn': 2222222222,
                'title': 'Attack of the bad code',
                'subtitle': 'Return of the GOTO',
                'authors': 'cdchawthorne',
                'edition': '1st',
                'publisher': 'CSC Publishing',
                'publish year': '1992',
                'publish month': 'June',
                'publish location': 'Waterloo, Canada',
                'pages': '496',
                'pagination': 'xxvi, 493 p',
                'weight': '1 kg',
                'last updated': self.book0_last_updated,
        }

        found_book0 = False
        for book in books:
            if book.get('isbn') == 1111111111111:
                found_book0 = True
                self.assertEqual(book, expected_book0)

        self.assertTrue(found_book0, "getBooks() missing book0")

        expected_isbns = [1111111111111, 3333333333333, 5555555555555, None]
        self.assertISBNs(expected_isbns, books)

    def test_getBooksByCategory(self):
        books = db_layer.getBooksByCategory(str(self.category0_id))
        expected_isbns = [3333333333333]
        self.assertISBNs(expected_isbns, books)

    def test_getRemovedBooks(self):
        books = db_layer.getRemovedBooks()
        expected_isbns = [7777777777777]
        self.assertISBNs(expected_isbns, books)

    def test_addBook(self):
        db_layer.addBook({'isbn': 8888888888888, 'title': 'New book'})
        
        conn = sqlite3.connect(db_layer.dbFile)

        with contextlib.closing(conn.cursor()) as c:
            c.execute('''
SELECT title FROM books WHERE isbn = '8888888888888';
            ''')
            rows = list(c)
        
        self.assertEqual(['New book'], [row[0] for row in rows])

    def test_updateBook(self):
        db_layer.updateBook({'title': 'Attack of the questionable code'},
                            str(self.book0_id))

        conn = sqlite3.connect(db_layer.dbFile)

        with contextlib.closing(conn.cursor()) as c:
            c.execute('''
SELECT title FROM books WHERE id = ?;
            ''', (self.book0_id,))
            rows = list(c)
        
        self.assertEqual(['Attack of the questionable code'],
                         [row[0] for row in rows])

    def test_getBookById(self):
        book = db_layer.getBookByID(self.book0_id)
        self.assertEqual('Attack of the bad code', book['title'])

    def test_removeBook(self):
        conn = sqlite3.connect(db_layer.dbFile)
        with contextlib.closing(conn.cursor()) as c:
            c.execute('''
SELECT deleted FROM books WHERE id = ?;
            ''', (self.book1_id,))
            rows = list(c)

        self.assertEqual([0], [row[0] for row in rows])

        db_layer.removeBook(self.book1_id)

        with contextlib.closing(conn.cursor()) as c:
            c.execute('''
SELECT deleted FROM books WHERE id = ?;
            ''', (self.book1_id,))
            rows = list(c)

        self.assertEqual([1], [row[0] for row in rows])

    def test_removeBooks(self):
        conn = sqlite3.connect(db_layer.dbFile)
        with contextlib.closing(conn.cursor()) as c:
            c.execute('''
SELECT deleted FROM books WHERE id = ? OR id = ?;
            ''', (self.book0_id, self.book1_id,))
            rows = list(c)

        self.assertEqual([0,0], [row[0] for row in rows])

        db_layer.removeBooks([str(self.book0_id), str(self.book1_id)])

        with contextlib.closing(conn.cursor()) as c:
            c.execute('''
SELECT deleted FROM books WHERE id = ? OR id = ?;
            ''', (self.book0_id, self.book1_id))
            rows = list(c)

        self.assertEqual([1,1], [row[0] for row in rows])

    def test_deleteBook(self):
        conn = sqlite3.connect(db_layer.dbFile)

        with contextlib.closing(conn.cursor()) as c:
            c.execute('SELECT COUNT(*) FROM books WHERE id = ? OR id = ?;',
                      (self.book0_id, self.book1_id))
            count = c.fetchone()[0]

        self.assertEqual(2, count)

        db_layer.deleteBook(self.book0_id)
        db_layer.deleteBook(self.book1_id)

        with contextlib.closing(conn.cursor()) as c:
            c.execute('SELECT COUNT(*) FROM books WHERE id = ? OR id = ?;',
                      (self.book0_id, self.book1_id))
            count = c.fetchone()[0]

        self.assertEqual(0, count)

    # Code duplication? What's that?
    def test_deleteBooks(self):
        conn = sqlite3.connect(db_layer.dbFile)

        with contextlib.closing(conn.cursor()) as c:
            c.execute('SELECT COUNT(*) FROM books WHERE id = ? OR id = ?;',
                      (self.book0_id, self.book1_id))
            count = c.fetchone()[0]

        self.assertEqual(2, count)

        db_layer.deleteBooks([str(self.book0_id), str(self.book1_id)])

        with contextlib.closing(conn.cursor()) as c:
            c.execute('SELECT COUNT(*) FROM books WHERE id = ? OR id = ?;',
                      (self.book0_id, self.book1_id))
            count = c.fetchone()[0]

        self.assertEqual(0, count)

    def test_getBookCategories(self):
        categories = db_layer.getBookCategories(str(self.book1_id))
        expected_categories = ['My special category',
                               'My second special category']
        self.assertCategories(expected_categories, categories)

        categories = db_layer.getBookCategories(str(self.book0_id))
        expected_categories = ['My second special category']
        self.assertCategories(expected_categories, categories)

        categories = db_layer.getBookCategories(str(self.book3_id))
        expected_categories = []
        self.assertCategories(expected_categories, categories)

    def test_categorizeBook(self):
        conn = sqlite3.connect(db_layer.dbFile)
        with contextlib.closing(conn.cursor()) as c:
            c.execute('SELECT cat_id FROM book_categories WHERE id = ?;',
                      (self.book3_id,))
            rows = list(c)

        self.assertEqual([], rows)

        db_layer.categorizeBook({'id': self.book3_id},
                                [{'id': self.category0_id},
                                 {'id': self.category1_id}])

        with contextlib.closing(conn.cursor()) as c:
            c.execute('SELECT cat_id FROM book_categories WHERE id = ?;',
                      (self.book3_id,))
            rows = list(c)

        self.assertEqual(frozenset([self.category0_id, self.category1_id]),
                         frozenset(row[0] for row in rows))

    def test_uncategorizeBook(self):
        conn = sqlite3.connect(db_layer.dbFile)
        with contextlib.closing(conn.cursor()) as c:
            c.execute('SELECT cat_id FROM book_categories WHERE id = ?;',
                      (self.book1_id,))
            rows = list(c)

        self.assertEqual(frozenset([self.category0_id, self.category1_id]),
                         frozenset(row[0] for row in rows))

        db_layer.uncategorizeBook({'id': self.book1_id},
                                  [{'id': self.category0_id},
                                   {'id': self.category1_id}])

        with contextlib.closing(conn.cursor()) as c:
            c.execute('SELECT cat_id FROM book_categories WHERE id = ?;',
                      (self.book3_id,))
            rows = list(c)

        self.assertEqual([], rows)

    def test_getCategories(self):
        categories = db_layer.getCategories()
        expected_categories = ['My special category',
                               'My second special category']
        self.assertCategories(expected_categories, categories)

    def test_addCategory(self):
        conn = sqlite3.connect(db_layer.dbFile)
        with contextlib.closing(conn.cursor()) as c:
            c.execute('SELECT category FROM categories;')
            rows = list(c)

        expected_categories = ['My special category',
                               'My second special category']
        self.assertEqual(frozenset(expected_categories),
                         frozenset(row[0] for row in rows))
        
        db_layer.addCategory('My third special category')

        with contextlib.closing(conn.cursor()) as c:
            c.execute('SELECT category FROM categories;')
            rows = list(c)

        expected_categories.append('My third special category')
        self.assertEqual(frozenset(expected_categories),
                         frozenset(row[0] for row in rows))

    def test_deleteCategories(self):
        conn = sqlite3.connect(db_layer.dbFile)

        with contextlib.closing(conn.cursor()) as c:
            c.execute('SELECT COUNT(*) FROM categories;')
            rows = list(c)

        self.assertEqual(2, rows[0][0])

        with contextlib.closing(conn.cursor()) as c:
            c.execute('SELECT COUNT(*) FROM book_categories;')
            rows = list(c)

        self.assertEqual(4, rows[0][0])

        db_layer.deleteCategories([str(self.category1_id)])

        with contextlib.closing(conn.cursor()) as c:
            c.execute('SELECT COUNT(*) FROM categories;')
            rows = list(c)

        self.assertEqual(1, rows[0][0])

        with contextlib.closing(conn.cursor()) as c:
            c.execute('SELECT COUNT(*) FROM book_categories;')
            rows = list(c)

        self.assertEqual(1, rows[0][0])

class TestDBFunctionPermissions(unittest.TestCase):
    def setUp(self):
        db_layer.initializeDatabase()
        # Need book in database or getBookByID will error when we test it
        conn = sqlite3.connect(db_layer.dbFile)

        with contextlib.closing(conn.cursor()) as c:
            c.execute('INSERT INTO books (isbn) VALUES (5555555555555);')

        with contextlib.closing(conn.cursor()) as c:
            c.execute('SELECT rowid FROM books;')
            self.dummy_book_id = c.fetchone()[0]

    def tearDown(self):
        try:
            os.remove(db_layer.dbFile)
        except FileNotFoundError:
            pass

    def verify_permissions(self, fn, authorized_groups, unauthorized_groups):
        for group in authorized_groups:
            permissions._CURRENT_GROUPS_GETTER = lambda: [group]
            fn()

        for group in unauthorized_groups:
            permissions._CURRENT_GROUPS_GETTER = lambda: [group]
            with self.assertRaises(exceptions.PermissionsError):
                fn()

    def test_db_function_permissions(self):
        function_dicts = [
                {'fn': lambda: db_layer.addBook({'isbn': 8888888888888}),
                 'authorized_groups': ['libcom'],
                 'unauthorized_groups': ['office', 'unauthorized']},
                {'fn': lambda: db_layer.updateBook({'isbn': 9999999999999}, 0),
                 'authorized_groups': ['libcom'],
                 'unauthorized_groups': ['office', 'unauthorized']},
                {'fn': lambda: db_layer.getBooks(),
                 'authorized_groups': ['libcom', 'office', 'unauthorized'],
                 'unauthorized_groups': []},
                {'fn': lambda: db_layer.getBooksByCategory('0'),
                 'authorized_groups': ['libcom', 'office', 'unauthorized'],
                 'unauthorized_groups': []},
                {'fn': lambda: db_layer.getRemovedBooks(),
                 'authorized_groups': ['libcom', 'office', 'unauthorized'],
                 'unauthorized_groups': []},
                {'fn': lambda: db_layer.getBookByID(self.dummy_book_id),
                 'authorized_groups': ['libcom', 'office', 'unauthorized'],
                 'unauthorized_groups': []},
                {'fn': lambda: db_layer.removeBook(0),
                 'authorized_groups': ['libcom'],
                 'unauthorized_groups': ['office', 'unauthorized']},
                {'fn': lambda: db_layer.removeBooks(['0']),
                 'authorized_groups': ['libcom'],
                 'unauthorized_groups': ['office', 'unauthorized']},
                {'fn': lambda: db_layer.restoreBooks(['0']),
                 'authorized_groups': ['libcom'],
                 'unauthorized_groups': ['office', 'unauthorized']},
                {'fn': lambda: db_layer.deleteBook(0),
                 'authorized_groups': ['libcom'],
                 'unauthorized_groups': ['office', 'unauthorized']},
                {'fn': lambda: db_layer.deleteBooks(['0']),
                 'authorized_groups': ['libcom'],
                 'unauthorized_groups': ['office', 'unauthorized']},
                {'fn': lambda: db_layer.getBookCategories('0'),
                 'authorized_groups': ['libcom', 'office', 'unauthorized'],
                 'unauthorized_groups': []},
                {'fn': lambda: db_layer.categorizeBook({'id':'0'}, []),
                 'authorized_groups': ['libcom'],
                 'unauthorized_groups': ['office', 'unauthorized']},
                {'fn': lambda: db_layer.uncategorizeBook({'id':'0'}, []),
                 'authorized_groups': ['libcom'],
                 'unauthorized_groups': ['office', 'unauthorized']},
                {'fn': lambda: db_layer.getCategories(),
                 'authorized_groups': ['libcom', 'office', 'unauthorized'],
                 'unauthorized_groups': []},
                {'fn': lambda: db_layer.addCategory('Cat5'),
                 'authorized_groups': ['libcom'],
                 'unauthorized_groups': ['office', 'unauthorized']},
                {'fn': lambda: db_layer.deleteCategories([]),
                 'authorized_groups': ['libcom'],
                 'unauthorized_groups': ['office', 'unauthorized']},
        ]

        for function_dict in function_dicts:
            self.verify_permissions(function_dict['fn'],
                                    function_dict['authorized_groups'],
                                    function_dict['unauthorized_groups'])
