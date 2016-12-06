import os
import logging

POST_IMAGES_PATH = 'blog-post-images/'
POST_IMAGES = {}
POSTS_PATH = 'posts/'

from cactus.utils import fileList
from cactus.file import File

def preBuild(site):
    """
    create a dict keyed on each post path.
    each value of the dict is an array of paths pointing
    to image filenames.
    """
    global POST_IMAGES

    # grab all posts
    posts = site.pages()
    posts = filter(lambda x: x.path.startswith(POSTS_PATH), posts)

    for page in posts:

        # Skip non html posts for obious reasons
        if not page.path.endswith('.html'):
            continue

        try:
            post_filename = os.path.splitext(os.path.basename(page.path))[0]
            images = fileList(os.path.join(site.paths['static'], POST_IMAGES_PATH + post_filename), relative=True)
            POST_IMAGES[page.path] = []
            for image in images:
                image_path = POST_IMAGES_PATH + post_filename + "/" + image
                POST_IMAGES[page.path].append(File(site,image_path))
        except Exception, e:
            logging.warning("Error processing blog images: %s" % e)


def preBuildPage(site, page, context, data):
    """
    Add the list of posts to every page context so we can
    access them from wherever on the site.
    """
    context['post_images'] = POST_IMAGES

    for path in POST_IMAGES:
        if path == page.path:
            context['images'] = POST_IMAGES[path]

    return context, data
