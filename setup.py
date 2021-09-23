from distutils.core import setup

setup(
      name="sqlite-ctrlx",
      version="1.0.01",
      description="Simple SQLite database",
      author="A. Fouraker",
      packages=['app'],
      # https://stackoverflow.com/questions/1612733/including-non-python-files-with-setup-py
      scripts=['main.py'],
      license="Copyright (c) 2020-2021 Bosch Rexroth AG, Licensed under MIT License"
 )
