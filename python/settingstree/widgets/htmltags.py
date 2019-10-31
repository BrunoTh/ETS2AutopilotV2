from . import HTMLWidget, Text


class HTMLTag(HTMLWidget):
    """
    A WidgetHTMLWidget takes several widgets as inputs and renders between an open and close tag.
    """
    def __init__(self, *widgets: HTMLWidget, attrs=None):
        super().__init__(attrs=attrs)
        self.widgets = list(widgets)

    def get_html_source(self) -> str:
        """
        Returns rendered widgets between html-tags.
        """
        html_code = self._render_open_tag()

        for widget in self.widgets:
            html_code += widget.get_html_source()

        html_code += self._render_close_tag()

        return html_code


class BR(HTMLWidget):
    TAG_NAME = 'br'

    def get_html_source(self) -> str:
        return self._render_close_tag()


class Div(HTMLTag):
    TAG_NAME = 'div'


class H1(HTMLTag):
    TAG_NAME = 'h1'


class H2(HTMLTag):
    TAG_NAME = 'h2'


class Label(HTMLTag):
    TAG_NAME = 'label'


class Input(HTMLTag):
    TAG_NAME = 'input'

    def __init__(self, *widgets, attrs=None):
        super().__init__(*widgets, attrs=attrs)

        if 'type' not in self.attrs.keys():
            self.attrs['type'] = 'text'


class Select(Input):
    def __init__(self, *widgets, attrs=None):
        super().__init__(*widgets, attrs=attrs)

        self.attrs['type'] = 'select'


class Option(HTMLTag):
    TAG_NAME = 'option'

    def __init__(self, *widgets, attrs=None, label=None, value=None):
        """
        Renders <option value="value">label</option>
        :param label: is added as Text-Widget to self.widgets
        :type label: str
        :param value: is added to attrs: {'value': value}
        :type value: str
        """
        super().__init__(*widgets, attrs=attrs)

        if label:
            self.widgets.append(Text(label))

        if value:
            self.attrs['value'] = value


class P(HTMLTag):
    TAG_NAME = 'p'
