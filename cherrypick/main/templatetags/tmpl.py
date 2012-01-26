from django import template

register = template.Library()

def mustache(parser, token):
	nodelist = parser.parse(('endmustache',))
	parser.delete_first_token()
	return MustacheNode(nodelist)

class MustacheNode(template.Node):
	def __init__(self, nodelist):
		self.nodelist = nodelist
		    
	def render(self, context):
		#return ''.join(tuple(node.source for node in self.nodelist))
		def nodelist_source():
			for node in self.nodelist:
				if hasattr(node, 's'):
					yield node.s

		return ''.join(nodelist_source())
		"""
		#print dir(self.nodelist)
		output = self.nodelist
		return output
		"""

@register.tag
def raw2(parser, token):
    # Whatever is between {% raw %} and {% endraw %} will be preserved as
    # raw, unrendered template code.
    text = []
    parse_until = ('endraw',)
    tag_mapping = {
        template.TOKEN_TEXT: ('', ''),
        template.TOKEN_VAR: ('{{', '}}'),
        template.TOKEN_BLOCK: ('{%', '%}'),
        template.TOKEN_COMMENT: ('{#', '#}'),
    }
    # By the time this template tag is called, the template system has already
    # lexed the template into tokens. Here, we loop over the tokens until
    # {% endraw %} and parse them to TextNodes. We have to add the start and
    # end bits (e.g. "{{" for variables) because those have already been
    # stripped off in a previous part of the template-parsing process.
    while parser.tokens:
        token = parser.next_token()
        if token.token_type == template.TOKEN_BLOCK and token.contents == parse_until:
            return template.TextNode(u''.join(text))
        start, end = tag_mapping[token.token_type]
        text.append(u'%s%s%s' % (start, token.contents, end))
    parser.unclosed_block_tag(parse_until)


"""
jQuery templates use constructs like:

    {{if condition}} print something{{/if}}

This, of course, completely screws up Django templates,
because Django thinks {{ and }} means something.

Wrap {% verbatim %} and {% endverbatim %} around those
blocks of jQuery templates and this will try its best
to output the contents with no changes.

This version of verbatim template tag allows you to use tags
like url {% url name %} or {% csrf_token %} within.
"""


class VerbatimNode(template.Node):
    def __init__(self, text_and_nodes, **kwargs):
		#self.attrs = {'type': 'text/x-jquery-tmpl'}
        self.attrs = {'type': 'text/html'}
        self.attrs.update(kwargs)
        self.text_and_nodes = text_and_nodes
    
    def render(self, context):
        output = '<script id="%(id)s" type="%(type)s">' % self.attrs

        # If its text we concatenate it, otherwise it's a node and we render it
        for bit in self.text_and_nodes:
            if isinstance(bit, basestring): 
                output += bit
            else:
                output += bit.render(context)

        return output + '</script>'

@register.tag
def tmpl(parser, token):
    contents = token.split_contents()
    contents.pop(0)
    if len(contents) == 1:
		attrs = {'id': contents[0]}
    else:
		attrs = dict(content.split('=', 2) for content in contents)

    text_and_nodes = []
    while 1:
        token = parser.tokens.pop(0)
        if token.contents == 'endtmpl':
            break

        if token.token_type == template.TOKEN_VAR:
            text_and_nodes.append('{{')
            text_and_nodes.append(token.contents)

        elif token.token_type == template.TOKEN_TEXT:
            text_and_nodes.append(token.contents)

        elif token.token_type == template.TOKEN_BLOCK:
            try:
                command = token.contents.split()[0]
            except IndexError:
                parser.empty_block_tag(token)

            try:
                compile_func = parser.tags[command]
            except KeyError:
                parser.invalid_block_tag(token, command, None)
            try:
                node = compile_func(parser, token)
            except template.TemplateSyntaxError, e:
                if not parser.compile_function_error(token, e):
                    raise
        
            text_and_nodes.append(node)

        if token.token_type == template.TOKEN_VAR:
            text_and_nodes.append('}}')
           
    return VerbatimNode(text_and_nodes, **attrs)