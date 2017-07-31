import re
import logging

from markdown.preprocessors import Preprocessor
from markdown.extensions import Extension

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, TextLexer

def repl(m):
  formatter = HtmlFormatter(noclasses=False, nobackground=False)
  try:
    lexer = get_lexer_by_name(m.group(1))
  except ValueError:
    lexer = TextLexer()
  code = highlight(m.group(2), lexer, formatter)
  #code = code.replace('\n\n', '\n&nbsp;\n').replace('\n', '\n<br />')
  return '\n\n<div class="code">%s</div>\n\n' % code

def preBuildPage(site, page, context, data):
  pattern = re.compile(r'\[sourcecode:(.+?)\](.+?)\[/sourcecode\]', re.S)
  data = re.sub(pattern, repl, data)
  return context, data
        

    