import os
import codecs
import logging

from .utils import parseValues

from django.template import Template, Context
from django.template import loader as templateLoader

class Page(object):
	
	def __init__(self, site, path):
		self.site = site
		self.path = path

		self.paths = {
			'full': os.path.join(self.site.path, 'pages', self.path),
			# 'build': os.path.join('.build', self.path),
			'full-build': os.path.join(site.paths['build'], self.path),
		}
		
	def data(self):
		f = codecs.open(self.paths['full'], 'r', 'utf-8')
		data = f.read()
		f.close()
		return data
	
	def context(self):
		"""
		The page context.
		"""
		
                # Site context, making a shallow-copy using dict so that the
                # things we add to this page's context below won't be added to
                # the site's context. if in the future we make non-top-level
                # changes to the page's context the shallow copy won't be
                # enough, we'd need to look at copy.deepcopy
		context = dict(self.site._contextCache)
		
		# Relative url context
		prefix = '/'.join(['..' for i in xrange(len(self.path.split('/')) - 1)]) or '.'
		
		context.update({
			'STATIC_URL': os.path.join(prefix, 'static'),
			'ROOT_URL': prefix,
			'PAGE_URL': self.path
		})
		
		# Page context (parse header)
		context.update(parseValues(self.data())[0])
		
		return Context(context)

	def render(self):
		"""
		Takes the template data with contect and renders it to the final output file.
		"""
		
		data = parseValues(self.data())[1]
		context = self.context()
		
		# Run the prebuild plugins, we can't use the standard method here because
		# plugins can chain-modify the context and data.
		for plugin in self.site._plugins:
			if hasattr(plugin, 'preBuildPage'):
				context, data = plugin.preBuildPage(self.site, self, context, data)

		return Template(data).render(context)

	def build(self):
		"""
		Save the rendered output to the output file.
		"""
		logging.info("Building %s", self.path)
		
		data = self.render()
		
		# Make sure a folder for the output path exists
		try: os.makedirs(os.path.dirname(self.paths['full-build']))
		except OSError: pass
		
		# Write the data to the output file
		f = codecs.open(self.paths['full-build'], 'w', 'utf-8')
		f.write(data)
		f.close()
		
		# Run all plugins
		self.site.pluginMethod('postBuildPage', self.site, self.paths['full-build'])
