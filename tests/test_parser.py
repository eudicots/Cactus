import unittest

from cactus.utils import parseValues


class SimpleTest(unittest.TestCase):
    def testBootstrap(self):
        data = "name: Koen Bok\nage: 29\nIt's a nice boy."

        self.assertEqual(
            parseValues(data)[0],
            {'name': 'Koen Bok', 'age': '29'}
        )

        self.assertEqual(
            parseValues(data)[1],
            "It's a nice boy."
        )