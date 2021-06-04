from django.template import Library, Node, TemplateSyntaxError


class InboxOutput(Node):
    def __init__(self, varname=None):
        self.varname = varname

    def render(self, context):
        try:
            user = context['user']
            count = user.received_messages.filter(read_at__isnull=True, recipient_deleted_at__isnull=True).count()
        except (KeyError, AttributeError):
            count = ''
        if self.varname is not None:
            context[self.varname] = count
            return ""
        else:
            return "%s" % (count)


def do_print_inbox_count(parser, token):

    bits = token.contents.split()
    if len(bits) > 1:
        if len(bits) != 3:
            raise TemplateSyntaxError("inbox_count tag takes either no arguments or exactly two arguments")
        if bits[1] != 'as':
            raise TemplateSyntaxError("first argument to inbox_count tag must be 'as'")
        return InboxOutput(bits[2])
    else:
        return InboxOutput()


register = Library()
register.tag('inbox_count', do_print_inbox_count)
