"""
Modify `config.json` to set a custom blog path, default author name, or date pattern used to parse metadata. The defaults are:
"blog": {
    "path": "blog",
    "author": "Unknown",
    "date-format": "%d-%m-%Y"
}
"""

import os
import datetime
import logging

ORDER = 999
POSTS = []

from django.template import Context
from django.template.loader import get_template
from django.template.loader_tags import BlockNode, ExtendsNode

def getNode(template, context=Context(), name='subject'):
    """
    Get django block contents from a template.
    http://stackoverflow.com/questions/2687173/
    django-how-can-i-get-a-block-from-a-template
    """
    for node in template:
        if isinstance(node, BlockNode) and node.name == name:
            return node.render(context)
        elif isinstance(node, ExtendsNode):
            return getNode(node.nodelist, context, name)
    raise Exception("Node '%s' could not be found in template." % name)


def preBuild(site):

    global POSTS
    siteContext = site.context()
    
    blog = site.config.get('blog', {})
    blogPath = os.path.join(blog.get('path', 'blog'), '')
    dateFormat = blog.get('date-format', '%d-%m-%Y')
    defaultAuthor = blog.get('author', 'Unknown')

    # Build all the posts
    for page in site.pages():
        if page.path.startswith(blogPath):

            # Skip non html posts for obious reasons
            if not page.path.endswith('.html'):
                continue

            # Find a specific defined variable in the page context,
            # and throw a warning if we're missing it.
            def find(name):
                c = page.context()
                if not name in c:
                    logging.info("Missing info '%s' for post %s" % (name, page.path))
                    return ''
                return c.get(name, '')

            # Build a context for each post
            context = {'__CACTUS_CURRENT_PAGE__': page,}
            context.update(siteContext)

            postContext = {}
            postContext['title'] = find('title')
            postContext['author'] = find('author') or defaultAuthor
            postContext['date'] = find('date')
            postContext['path'] = page.final_url
            postContext['body'] = getNode(get_template(page.path), context=Context(context), name="body")

            # Parse the date into a date object
            try:
                postContext['date'] = datetime.datetime.strptime(postContext['date'], dateFormat)
            except Exception as e:
                logging.warning("Date format not correct for page %s, should be %s\n%s" % (page.path, dateFormat, e))
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
    """
    Add the list of posts to every page context so we can
    access them from wherever on the site.
    """
    context['posts'] = POSTS

    for post in POSTS:
        if post['path'] == page.final_url:
            context.update(post)

    return context, data
