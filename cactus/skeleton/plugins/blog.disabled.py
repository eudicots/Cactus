import os
import datetime
import logging

ORDER = 999
DEFAULT_PATH = 'posts/'
POSTS = []

from django.template import Context
from django.template.loader import get_template
from django.template.loader_tags import BlockNode, ExtendsNode

def get_post_meta(name, page, warn=True):
    """
    Given a string 'name', try to find a matching value either in the page
    context or in config.json under blog['defaults']
    """
    context = page.context()
    defaults = page.site.config.get('blog', {}).get('defaults')

    if name in context:
        return context.get(name, '')
    elif name in defaults:
        return defaults.get(name, '')
    else:
        if warn:
            logging.warning("%s - No %s found" % (page.path, name))
        return ''

def get_post_date(page):
    """
    Look for a date in the page context, otherwise use the file modification
    date.

    Accepts dd-mm-yyyy or yyyy-mm-dd
    """
    manual_date = get_post_meta('date', page, False)
    bad_date = False

    if manual_date:
        for format in ['%Y-%m-%d', '%d-%m-%Y']:
            try:
                return datetime.datetime.strptime(manual_date, format)
            except:
                bad_date = True
                continue
    
        if bad_date:
            logging.warning("%s - Date isn't YYYY-MM-DD or DD-MM-YYYY" % (page.path))

    mod_time = os.path.getmtime(page.full_source_path)
    return datetime.datetime.fromtimestamp(mod_time)

def get_post_output_path(path):
    """
    Return a .html path for build/link purposes
    """
    return path.replace('.md', '.html')

def preBuild(site):
    """
    Find and parse all .md files in the posts_path directory, add them to POSTS
    """
    global POSTS

    posts_path = site.config.get('blog', {}).get('path', DEFAULT_PATH)

    # Build all the posts
    for page in site.pages():
        if page.path.startswith(posts_path):

            # Skip non md posts for obvious reasons
            if not page.path.endswith('.md'):
                continue

            # Skip posts with 'status: draft' in the context
            if get_post_meta('status', page, False) == 'draft':
                continue

            # Workaround to actually get a hold of the context-stripped
            # data returned by page.parse_context()
            context, clean_data = page.parse_context(page.data())

            # Build a context for each post
            post_context = {}
            post_context['title'] = get_post_meta('title', page)
            post_context['author'] = get_post_meta('author', page)
            post_context['date'] = get_post_date(page)
            post_context['path'] = get_post_output_path(page.path)
            post_context['body'] = clean_data
            post_context['template'] = get_post_meta('template', page)

            POSTS.append(post_context)

            # Override build path so we output an .html page
            page.build_path = get_post_output_path(page.path)

    # Sort the posts by date
    POSTS = sorted(POSTS, key=lambda x: x['date'])
    POSTS.reverse()

    indexes = xrange(0, len(POSTS))

    for i in indexes:
        if i+1 in indexes: POSTS[i]['prev_post'] = POSTS[i+1]
        if i-1 in indexes: POSTS[i]['next_post'] = POSTS[i-1]


def preBuildPage(page, context, data):
    """
    Add the list of posts to every page context so we can
    access them from wherever on the site.

    For posts, inject the post's template
    """
    context['posts'] = POSTS
    posts_path = page.site.config.get('blog', {}).get('path', DEFAULT_PATH)

    # If we're building a post, loop through POSTS to find the current one
    if page.path.startswith(posts_path):
        for post in POSTS:
            if post['path'] == get_post_output_path(page.path):

                # Add the current post to the page's context as 'post'
                context.update(post)

                # Get the full path to the post's template
                full_template_path = ''.join([page.site.template_path, '/',
                                             post['template']])

                # Load and inject the template contents into the page we're building
                with open(full_template_path, 'rU') as f:
                    try:
                        data = f.read().decode('utf-8')
                    except:
                        logging.warning("%s - Could not process template", post.path)

    return context, data