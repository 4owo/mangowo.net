Recipes
=======

\* Fancy things you can do with Poole. *

[Navigation Menu](Recipes#!navigation-menu) ·
[Breadcrumb Navigation](Recipes#!breadcrumb-navigation) ·
[List of Blog Posts](Recipes#!list-of-blog-posts) ·
[Google Sitemap File](Recipes#!google-sitemap-file) ·
[RSS Feed for Blog Posts](Recipes#!rss-feed-for-blog-posts) ·
[Multiple Languages Support](Recipes#!multiple-languages-support) ·
[Link File Size](Recipes#!link-file-size)

Feel free to add yours!

------------------------------------------------------------------------

Navigation Menu
---------------

Have a look into the `page.html` file in a freshly initialized Poole
project.

------------------------------------------------------------------------

Breadcrumb Navigation
---------------------

To add breadcrumb navigation, put this into the project\'s `macros.py`
file:

    #!python
    def breadcrumb():
        parents = {p.title: (p.url, p.get('parent')) for p in pages}
        title = page.title
        output = hx(title)
        while parents[title][1] is not None:
            title = parents[title][1]
            url = parents[title][0]
            output = '<a href="%s">%s</a> &gt; %s' % (url, hx(title), output)
        return output

For each page that has a parent, set the page attribute `parent` to the
`title` of the parent page. The breadcrumb trail can then be included by
specifying `{{ breadcrumb() }}` in your `page.html` (or elsewhere).

------------------------------------------------------------------------

List of Blog Posts
------------------

If you want to write some blog posts, you probably would like to have a
page listing all or the latest blog posts. This is easy if you set
certain page attributes in every blog post page:

`input/brain-on-mongs.md`:

    title: blog
    post: This is your brain on mongs
    date: 2010-03-01
    ---

    # {{ page.post }}

    Posted on {{ page.date }}

    My hero is full of keyboards. Get nonsense at <http://automeme.net/>

`input/blog.md`:

    This is my blog.

    # My posts

    {%
    from datetime import datetime
    posts = [p for p in pages if "post" in p] # get all blog post pages
    posts.sort(key=lambda p: p.get("date"), reverse=True) # sort post pages by date
    for p in posts:
        date = datetime.strptime(p["date"], "%Y-%m-%d").strftime("%B %d, %Y")
        print "  * **[%s](%s)** - %s" % (p.post, p.url, date) # markdown list item
    %}

Feel free to adjust this to your needs.

**TIP:** Instead of setting the post title and date as page attributes,
you can encode them in the page\'s file name using a structure like
`page-title.YYYY-MM-DD.post-title.md`. For instance for the file name
`blog.2010-03-01.This_is_your_brain_on_mongs.md` Poole would
automatically set the page attributes which has been set manually in the
example above.

To see this example in action, have a look into the example pages in a
freshly initialized Poole project.

------------------------------------------------------------------------

Google Sitemap File
-------------------

To generate a Google `sitemap.xml` file, put this into the project\'s
`macros.py` file:

    #!python
    from datetime import datetime
    import os.path

    _SITEMAP = """<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    %s
    </urlset>
    """

    _SITEMAP_URL = """
    <url>
        <loc>%s/%s</loc>
        <lastmod>%s</lastmod>
        <changefreq>%s</changefreq>
        <priority>%s</priority>
    </url>
    """

    def hook_preconvert_sitemap():
        """Generate Google sitemap.xml file."""
        date = datetime.strftime(datetime.now(), "%Y-%m-%d")
        urls = []
        for p in pages:
            urls.append(_SITEMAP_URL % (options.base_url.rstrip('/'), p.url, date,
                        p.get("changefreq", "monthly"), p.get("priority", "0.8")))
        fname = os.path.join(options.project, "output", "sitemap.xml")
        fp = open(fname, 'w')
        fp.write(_SITEMAP % "".join(urls))
        fp.close()

You probably want to adjust the default values for *changefreq* and
*priority*.

**Info:** Every function in `macros.py` whose name starts with
`hook_preconvert_` or `hook_postconvert_` is executed exactly once per
project build \-- either before or after converting pages from markdown
to HTML. In post-convert hooks the HTML content of a page (yet without
header and footer) can be accessed with `page.html`. This is useful to
generate full-content RSS feeds.

------------------------------------------------------------------------

RSS Feed for Blog Posts
-----------------------

To generate an RSS feed for blog posts put this into the project\'s
`macros.py` file and adjust for your site:

    #!python
    import email.utils
    import os.path
    import time

    _RSS = """<?xml version="1.0"?>
    <rss version="2.0">
    <channel>
    <title>%s</title>
    <link>%s</link>
    <description>%s</description>
    <language>en-us</language>
    <pubDate>%s</pubDate>
    <lastBuildDate>%s</lastBuildDate>
    <docs>http://blogs.law.harvard.edu/tech/rss</docs>
    <generator>Poole</generator>
    %s
    </channel>
    </rss>
    """

    _RSS_ITEM = """
    <item>
        <title>%s</title>
        <link>%s</link>
        <description>%s</description>
        <pubDate>%s</pubDate>
        <guid>%s</guid>
    </item>
    """

    def hook_postconvert_rss():
        items = []
        posts = [p for p in pages if "post" in p] # get all blog post pages
        posts.sort(key=lambda p: p.date, reverse=True)
        for p in posts:
            title = p.post
            link = "%s/%s" % (options.base_url.rstrip("/"), p.url)
            desc = p.get("description", "")
            date = time.mktime(time.strptime("%s 12" % p.date, "%Y-%m-%d %H"))
            date = email.utils.formatdate(date)
            items.append(_RSS_ITEM % (title, link, desc, date, link))

        items = "".join(items)

        # --- CHANGE THIS --- #
        title = "Maximum volume yields maximum moustaches"
        link = "%s/blog.html" % options.base_url.rstrip("/")
        desc = "My name is dragonforce. You killed my dragons. Prepare to scream."
        date = email.utils.formatdate()

        rss = _RSS % (title, link, desc, date, date, items)

        fp = open(os.path.join(output, "rss.xml"), 'w')
        fp.write(rss)
        fp.close()

------------------------------------------------------------------------

Multiple languages support
--------------------------

To make your website available in several languages, put this into the
project\'s `macros.py` file:

    #!python

    import re
    import itertools


    def hook_preconvert_multilang():
        MKD_PATT = r'\.(?:md|mkd|mdown|markdown)$'
        _re_lang = re.compile(r'^[\s+]?lang[\s+]?[:=]((?:.|\n )*)', re.MULTILINE)
        vpages = [] # Set of all virtual pages
        for p in pages:
            current_lang = "en" # Default language
            langs = [] # List of languages for the current page
            page_vpages = {} # Set of virtual pages for the current page
            text_lang = re.split(_re_lang, p.source)
            text_grouped = dict(zip([current_lang,] + \
                                            [lang.strip() for lang in text_lang[1::2]], \
                                            text_lang[::2]))

            for lang, text in text_grouped.iteritems():
                spath = p.fname.split(os.path.sep)
                langs.append(lang)
                filename = re.sub(MKD_PATT, ".%s\g<0>" % lang, p.fname).split(os.path.sep)[-1]
                vp = Page(filename, virtual=text)
                # Copy real page attributes to the virtual page
                for attr in p:
                    if not vp.has_key(attr):
                        vp[attr] = p[attr]
                # Define a title in the proper language
                vp["title"] = p["title_%s" % lang] \
                                        if p.has_key("title_%s" % lang) \
                                        else p["title"]
                # Keep track of the current lang of the virtual page
                vp["lang"] = lang
                # Fix post name if exists
                if vp.has_key("post"):
                    vp["post"] = vp["post"][:-len(lang) - 1]
                page_vpages[lang] = vp

            # Each virtual page has to know about its sister vpages
            for lang, vpage in page_vpages.iteritems():
                vpage["lang_links"] = dict([(l, v["url"]) for l, v in page_vpages.iteritems()])
                vpage["other_lang"] = langs # set other langs and link

            vpages += page_vpages.values()

        pages[:] = vpages

Then make the following modifications in `page.html`:

    #!python

    mpages = [p for p in pages if "menu-position" in p]

becomes

    #!python

    mpages = [p for p in pages if "menu-position" in p and p.has_key("lang") and p["lang"] == page["lang"]]

Add the language list by adding this code in `page.html`, for example at
the end of the div menu:

    #!html
         <div id="lang">
             <!--%
                 print " | ".join(["<span><a href='%s'>%s</a></span>" % \
                          (url, lang) for lang, url in page["lang_links"].iteritems()])
             %-->
          </div>

Adjust the `poole.css` file by adding something like:

    #!css
    div#lang {
        float:right;
        text-align:right;
        color: white;
    }

Finally, if you want to show blog pages of the current language only,
replace:

    #!python

    posts = [p for p in pages if "post" in p] # get all blog post pages

with

    #!python

    posts = [p for p in pages if "post" in p if p.lang == page.lang] # get all blog post pages

in `blog.md` (or whatever your blog file is).

### Usage

The directive `lang: lang_name` (where `lang_name` can be any language
code, typically according to
[ISO 639-1](http://en.wikipedia.org/wiki/List_of_ISO_639-1_codes))
separate different languages of the same page. The attribute
`title_lang_name` can be used to translate the title page (which may be
displayed in the menu). Example:

`input/stuff/news.md:`

        title: Hot News
        title_fr: Nouvelles
        foobar: King Kong
        ---
        Here are some news about {{ page.foobar }}.
        Did I say {% print(page.foobar) %}?

        lang: fr

        Voici quelques nouvelles a propos de {{ page.foobar }}.
        Ai-je bien dit {% print(page.foobar) %} ?

The first block will always take the default language (which can be
changed in the hook above).

------------------------------------------------------------------------

Link File Size
--------------

For people with slow internet access, or simply to inform the visitor
about the size of a downloadable file on your poole web site, you can
use the following postconvert hook:

    #!python
    def hook_postconvert_size():
        file_ext = '|'.join(['pdf', 'eps', 'ps'])
        def matched_link(matchobj):
        try:
            # We assume a relative link to a document in the output directory of poole.
            size = os.path.getsize(os.path.join("output", matchobj.group(1)))
            return  "<a href=\"%s\">%s</a>&nbsp;(%d KiB)" % (matchobj.group(1), \
                                     matchobj.group(3), \
                                     size // 1024)
        except:
            print "Unable to estimate file size for %s" % matchobj.group(1)
            return '<a href=\"%s\">%s</a>' % (matchobj.group(1), \
                              matchobj.group(3))

        _re_url = '<a href=\"(.*?\.(%s))\">(.*?)<\/a>' % file_ext
        for p in pages:
        p.html = re.sub(_re_url, matched_link, p.html)

It will add the file size in KiB, right after the link, for the file
extensions specified in the second line.
