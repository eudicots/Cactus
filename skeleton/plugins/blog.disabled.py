import os
import datetime
import logging

POSTS_PATH = 'posts/'
POSTS = []

def preBuild(site):
	
	global POSTS
	
	# Build all the posts
	for page in site.pages():
		if page.path.startswith(POSTS_PATH):
			
			if not page.path.endswith('.html'):
				continue
			
			def find(name):
				c = page.context()
				if not name in c:
					logging.info("Missing info '%s' for post %s" % (name, page.path))
					return ''
				return c.get(name, '')
			
			postContext = {}
			postContext['title'] = find('title')
			postContext['author'] = find('author')
			postContext['date'] = find('date')
			postContext['path'] = page.path
			
			# Parse the date into a date object
			try:
				postContext['date'] = datetime.datetime.strptime(postContext['date'], '%d-%m-%Y')
			except Exception, e:
				logging.warning("Date format not correct for page %s, should be dd-mm-yy\n%s" % (page.path, e))
				continue
			
			POSTS.append(postContext)
	
	# Sort the posts by date
	POSTS = sorted(POSTS, key=lambda x: x['date'])
	POSTS.reverse()
	
	indexes = xrange(0, len(POSTS))
	
	for i in indexes:
		if i+1 in indexes: POSTS[i]['prevPost'] = POSTS[i+1]
		if i-1 in indexes: POSTS[i]['nextPost'] = POSTS[i-1]


def preBuildPage(site, page, context, data):
	
	context['posts'] = POSTS
	
	for post in POSTS:
		if post['path'] == page.path:
			context.update(post)
	
	return context, data