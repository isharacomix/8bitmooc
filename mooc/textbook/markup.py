# -*- coding: utf-8 -*-
from creoleparser.core import Parser
from creoleparser.dialects import create_dialect, creole11_base, parse_args
from creoleparser.elements import PreBlock
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from genshi import builder, Markup
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.styles.autumn import AutumnStyle
from pygments.util import ClassNotFound

global_cache = {}

# This includes Markdown-style backticks for inline code.
INLINE_MARKUP = [
    ('**','strong'),    ('//','em'),        (',,','sub'),
    ('^^','sup'),       ('__','u'),         ('##','code'),
    ('`', 'code'),      ('--','del'),
]

def build_interwikis():
    from django.conf import settings
    bases, spaces, classes = {}, {}, {}
    for name, (base, space) in getattr(settings, 'INTERWIKIS', {}).items():
        bases[name] = base
        spaces[name] = space
        classes[name] = lambda page: name + '-link'
    return bases, spaces, classes


def wiki_link_path(link):
    #if link.startswith("~"):
    #    # User profile
    #    return reverse('profile', args=[MemberProfile.make_username(link[1:])])
    #else:
    return reverse('textbook_page', kwargs={'page': link})


def wiki_link_class(link):
    #if link.startswith("~"):
    #    return 'user-link'
    #else:
    return 'wiki-link'


def get_pygments_formatter():
    if 'formatter' not in global_cache:
        global_cache['formatter'] = HtmlFormatter(style=AutumnStyle)
    return global_cache['formatter']


class CodeBlock(PreBlock):
    # Code borrowed from Flask Website:
    # https://github.com/mitsuhiko/flask/blob/website/flask_website/utils.py
    def __init__(self):
        super(CodeBlock, self).__init__('pre', ['{{{', '}}}'])

    def _build(self, mo, element_store, environ):
        lines = self.regexp2.sub(r'\1', mo.group(1)).splitlines()
        if lines and lines[0].startswith('#!'):
            try:
                lexer = get_lexer_by_name(lines.pop(0)[2:].strip())
            except ClassNotFound:
                pass
            else:
                return Markup(highlight(u'\n'.join(lines), lexer,
                                        get_pygments_formatter()))
        return builder.tag.pre(u'\n'.join(lines))


def create_lug_dialect():
    iw_bases, iw_spaces, iw_classes = build_interwikis()

    dialect = create_dialect(creole11_base,
        # Markup customizations
        simple_markup = INLINE_MARKUP,
        indent_style = '',
        indent_class = 'quote',
        no_wiki_monospace = False,
        # Internal links
        wiki_links_base_url = "",
        wiki_links_path_func = wiki_link_path,
        wiki_links_class_func = wiki_link_class,
        # Everyone else's links
        external_links_class = 'external-link',
        interwiki_links_base_urls = iw_bases,
        interwiki_links_class_funcs = iw_classes,
        interwiki_links_space_chars = iw_spaces
    )
    dialect.pre = CodeBlock()
    return dialect


def get_parser():
    if 'parser' not in global_cache:
        global_cache['parser'] = Parser(dialect=create_lug_dialect(),
                                        method='html')
    return global_cache['parser']


def render_markup(text):
    return mark_safe(get_parser().render(text))

