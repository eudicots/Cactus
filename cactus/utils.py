import os

def fileList(path, relative=False):
	"""
	Generate a recursive list of files from a given path.
	"""
	
	files = []
	
	for fileName in os.listdir(path):
		
		if fileName.startswith('.'):
			continue
		
		filePath = os.path.join(path, fileName)
		
		if os.path.isdir(filePath):
			files += fileList(filePath)
		else:
			files.append(filePath)
	
	if relative:
		files = map(lambda x: x[len(path)+1:], files)
		
	return files