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
			
			c = page.context()
			
			postContext = {}
			postContext['title'] = c.get('title', '')
			postContext['author'] = c.get('author', '')
			postContext['date'] = c.get('date', '')
			postContext['path'] = page.path
			
			# Parse the date into a date object
			postContext['date'] = datetime.datetime.strptime(postContext['date'], '%d-%m-%Y')
			
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