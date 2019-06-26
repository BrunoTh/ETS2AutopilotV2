from . import HTMLWidget


class WidgetHTMLWidget(HTMLWidget):
    """
    A WidgetHTMLWidget takes several widgets as inputs and renders between an open and close tag.
    """
    def __init__(self, *widgets: HTMLWidget, attrs={}):
        super().__init__(attrs=attrs)
        self.widgets = widgets

    def get_html_source(self) -> str:
        html_code = self._render_open_tag()

        for widget in self.widgets:
            html_code += widget.get_html_source()

        html_code += self._render_close_tag()


class Div(WidgetHTMLWidget):
    TAG_NAME = 'div'
