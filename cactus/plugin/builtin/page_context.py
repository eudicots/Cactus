#coding:utf-8
from __future__ import unicode_literals
import logging
import re

logger = logging.getLogger(__name__)


class PageContextPlugin(object):
    """
    A plugin to extract context variables from the top of the file

    TODO:
    - read style of metadata from config
    - read splitChar from config
    """
    ORDER = 0

    def preBuildPage(self, page, context, data):
        """
        Update the page context with the context variables from the file
        and delete them
        """
        if not page.is_html() or not data:
            return context, data

        lines = data.splitlines()

        # Look into the file to decide on the style of metadata
        # TODO: make that configurable
        if lines[0].strip() == '---':
            page_context, lines = self.jekyll_style(lines, page)
        else:
            page_context, lines = self.simple_style(lines)
        context.update(page_context)

        return context, '\n'.join(lines)

    def jekyll_style(self, lines, page):
        """
        metadata as defined in http://jekyllrb.com/docs/frontmatter/

        `lines` should not be empty
        `page` is required only for the error message
        """
        if lines[0].strip() != '---':  # no metadata
            return {}, lines

        context = {}
        splitChar = ':'
        for i, line in enumerate(lines[1:]):
            if line.strip() == '---':  # end of metadata
                i += 1
                break

            try:
                key, value = line.split(splitChar, 1)
            except ValueError:
                # splitChar not in line
                logger.warning('Page context data in file %s seem to end in line %d',
                        page.source_path, i)
                break

            context[key.strip()] = value.strip()

        return context, lines[i+1:]

    def simple_style(self, lines):
        """
        Only lines at the top of the file with a colon are metadata.
        No multiline metadata

        `lines` should not be empty
        """
        context = {}
        splitChar = ':'

        for i, line in enumerate(lines):

            if splitChar not in line:
                break

            key, value = line.split(splitChar, 1)
            context[key.strip()] = value.strip()

        return context, lines[i:]

    def multimarkdown_style(self, lines):
        """
        metadata as defined in http://fletcher.github.io/MultiMarkdown-4/metadata

        `lines` should not be empty
        """
        context = {}
        splitChar = ':'
        fenced = False
        key = None
        whitespace = re.compile(r'\s')

        if splitChar not in lines[0] and lines[0].strip() != '---':
            return {}, lines  # no metadata

        for i, line in enumerate(lines):
            # fencing is allowed but not required in multimarkdown
            if line.strip() == '---':
                if i == 0:
                    fenced = True
                    continue
                elif fenced:
                    i += 1
                    break

            # a blank line triggers the beginning of the rest of the document
            if not line.strip():
                # if the file starts with a blank line, nothing should be changed
                if i != 0:
                    i += 1
                break

            # indented lines are the continuation of the previous value
            # but multiline values don't have to be indented
            if key and (whitespace.match(line) or not splitChar in line):
                context[key] = ' '.join(
                    (context[key], line.lstrip()))
                continue

            key, value = line.split(splitChar, 1)

            # keys are lower cased and stripped of all whitespace
            key = re.sub(r'\s', '', key.lower())
            context[key] = value.strip()

        return context, lines[i:]
