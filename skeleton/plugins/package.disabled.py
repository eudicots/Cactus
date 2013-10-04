import hashlib
import itertools
import imp
import sys
import os
import re
import pipes
import AssetPackager
from bs4 import BeautifulSoup

# Packager!
# Puts CSS and JavaScript files referenced in your html together as one, compressed
# (via YUI compressor) and concatenated, with the help of the AssetPackager.
#
# Having lots of HTTP requests is expensive. In an ideal world your page would have one
# CSS file and one JS file. It's possible to get overagressive here and include something
# big that is only needed on, say, 1 one of your rarely used pages. There's lots of
# tradeoffs and heuristics we could use based on frequency of requests and likelihood
# of assets being requested at a given time. Packager takes a simple approach: analyze
# the assets that appear on each page, and bucket them according to which ones appear
# together. In the simplest case, a site with one page that references assets A,B,C
# will be able to confidently create a single package (file) containing all 3. If we
# add 12 more pages to the site and they all contain A,B, packager will build one package
# of A,B and one of C since C doesn't *always* appear with A,B. It's naive, but it works.

# Packager is NOT a dependency manager! It's naive and just looks at an HTML tree
# and figures out a resonable way to bundle things together to reduce requests.

# Features:
# Preserves original asset order.
# Supports blacklisting of assest with data-nopackage
# Downloads and packages remote assets so you can package your site's base function with your js framework
# Compresses all CSS/JS, even if it's included inline

# Known limitations:
# 1. Does not support @import syntax in css
# 2. If your script tags aren't all in one spot in the markup, it's possible that packaging could
#    force them all together. This is something to be aware of if you've written scripts that
#    expect themselves to come both before and after some other html (or if you're doing some
#    sketchy document.writes or something).


## INSTALLATION:
# sudo pip install AssetPackager
# sudo pip install beautifulsoup4



## CONFIGURATION ##
# For trying packaging on localhost or debugging, set to True which runs packaging on every build.
# Otherwise set to False to only package on deploy. You may have to clean up autogen files manually:
PACKAGE_LOCALLY_DEBUG = False
INCLUDE_REMOTE_ASSETS = True # whether to fetch and package remotely hosted files
MINIFY_FILENAMES = False # otherwise all package filenames will be a concatenation of the filenames within
COMPRESS_PACKAGES = True
INCLUDE_ORIGINAL_FILENAMES_IN_COMMENTS = True
PACKAGE_CSS = True
PACKAGE_JS = True
AUTOGEN_PREFIX = 'cx_' # file prefix for packaged files


localpath_re = re.compile('^(?!http|\/\/)')
relativedir_re = re.compile('^(\.+\/)+')
assets = []
inline_assets = set()

def _isLocalFile(path):
  return re.match(localpath_re, path)

def _staticPath(site, includeBuild=False):
  static = os.path.relpath(site.paths['static'], site.path)
  if includeBuild:
    static = os.path.join(site.paths['build'], static)
  return static

def _withoutStatic(site, url):
  return os.path.relpath(url, _staticPath(site))

def _relToStaticBuild(site, url):
  return os.path.join(_staticPath(site, includeBuild=True), url)

def _getDir(path):
  if os.path.isdir(path):
    return path
  else:
    return os.path.dirname(path)

def _getLinks(soup):
  all_links = soup.find_all('link', attrs={
    'rel': 'stylesheet',
    'href': True if INCLUDE_REMOTE_ASSETS else localpath_re
  }) + soup.find_all('style')
  return [x for x in all_links if not 'data-nopackage' in x.attrs]

def _getScripts(soup):
  all_scripts = soup.find_all('script', attrs={ # scripts with src's
    'src': True if INCLUDE_REMOTE_ASSETS else localpath_re
  }) + soup.find_all('script', attrs={'src': None}) # ... and scripts without (inline)
  return [x for x in all_scripts if not 'data-nopackage' in x.attrs]

def _getAssetFrom(tag, site, save=False):
  url = tag.get('href') or tag.get('src') or None
  if url:
    # normalize across subdirectories by removing leading "./" or "../"
    url = re.sub(relativedir_re, '', url)
    if url.startswith(_staticPath(site)):
      # change 'static/js/foo' to '/full/absolute/static/.build/static/js/foo'
      url = _relToStaticBuild(site, _withoutStatic(site, url))
  else:
    extension = 'css' if tag.name == 'style' else 'js'
    contents = tag.renderContents()
    url = 'inline_%s_%s.%s' % (
        extension,
        hashlib.md5(contents).hexdigest(),
        extension
      )
    url = _relToStaticBuild(site, url)
    if save:
      inline_assets.add(url) # for cleanup later
      with open(url, 'w') as f:
        f.write(contents)

  return url

def _replaceHTMLWithPackaged(html, replace_map, path, site):
  soup = BeautifulSoup(html)
  replaced = []
  for tag in _getLinks(soup) + _getScripts(soup):
    asset = _getAssetFrom(tag, site)
    if asset not in replace_map:
      continue

    path_to_static = os.path.relpath(_staticPath(site, includeBuild=True), _getDir(path))
    new_url = os.path.join(path_to_static, replace_map[asset])
    if new_url in replaced:
      # remove HTML node; this was already covered by another node with same package
      tag.extract()
    else:
      # replace assets with packaged version, but just once per package
      replaced.append(new_url)

      # update the actual HTML
      if tag.name == 'script':
        if not tag.get('src'): # inline scripts
          tag.clear()
        tag['src'] = new_url
      else:
        if tag.name == 'style': # inline styles
          new_tag = soup.new_tag('link', rel="stylesheet")
          tag.replace_with(new_tag)
          tag = new_tag
        tag['href'] = new_url
  return soup.prettify().encode('UTF-8')

def _getPackagedFilename(path_list):
  merged_name = '__'.join(map(os.path.basename, path_list))
  split = merged_name.rsplit('.', 1)
  extension = '.' + split[1] if len(split) > 1 else ''

  if MINIFY_FILENAMES:
    merged_name = hashlib.md5(merged_name).hexdigest()[:7] + extension

  subdir = 'js' if extension.endswith('js') else 'css'
  filename = os.path.join(subdir, AUTOGEN_PREFIX + merged_name)

  no_local_paths = not filter(lambda p: _isLocalFile(p), path_list)
  return filename, no_local_paths

def analyzeAndPackageAssets(site):
  sys.stdout.write('Analyzing %d gathered assets across %d pages...' %
    (len(list(itertools.chain.from_iterable(assets))), len(assets))
  )
  sys.stdout.flush()
  replace_map = {}

  # determine what should be packaged with what
  packages = AssetPackager.analyze(assets)
  print('done')

  for i, package in enumerate(packages):
    sys.stdout.write(
      '\rPacking analyzed assets into %d packages (%d/%d)' %
      (len(packages), i + 1, len(packages))
    )
    sys.stdout.flush()

    packaged_filename, no_local = _getPackagedFilename(package)

    if len(package) <= 1 and (no_local or not COMPRESS_PACKAGES):
      # it would be silly to compress a remote file and "package it with itself"
      # also silly for a local file to be packaged with itself if we won't be compressing it
      continue

    # Create and save the packaged, minified files
    AssetPackager.package(
      package,
      _relToStaticBuild(site, packaged_filename),
      compress = COMPRESS_PACKAGES,
      filename_markers_in_comments = INCLUDE_ORIGINAL_FILENAMES_IN_COMMENTS
    )

    for asset in package:
      replace_map[asset] = packaged_filename

  sys.stdout.write('\nUpdating HTML sources...')
  sys.stdout.flush()
  for page in site.pages():
    path = page.paths['full-build']

    with open(pipes.quote(path), 'r') as f:
      html = _replaceHTMLWithPackaged(f.read(), replace_map, path, site)
      f.close()
    with open(pipes.quote(path), "wb") as f:
      f.write(html)
      f.close()

  for asset in inline_assets:
    os.remove(asset) # clean up temp buffers
  print('done')



# CACTUS METHODS

def preBuild(site):
  # disable symlinking so we don't end up with a mess of files
  site.nosymlink = True

def postBuild(site):
  if PACKAGE_LOCALLY_DEBUG:
    analyzeAndPackageAssets(site)

def preDeploy(site):
  if not PACKAGE_LOCALLY_DEBUG:
    analyzeAndPackageAssets(site)

def postBuildPage(site, path):
  # Skip non html pages
  if not path.endswith('.html'):
    return

  with open(pipes.quote(path), 'r') as f:
    soup = BeautifulSoup(f.read())
  if PACKAGE_JS:
    assets.append(map(lambda x: _getAssetFrom(x, site, save=True), _getScripts(soup)))
  if PACKAGE_CSS:
    assets.append(map(lambda x: _getAssetFrom(x, site, save=True), _getLinks(soup)))

def postDeploy(site):
  # cleanup all static files that aren't used anymore
  files = [f.path for f in site.files()]
  keys = site.bucket.list(_staticPath(site))
  unused = filter(lambda k: k.name not in files, keys)
  if len(unused) > 0:
    print '\nCleaning up %d unused static files on the server:' % len(unused)
    for key in list(unused):
      print 'D\t' + _withoutStatic(site, key.name)
    site.bucket.delete_keys(unused)
