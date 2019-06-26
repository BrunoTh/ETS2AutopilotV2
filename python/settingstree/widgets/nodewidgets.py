from . import HTMLWidget


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


class Input(NodeHTMLWidget):
    """
    Renders an input tag with set attributes. Default type is text.
    """
    TAG_NAME = 'input'

    def __init__(self, settings_node, attrs={}):
        if 'type' not in attrs.keys():
            attrs['type'] = 'text'

        super().__init__(settings_node, attrs=attrs)

    def get_html_source(self) -> str:
        return self._render_open_tag()
