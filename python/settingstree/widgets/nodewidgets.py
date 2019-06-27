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
        This method returns the id of settings_node for html objects.
        :param settings_node: SettingsNode
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
    def get_html_source(self) -> str:
        return H2(Text(self.settings_node.label)).get_html_source()


class NodeSubtree(NodeHTMLWidget):
    def get_html_source(self) -> str:
        if not self.settings_node.has_children():
            return ''

        if not self._is_in_attr('class'):
            self.attrs['class'] = 'row'

        child_widgets = []
        for child in self.settings_node.children:
            try:
                child_widgets.append(Text(child.render_element()))
            except ValueError:
                pass

        return Div(NodeH2(self.settings_node), *child_widgets, attrs=self.attrs).get_html_source()
