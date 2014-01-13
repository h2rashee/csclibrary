from distutils.core import setup
setup(name="librarian",
      description="Library Management Software for CSC",
      author="jladan",
      version="1.0",
      packages=['library','library.interface'],
      scripts=["librarian"]
      )
