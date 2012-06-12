import os
import codecs
import logging

try:
	from django.template import Template, Context
	from django.template import loader as templateLoader
except:
	pass

class Page(object):

	def __init__(self, site, path):
		self.site = site
		self.path = path

		self.paths = {
			'full': os.path.join(self.site.path, 'pages', self.path),
			'build': os.path.join('build', self.path),
			'full-build': os.path.join(site.path, 'build', self.path),
		}
		
	def data(self):		
		f = codecs.open(self.paths['full'], 'r', 'utf-8')
		data = f.read()
		f.close()
		return data
	
	def parseHeader(self):
		"""
		Parse the page header in the format key:value<newline>
		"""
		return {}
	
	def context(self):
		"""
		The page context.
		"""
		
		# Site context
		context = self.site.context()
		
		# Relative url context
		prefix = '/'.join(['..' for i in xrange(len(self.path.split('/')) - 1)])
		
		context.update({
			'STATIC_URL': os.path.join(prefix, 'static'),
			'ROOT_URL': prefix,
		})
		
		# Page context (parse header)
		context.update(self.parseHeader())
		
		# Addon context (extras folder)
		# context.update(self.extraContext(path, context))
		
		return Context(context)

	def render(self):
		"""
		Takes the template data with contect and renders it to the final output file.
		"""
		
		template = Template(self.data())
		return template.render(self.context())

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