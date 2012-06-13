import os

def fileList(path, relative=False, folders=False):
	"""
	Generate a recursive list of files from a given path.
	"""
	
	files = []
	
	for fileName in os.listdir(path):
		
		if fileName.startswith('.'):
			continue
		
		filePath = os.path.join(path, fileName)
		
		if os.path.isdir(filePath):
			if folders:
				files.append(filePath)
			files += fileList(filePath)
		else:
			files.append(filePath)
	
	if relative:
		files = map(lambda x: x[len(path)+1:], files)
		
	return files

def multiMap(f, items, workers=4):
	
	import threadpool
	
	pool = threadpool.ThreadPool(workers)
	requests = threadpool.makeRequests(f, items)
	
	[pool.putRequest(req) for req in requests]
	
	try:
		pool.wait()
	except KeyboardInterrupt:
		pass
