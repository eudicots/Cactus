import json

class Config(object):
	
	def __init__(self, path):
		self.path = path
		self.load()
	
	def get(self, key):
		return self._data.get(key, None)
	
	def set(self, key, value):
		self._data[key] = value
	
	def load(self):
		try:
			self._data = json.load(open(self.path, 'r'))
		except:
			self._data = {}
	
	def write(self):
		json.dump(self._data, open(self.path, 'w'), sort_keys=True, indent=4)