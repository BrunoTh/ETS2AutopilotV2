from abc import ABC, abstractmethod


class HTMLWidget(ABC):
    @staticmethod
    @abstractmethod
    def get_html_source(settings_node) -> str:
        """
        This method returns html code of the widget.
        :type settings_node: SettingsNode
        """


class TextWidget(HTMLWidget):
    """
    Renders text input.
    """
    @staticmethod
    def get_html_source(settings_node) -> str:
        return f'<input type="text" id="id_{settings_node.key}" value="{settings_node.value}" />'


class SelectWidget(HTMLWidget):
    """
    Renders select tag.
    """
    @staticmethod
    def get_html_source(settings_node) -> str:
        html = f'<select id="id_{settings_node.key}">\n'

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
    @staticmethod
    def get_html_source(settings_node) -> str:
        return f'<option id="id_{settings_node.key}">{settings_node.key}</option>'
