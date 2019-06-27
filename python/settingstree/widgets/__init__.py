from abc import ABC, abstractmethod


class HTMLWidget(ABC):
    TAG_NAME = None

    def __init__(self, attrs={}):
        """
        :type attrs: dict
        :param attrs: HTML-Tag attributes like class="" or style="".
        """
        self.attrs = attrs

    def _render_open_tag(self, tag_name=None):
        """
        This method renders a tag with the previously set attributes.
        Uses self.TAG_NAME if tag_name parameter is not set.
        :param tag_name: HTML Tag name
        :return:
        """
        if not tag_name and self.TAG_NAME:
            tag_name = self.TAG_NAME

        tag = f'<{tag_name}'

        for key, value in self.attrs.items():
            tag += f' {key}="{value}"'
        tag += '>'

        return tag

    def _render_close_tag(self, tag_name=None):
        if not tag_name and self.TAG_NAME:
            tag_name = self.TAG_NAME

        return f'</{tag_name}>'

    def _is_in_attr(self, key):
        return key in self.attrs.keys()

    @abstractmethod
    def get_html_source(self) -> str:
        """
        This method returns html code of the widget.
        """


class Text(HTMLWidget):
    """
    Simply returns the given text. Newlines are replaced by <br />.
    """
    def __init__(self, text):
        super().__init__()
        self.text = text

    def get_html_source(self) -> str:
        return self.text.replace('\n', '<br />')
