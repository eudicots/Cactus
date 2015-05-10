# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
try:
    import unittest2 as unittest
except ImportError:
    import unittest
from testfixtures import LogCapture

from cactus.plugin.builtin.page_context import PageContextPlugin
from cactus.tests import SiteTestCase
from cactus.page import Page


class TestPagecontextStyles(unittest.TestCase):

    def test_jekyll_style(self):
        testdata = [
            (['---',  # fenced
              'Author : Me',
              'Content: Awesome',
              '---',
              'Here comes the content'],
             {'Author': 'Me', 'Content': 'Awesome'},
             ['Here comes the content']),

            (['Author : Me',  # no start of metadata
              '---',
              'Here comes the content'],
             {},
             ['Author : Me',
              '---',
              'Here comes the content']),

            (['',  # file starts with a blank line
              '---',
              'Todays motto: whatever'],
             {},  # no context data
             ['', '---', 'Todays motto: whatever']),  # everything preserved

            (['This file has',
              'no metadata whatsoever'],
             {},
             ['This file has', 'no metadata whatsoever']),

        ]
        plugin = PageContextPlugin()
        class Page:
            source_path = '/some/path'
        page = Page()

        for i, (input_lines,
                expected_context,
                expected_output_lines) in enumerate(testdata):
            self.assertEqual((expected_context, expected_output_lines),
                             plugin.jekyll_style(input_lines, page),
                             'Test Data No. %d failed' % i)

        input_lines = ['---',
                       'Author : Me',  # no end of metadata
                       'Here comes the content']
        with LogCapture() as l:
            context, data = plugin.jekyll_style(input_lines, page)
        self.assertEqual(len(l.records), 1)
        self.assertEqual(l.records[0].levelname, 'WARNING')
        self.assertEqual(l.records[0].msg, 'Page context data in file %s seem to end in line %d')

    def test_simple_style(self):
        testdata = [
            (['Author : Me',
              'Content: Awesome',
              '',
              'Here comes the content'],
             {'Author': 'Me', 'Content': 'Awesome'},
             ['', 'Here comes the content']),

            (['',  # file starts with a blank line
              'Todays motto: whatever'],
             {},  # no context data
             ['', 'Todays motto: whatever']),  # blank line preserved

            (['This file has',
              'no metadata whatsoever'],
             {},
             ['This file has', 'no metadata whatsoever']),
        ]
        plugin = PageContextPlugin()

        for i, (input_lines,
                expected_context,
                expected_output_lines) in enumerate(testdata):
            self.assertEqual((expected_context, expected_output_lines),
                             plugin.simple_style(input_lines),
                             'Test Data No. %d failed' % i)

    def test_multimarkdown_style(self):
        testdata = [
            (['Author : Me',
              'Content: Awesome',
              '',
              'Here comes the content'],
             {'author': 'Me', 'content': 'Awesome'},
             ['Here comes the content']),

            (['---',  # fenced
              'Author : Me',
              'Content: Awesome',
              '---',
              'Here comes the content'],
             {'author': 'Me', 'content': 'Awesome'},
             ['Here comes the content']),

            (['Multiline: in two',
              ' lines',
              '',
              'Here comes the content'],
             {'multiline': 'in two lines'},
             ['Here comes the content']),

            (['Multiline: in two',
              'lines',  # not indented
              '',
              'Here comes the content'],
             {'multiline': 'in two lines'},
             ['Here comes the content']),

            (['Multiline: in',
              '           three',
              '           lines',
              '',
              'Here comes the content'],
             {'multiline': 'in three lines'},
             ['Here comes the content']),

            (['Multiline: in two lines',
              '           with: colon',
              '',
              'Here comes the content'],
             {'multiline': 'in two lines with: colon'},
             ['Here comes the content']),

            (['',  # file starts with a blank line
              'Todays motto: whatever'],
             {},  # no context data
             ['', 'Todays motto: whatever']),  # blank line preserved

            (['This file has',
              'no metadata whatsoever'],
             {},
             ['This file has', 'no metadata whatsoever']),
        ]
        plugin = PageContextPlugin()

        for i, (input_lines,
                expected_context,
                expected_output_lines) in enumerate(testdata):
            self.assertEqual((expected_context, expected_output_lines),
                             plugin.multimarkdown_style(input_lines),
                             'Test Data No. %d failed' % i)


class TestPageTags(SiteTestCase):
    def test_preBuildPage(self):
        testdata = [
            ('simple.html',                  # filename
             "name: koen\n"                  # input data
             "age: 29\n"
             "A Cactus is a spiny plant",
             {},                             # given context
             {"name": "koen", "age": "29"},  # expected context
             "A Cactus is a spiny plant"),   # expected content

            ('given_context.html',
             "name: koen\n"
             "age: 29\n"
             "A Cactus is a spiny plant",
             {"subject": "biology"},
             {"subject": "biology", "name": "koen", "age": "29"},
             "A Cactus is a spiny plant"),

            ('given_context.html',
             "name: koen\n"
             "subject: computer\n"
             "Cactus is great software",
             {"subject": "biology"},
             {"subject": "computer", "name": "koen"},
             "Cactus is great software"),

            ('separating-line.html',
             "name: koen\n"
             "\n"
             "A Cactus is a spiny plant",
             {},
             {"name": "koen"},
             "\nA Cactus is a spiny plant"),

            ('jekyll.html',
             "---\n"
             "name: koen\n"
             "---\n"
             "A Cactus is a spiny plant",
             {},
             {"name": "koen"},
             "A Cactus is a spiny plant"),

            ('empty.html',
             "",
             {},
             {},
             ""),

            ('empty-line.html',
             "\n",
             {},
             {},
             ""),

        ]
        pcp = PageContextPlugin()
        for (filename,
             input_data,
             given_context,
             expected_context,
             expected_content) in testdata:
            page = Page(self.site, filename)
            context, content = pcp.preBuildPage(
                    page, given_context, input_data)
            self.assertEqual(context, expected_context, "Testcase " + filename)
            self.assertEqual(content, expected_content, "Testcase " + filename)


