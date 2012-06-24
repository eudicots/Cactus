import os
import shutil
import codecs
import unittest

from cactus import Site
from cactus.utils import parseValues

class SimpleTest(unittest.TestCase):
	
	def testBootstrap(self):

		data = """
		name: Koen Bok
		age: 29
		It's a nice boy.
		"""

		self.assertEqual(
			parseValues(data)[0], 
			{'name': 'Koen Bok', 'age': '29'}
		)

		self.assertEqual(
			parseValues(data)[1], 
			'\t\tIt\'s a nice boy.\n\t\t'
		)