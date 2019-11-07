Macros
------

Though poole is made for simple websites you can add a thin layer of
smartness to a site using macros.

**Note:** If you end up using macros a lot and everywhere, you should
have a look at more powerful site generator\'s like Jekyll or Hyde which
realize the idea of processing logic much better and with a more clear
distinction between logic, content and layout.

### Macros as variables

You can use macros to avoid writing some repetitive content again and
again. Consider the following as the content of a page, let\'s say
*some-page.md*, in your project\'s *input* folder:

**some-page.md**:

    #!text
    # book_title: Fool
    # book_author: Moore

    Books
    -----

    My current favorite book is {{ book_title }} by {{ book_author }}.
    ...
    That is why I love *{{book_title}}*.

At the beginning it defines 2 macros which are used later using *{{
macro-name }}*. Macros defined within a page are only valid in the scope
of that page. If you want to reference your currently favored book on
other pages, you should define it as a *global* macro.

To define global macros, create a file *macros.py* in the same folder
where *page.html* is located and set your macros there:

**macros.py**:

    #!python
    book_title = Fool
    book_author = Moore

Now you can reference these macro in every page.

What about a *today* macro, specifying the site build day:

**macros.py:**

    #!python
    import datetime
    today = datetime.datetime.now().strftime("%Y-%m-%d")

### Overriding global macros in pages

A good use case for a global macro defined in *macors.py* is to set a
description or some keywords for your site which can then be referenced
in the *page.html* file, e.g.:

**macros.py:**

    #!python
    # ...
    description = "a site about boo"
    keywords = "foo, bar"
    # ...

**page.html:**

    #!html
    <!-- ... -->
    <meta name="description" content="{{ description }}">
    <meta name="keywords" content="{{ keywords }}">
    <!-- ... -->

For individual pages you can override these settings, for instance:

**some-page.md:**

    #!text
    # keywords: foo, baz
    ...

Page macro definitions override global macro definitions in *macros.py*!

### Dynamically generated content

In *macros.py* you can define functions which then can be referenced as
macros. Here\'s a simple and useless example:

**macros.py**:

    #!python
    def asum(pages, page, a="0", b="1"):
        return int(a) + int(b)

**some-page.md:**

    #!text
    ...
    The sum of 1 and 5 is {{ asum a=1 b=5 }}.
    ...

This will be replaced by, suprise, *6*.

Macro function in must have at least 2 parameters:

1.  *pages*: a list of all pages in the site processed by *poole*
2.  *page*: the current page where this macro is used

Additional parameters must be declared as keword arguments.

The objects in *pages* as well as *page* itself are Page objects which
have the following public fields:

-   *name*: name of the page (either the file name without extension or
    the value of the `name` macro, if defined within the page\'s source
    file
-   *macros*: a dictionary of all macros defined for the page (including
    global macros defined in *macro.py*)
-   *url*: URL to link to that page

Here is a more complex example, the built-in *menu* macro used in the
default *page.html/ file to display a navigation menu:*

    #!python
    def menu(pages, page, tag="span", current="current"):
        """Compile an HTML list of pages to appear as a navigation menu.

        Any page which has a macro {{{menu_pos}}} defined is included. Menu
        positions are sorted by the integer values of {{{menu_pos}}} (smallest
        first).

        The current page's //tag// element is assigned the CSS class //current//.

        """
        menu_pages = [p for p in self.pages if "menu_pos" in p.macros]
        menu_pages.sort(key=lambda p: int(p.macros["menu_pos"]))

        html = ''
        for p in menu_pages:
            style = p == self.__page and (' class="%s"' % current) or ''
            html += '<%s%s><a href="%s">%s</a></%s>' % (tag, style, p.url, p.name, tag)
        return html

You can write your own *menu* macro in *macros.py*, if you don\'t like
the built-in one.

### Limitations

Macros are not nestable.
