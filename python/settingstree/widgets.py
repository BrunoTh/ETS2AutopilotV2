from abc import ABC, abstractmethod


class HTMLWidget(ABC):
    # TODO: Don't use staticmethod or classmethod.
    @classmethod
    @abstractmethod
    def get_html_source(cls, settings_node) -> str:
        """
        This method returns html code of the widget.
        :type settings_node: SettingsNode
        """

    @classmethod
    def get_html_id(cls, settings_node) -> str:
        """
        This method returns the id of settings_node for html objects.
        :param settings_node: SettingsNode
        """
        return settings_node.fqid


class TextWidget(HTMLWidget):
    """
    Renders text input.
    """
    @classmethod
    def get_html_source(cls, settings_node) -> str:
        return f'<input type="text" id="id_{cls.get_html_id(settings_node)}" value="{settings_node.value}" />'


class SelectWidget(HTMLWidget):
    """
    Renders select tag.
    """
    @staticmethod
    def get_html_source(cls, settings_node) -> str:
        html = f'<select id="id_{cls.get_html_id(settings_node)}">\n'

        for child in settings_node.children:
            if child.is_choice and child.widget:
                html += child.render_element()
                html += '\n'

        html += f'</select>'
        return html


class OptionWidget(HTMLWidget):
    """
    Renders option tag.
    """
    @classmethod
    def get_html_source(cls, settings_node) -> str:
        return f'<option id="id_{cls.get_html_id(settings_node)}">{settings_node.key}</option>'


class SubtreeWidget(HTMLWidget):
    """
    Renders child elements in div.
    """
    @classmethod
    def get_html_source(cls, settings_node) -> str:
        html_code = f'<div id="div_{cls.get_html_id(settings_node)}">\n'
        html_code += f'<h2>{settings_node.verbose_name if settings_node.verbose_name else settings_node.key}</h2>\n'

        for child in settings_node.children:
            try:
                html_code += child.render_element()
                html_code += '\n'
            except Exception as e:
                pass

        html_code += '</div>\n'

        return html_code
