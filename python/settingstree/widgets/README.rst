Widgets
=======

The idea
--------
My idea behind the widgets is that you fully generate html code
in python. You can add any widget to a SettingsNode and the
SettingsNode.render_element() method returns the html code.

How to use
----------
The widgets package contains two modules.

* htmltags contains the simple html tags.
* nodewidgets are the widgets you want to attach to your
  SettingsNode. These widgets fill htmltags with
  content from SettingsNode (e.g. label or value).

Contribute?
-----------
If you are that crazy and want to write your own
widgets here is a guide.

Your widget has to inherit from `nodewidgets.NodeHTMLWidget`.
You have then access to the following fields:

* self.settings_node: The SettingsNode instance.
* self.attrs: Tag attributes the user of the widget wants to apply to the
  html tag. You don't have to pass them to the html tag.

Besides of that feel free to add some kwargs but don't forget to set default
values.

The html code is generated in the get_html_source() method. You have to
overwrite it. Trust me, I'm a programmer.
In that method the magic happens. Here you combine some html tags and render
them or you can simply return your own html code.
This method gets called when the settings page gets rendered.

How to use html tags
--------------------
Instead of writing html code directly you can use HTMLTag classes.
They have also a get_html_source() method. It simply outputs an open (<html>)
and close tag (</html>) and adds html code of entered HTMLWidgets in
between.

You've heard right. A HTMLTag can take other HTMLWidgets as parameter.

Here is an example. First the HTML code you want to generate::

    <div class='main'>
        <h1>Simply amazing</h1>
        <p>This is crazy stuff.</p>
    </div>

And the python code would look like::

    Div(
      H1(Text('Simply amazing')),
      P(Text('This is crazy stuff.')),
      attrs={'class': 'main'}
    ).get_html_source()

Text() is also a HTMLWidget. Its get_html_source() method just returns the
given text.

Got it? Div takes two other HTMLWidgets (here HTMLTags) and some attrs.
The attrs dict gets added to the open tag. The procedure is `key="value"`.
With that you could also add some JavaScript to your Tags, like
{'onclick': 'alert("Click!")'} to a button.
