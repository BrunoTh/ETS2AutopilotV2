from . import HTMLWidget, Text
from .htmltags import Div, H2, Input, Label, BR


class NodeHTMLWidget(HTMLWidget):
    def __init__(self, settings_node, attrs={}):
        self.settings_node = settings_node

        # Set the tag id
        attrs.update({'id': self.get_html_id()})

        super().__init__(attrs=attrs)

    def get_html_id(self) -> str:
        """
        This method returns the id of self.settings_node for html objects.
        """
        return self.settings_node.fqid

    def get_html_source(self) -> str:
        pass


class NodeInput(NodeHTMLWidget):
    """
    Renders an input field with label surrounded by a div. Materialize CSS style.
    """
    def get_html_source(self) -> str:
        self.attrs['id'] = self.get_html_id()

        if 'value' not in self.attrs:
            self.attrs['value'] = self.settings_node.value

        return Div(
            Input(attrs=self.attrs),
            Label(Text(self.settings_node.label), attrs={'for': self.attrs['id']}),
            attrs={'class': 'input-field col'}).get_html_source()


class NodeH2(NodeHTMLWidget):
    """
    Renders the settings node label as H2.
    Example: <h2>settings_node.label</h2>
    """
    def get_html_source(self) -> str:
        return H2(Text(self.settings_node.label)).get_html_source()


class NodeSubtree(NodeHTMLWidget):
    """
    Renders a div containing a NodeH2 and rendered children. The div as the class 'row' attached.
    """
    def get_html_source(self) -> str:
        if not self.settings_node.has_children():
            return ''

        if not self._is_in_attr('class'):
            self.attrs['class'] = 'row'
        elif 'row' not in self.attrs['class']:
            self.attrs['class'] += ' row'

        child_widgets = []
        for child in self.settings_node.children:
            try:
                child_widgets.append(Text(child.render_element()))
            except ValueError:
                pass

        return Div(NodeH2(self.settings_node), *child_widgets, attrs=self.attrs).get_html_source()
