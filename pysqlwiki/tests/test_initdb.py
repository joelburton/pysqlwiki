import unittest

from ..scripts.initializedb import main


class TestInitializeDB(unittest.TestCase):

    def test_usage(self):
        with self.assertRaises(SystemExit):
            main(argv=['foo'])

    def test_run(self):
        main(argv=['foo', 'development.ini', 'sqlalchemy.url=sqlite://'])