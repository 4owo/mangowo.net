#!/usr/bin/python

# =============================================================================
#
#    Poole - A damn simple static website generator.
#    Copyright (C) 2009 Oben Sonne <obensonne@googlemail.com>
#
#    This file is part of Poole.
#
#    Poole is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Poole is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Poole.  If not, see <http://www.gnu.org/licenses/>.
#
# =============================================================================

from __future__ import with_statement

import codecs
from ConfigParser import SafeConfigParser
import glob
import imp
import optparse
import os
import os.path
from os.path import join as opj
from os.path import exists as opx
import re
import shutil
import StringIO
import sys
import traceback
import urlparse

from SimpleHTTPServer import SimpleHTTPRequestHandler
from BaseHTTPServer import HTTPServer

try:
    import markdown
except ImportError:
    print("error: need python-markdown, get it from "
          "http://www.freewisdom.org/projects/python-markdown/Installation")
    sys.exit(1)

# =============================================================================
# init site
# =============================================================================

EXAMPLE_FILES =  {

"page.html": """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset={{ __encoding__ }}" />
    <title>poole - {{ page["title"] }}</title>
    <meta name="description" content="{{ page.get("description", "a poole site") }}" />
    <meta name="keywords" content="{{ page.get("keywords", "poole") }}" />
    <link rel="stylesheet" type="text/css" href="poole.css" />
</head>
<body>
    <div id="box">
    <div id="header">
         <h1>a poole site</h1>
         <h2>{{ page["title"] }}</h2>
    </div>
    <div id="menu">
    <!--%
        mpages = [p for p in pages if "menu-position" in p]
        mpages.sort(key=lambda p: int(p["menu-position"]))
        entry = '<span class="%s"><a href="%s">%s</a></span>'
        for p in mpages:
            style = p["title"] == page["title"] and "current" or ""
            print(entry % (style, p["url"], p["title"]))
    %-->
    </div>
    <div id="content">{{ __content__ }}</div>
    </div>
    <div id="footer">
        Built with <a href="http://bitbucket.org/obensonne/poole">Poole</a>
        &middot;
        Licensed as <a href="http://creativecommons.org/licenses/by-sa/3.0">CC-SA</a>
        &middot;
        <a href="http://validator.w3.org/check?uri=referer">Validate me</a>
    </div>
</body>
</html>
""",

# -----------------------------------------------------------------------------

opj("input", "index.md"): """
title: home
menu-position: 0
---

## Welcome to Poole

In Poole you write your pages in [markdown][md]. It's easier to write
markdown than HTML.

Poole is made for simple websites you just want to get done, without installing
a bunch of requirements and without learning a template engine.

In a build, Poole copies every file from the *input* directory to the *output*
directory. During that process every markdown file (ending with *md*, *mkd*,
*mdown* or *markdown*) is converted to HTML using the project's `page.html`
as a skeleton.

[md]: http://daringfireball.net/projects/markdown/
""",

# -----------------------------------------------------------------------------

opj("input", "logic.md"): """
menu-position: 4
---
Poole has basic support for content generation using Python code inlined in
page files. This is everything but a clear separation of logic and content but
for simple sites this is just a pragmatic way to get things done fast.
For instance the menu on this page is generated by some inlined Python code in
the project's `page.html` file.

Just ignore this feature if you don't need it :)

Content generation by inlined Python code is good to add some zest to your
site. If you use it a lot, you better go with more sophisticated site
generators like [Hyde](http://ringce.com/hyde). 
""",

# -----------------------------------------------------------------------------

opj("input", "layout.md"): """
menu-position: 3
---
Every page of a poole site is based on *one global template file*, `page.html`.
All you need to adjust the site layout is to
 
 * edit the page template `page.html` and
 * extend or edit the style file `input/poole.css`.
""",

opj("input", "blog.md"): """
menu-position: 10
---
Poole has basic blog support. If an input page's file name has a structure like
`page-title.YYYY-MM-DD.post-title.md`, e.g. `blog.201010-02-27.read_this.md`,
Poole recognizes the date and post title and sets them as attributes of the
page. These attributes can then be used to generate a list of blog posts:

<!--%
from datetime import datetime
posts = [p for p in pages if "post" in p] # get all blog post pages
posts.sort(key=lambda p: p.get("date"), reverse=True) # sort post pages by date
for p in posts:
    date = datetime.strptime(p.date, "%Y-%m-%d").strftime("%B %d, %Y")
    print "  * **[%s](%s)** - %s" % (p.post, p.url, date) # markdown list item
%-->

Have a look into `input/blog.md` to see how it works. Feel free to adjust it
to your needs.
""",

# -----------------------------------------------------------------------------

opj("input", "blog.2010-02-22.Doctors_in_my_penguin.md") : """

---
## {{ page["post"] }}

*Posted at
<!--%
from datetime import datetime
print datetime.strptime(page["date"], "%Y-%m-%d").strftime("%B %d, %Y")
%-->*

There is a bank in my eel, your argument is invalid.

More nonsense at <http://automeme.net/>.
""",

# -----------------------------------------------------------------------------

opj("input", "blog.2010-03-01.I_ate_all the pokemans.md"): """

## {{ page["post"] }}

*Posted at <!--{ page["date"] }-->.*

What *are* interior crocodile alligators? We just don't know.

More nonsense at <http://automeme.net/>.
""",

# -----------------------------------------------------------------------------

opj("input", "poole.css"): """
body {
    font-family: sans;
    width: 800px;
    margin: 1em auto;
    color: #2e3436;
}
div#box {
    border: solid #2e3436 1px;
}
div#header, div#menu, div#content, div#footer {
    padding: 1em;
}
div#menu {
    background-color: #2e3436;
    padding: 0.6em 0 0.6em 0;
}
#menu span {
    background-color: #2e3436;
    font-weight: bold;
    padding: 0.6em;
}
#menu span.current {
    background-color: #555753;
}
#menu a {
    color: #fefefc;
    text-decoration: none;
}
div#footer {
    color: gray;
    text-align: center;
    font-size: small;
}
div#footer a {
    color: gray;
    text-decoration: none;
}
pre {
    border: dotted black 1px;
    background: #eeeeec;
    font-size: small;
    padding: 1em;
}

"""
}

def init(project):
    """Initialize a site project."""
    
    if not opx(project):
        os.makedirs(project)
        
    if os.listdir(project):
        print("error  : project dir %s is not empty, abort" % project)
        sys.exit(1)
    
    os.mkdir(opj(project, "input"))
    os.mkdir(opj(project, "output"))
    
    for fname, content in EXAMPLE_FILES.items():
        with open(opj(project, fname), 'w') as fp:
            fp.write(content)

    print("success: initialized project")

# =============================================================================
# build site
# =============================================================================

MKD_PATT = r'\.(?:md|mkd|mdown|markdown)$'

class Page(dict):
    """Abstraction of a source page."""
    
    _re_eom = r'^---+ *\n?$'
    _sec_macros = "macros"
    _modmacs = None
    
    def __init__(self, templ, fname, strip, opts):
        """Create a new page.
        
        @param templ: template dictionary
        @param fname: full path to page input file
        @param strip: portion of path to strip from `fname` for deployment
        @param opts: command line options
        
        """
        super(Page, self).__init__()
        
        self.update(templ)
        
        self["url"] = re.sub(MKD_PATT, ".html", fname)
        self["url"] = self["url"][len(strip):].lstrip(os.path.sep)
        self["url"] = self["url"].replace(os.path.sep, "/")
        
        self["fname"] = fname
        
        with codecs.open(fname, 'r', opts.input_enc) as fp:
            self.raw = fp.readlines()
        
        # split raw content into macro definitions and real content
        vardefs = ""
        self.source = ""
        for line in self.raw:
            if not vardefs and re.match(self._re_eom, line):
                vardefs = self.source
                self.source = "" # only macro defs until here, reset source
            else:
                self.source += line

        # evaluate macro definitions
        tfname = ".page-macros.tmp"
        with codecs.open(tfname, "w", opts.input_enc) as tf:
            tf.write("[%s]\n" % self._sec_macros)
            tf.write(vardefs)
        with codecs.open(tfname, "r", opts.input_enc) as tf:
            cp = SafeConfigParser()
            cp.readfp(tf)
        os.remove(tfname)
        for key in cp.options(self._sec_macros):
            self[key] = cp.get(self._sec_macros, key)
        
        basename = os.path.basename(fname)
        
        fpatt = r'(.+?)(?:\.([0-9]+-[0-9]+-[0-9]+)(?:\.(.*))?)?%s' % MKD_PATT
        title, date, post = re.match(fpatt, basename).groups()
        title = title.replace("_", " ")
        post = post and post.replace("_", " ") or None
        self["title"] = self.get("title", title)
        if date and "date" not in self: self["date"] = date
        if post and "post" not in self: self["post"] = post
        
    def __getattribute__(self, name):
        
        try:
            return super(Page, self).__getattribute__(name)
        except AttributeError, e:
            if name in self:
                return self[name]
            raise e
        
def build(project, opts):
    """Build a site project."""
    
    # -------------------------------------------------------------------------
    # utilities
    # -------------------------------------------------------------------------

    def abort_iex(page, itype, inline, exc):
        """Abort because of an exception in inlined Python code."""
        print("error  : Python %s in %s failed" % (itype, page.fname))
        print((" %s raising the exception " % itype).center(79, "-"))
        print(inline)
        print(" exception ".center(79, "-"))
        print(exc)
        sys.exit(1)
        
    # -------------------------------------------------------------------------
    # regex patterns and replacements
    # -------------------------------------------------------------------------
    
    regx_escp = re.compile(r'\\((?:(?:&lt;|<)!--|{)(?:{|%))') # escaped code
    repl_escp = r'\1'
    regx_rurl = re.compile(r'(?<=(?:(?:\n| )src|href)=")([^#/&].*?)(?=")')
    repl_rurl = lambda m: urlparse.urljoin(opts.base_url, m.group(1))
    
    regx_eval = re.compile(r'(?<!\\)(?:(?:<!--|{){)((?:.*?\n?)*)(?:}(?:-->|}))')

    def repl_eval(m):
        """Replace a Python expression block by its evaluation."""
        
        expr = m.group(1)
        try:
            repl = eval(expr, macros.copy())
        except:
            abort_iex(page, "expression", expr, traceback.format_exc())
        else:
            if not isinstance(repl, basestring):
                repl = str(repl)
            elif not isinstance(repl, unicode):
                repl = repl.decode("utf-8")
            return repl

    regx_exec = re.compile(r'(?<!\\)(?:(?:<!--|{)%)((?:.*?\n?)*)(?:%(?:-->|}))')
    
    def repl_exec(m):
        """Replace a block of Python statements by their standard output."""
        
        stmt = m.group(1)
        
        # base indentation
        ind_lvl = len(re.findall(r'^(?: *\n)*( *)', stmt, re.MULTILINE)[0])
        ind_rex = re.compile(r'^ {0,%d}' % ind_lvl, re.MULTILINE)
        stmt = ind_rex.sub('', stmt)
        
        # execute
        sys.stdout = StringIO.StringIO()
        try:
            exec stmt in macros.copy()
        except:
            sys.stdout = sys.__stdout__
            abort_iex(page, "statements", stmt, traceback.format_exc())
        else:
            repl = sys.stdout.getvalue()[:-1] # remove last line break
            sys.stdout = sys.__stdout__
            return repl.decode(opts.input_enc)
    
    # -------------------------------------------------------------------------
    # preparations
    # -------------------------------------------------------------------------
    
    dir_in = opj(project, "input")
    dir_out = opj(project, "output")
    page_html = opj(project, "page.html")

    # check required files and folders
    for pelem in (page_html, dir_in, dir_out):
        if not opx(pelem):
            print("error  : %s does not exist, looks like project has not been "
                  "initialized, abort" % pelem)
            sys.exit(1)

    # prepare output directory
    for fod in glob.glob(opj(dir_out, "*")):
        if os.path.isdir(fod):
            shutil.rmtree(fod)
        else:
            os.remove(fod)
    if not opx(dir_out):
        os.mkdir(dir_out)

    # macro module
    class nomod: pass # dummy module, something we can set attributes on
    fname = opj(opts.project, "macros.py")
    macros = {"__encoding__": opts.output_enc}
    macmod = opx(fname) and imp.load_source("macros", fname) or nomod
    setattr(macmod, "options", opts)
    setattr(macmod, "project", opts.project)
    setattr(macmod, "input", os.path.join(opts.project, "input"))
    setattr(macmod, "output", os.path.join(opts.project, "output"))
    for attr in dir(macmod):
        if not attr.startswith("_"):
            macros[attr] = getattr(macmod, attr)

    # -------------------------------------------------------------------------
    # process input files
    # -------------------------------------------------------------------------
    
    pages = []
    page_global = macros.get("page", {})
    for cwd, dirs, files in os.walk(dir_in):
        cwd_site = cwd[len(dir_in):].lstrip(os.path.sep)
        for sdir in dirs:
            if re.search(opts.ignore, sdir): continue
            os.mkdir(opj(dir_out, cwd_site, sdir))
        for f in files:
            if re.search(opts.ignore, f):
                pass
            elif re.search(MKD_PATT, f):
                page = Page(page_global, opj(cwd, f), dir_in, opts)
                pages.append(page)
            else:
                shutil.copy(opj(cwd, f), opj(dir_out, cwd_site))

    macros["pages"] = pages
    macmod.pages = pages
    
    # -------------------------------------------------------------------------
    # run 'once' functions in macro module
    # -------------------------------------------------------------------------

    for fn in [a for a in dir(macmod) if a.startswith("once_")]:
        getattr(macmod, fn)()

    # -------------------------------------------------------------------------
    # convert pages
    # -------------------------------------------------------------------------
    
    with codecs.open(opj(project, "page.html"), 'r', opts.input_enc) as fp:
        skeleton = fp.read()
    
    for page in pages:
        
        print("info   : processing %s" % page.fname)

        macros["page"] = page
        macmod.page = page
        
        # replacements, phase 1 (expressions and statements in page source)
        out = regx_eval.sub(repl_eval, page.source)
        out = regx_exec.sub(repl_exec, out)
        
        # convert to HTML
        out = markdown.Markdown().convert(out)
        
        # replacements, phase 2 (variables and code blocks used in page.html)
        macros["__content__"] = out
        out = regx_eval.sub(repl_eval, skeleton)
        out = regx_exec.sub(repl_exec, out)
        
        # un-escape escaped python code blocks
        out = regx_escp.sub(repl_escp, out)
        
        # make relative links absolute
        out = regx_rurl.sub(repl_rurl, out)
        
        # write HTML page
        fname = page.fname.replace(dir_in, dir_out)
        fname = re.sub(MKD_PATT, ".html", fname)
        with codecs.open(fname, 'w', opts.output_enc) as fp:
            fp.write(out)

    print("success: built project")

# =============================================================================
# serve site
# =============================================================================

def serve(project, port):
    """Temporary serve a site project."""
    
    root = opj(project, "output")
    if not os.listdir(project):
        print("error  : output dir is empty (build project first!), abort")
        sys.exit(1)
    
    os.chdir(root)
    server = HTTPServer(('', port), SimpleHTTPRequestHandler)
    server.serve_forever()

# =============================================================================
# options
# =============================================================================

def options():
    """Parse and validate command line arguments."""
    
    usage = ("Usage: %prog --init [path/to/project]\n"
             "       %prog --build [OPTIONS] [path/to/project]\n"
             "       %prog --serve [OPTIONS] [path/to/project]\n"
             "\n"
             "       Project path is optional, '.' is used as default.")
    
    op = optparse.OptionParser(usage=usage)
    
    op.add_option("-i" , "--init", action="store_true", default=False,
                  help="init project")
    op.add_option("-b" , "--build", action="store_true", default=False,
                  help="build project")
    op.add_option("-s" , "--serve", action="store_true", default=False,
                  help="serve project")
    
    og = optparse.OptionGroup(op, "Build options")
    og.add_option("", "--base-url", default="/", metavar="URL",
                  help="base url for relative links (default: /)")
    og.add_option("", "--input-enc", default="utf-8", metavar="ENC",
                  help="encoding of input pages (default: utf-8)")
    og.add_option("", "--output-enc", default="utf-8", metavar="ENC",
                  help="encoding of output pages (default: utf-8)")
    og.add_option("" , "--ignore", default=r"^\.|~$", metavar="REGEX",
                  help="input files to ignore (default: '^\.|~$')")
    op.add_option_group(og)
    
    og = optparse.OptionGroup(op, "Serve options")
    og.add_option("" , "--port", default=8080,
                  metavar="PORT", type="int",
                  help="port for serving (default: 8080)")
    op.add_option_group(og)
    
    opts, args = op.parse_args()
    
    if opts.init + opts.build + opts.serve < 1:
        op.print_help()
        op.exit()
    
    opts.project = args and args[0] or "."
    
    return opts
    
# =============================================================================
# main
# =============================================================================

def main():
    
    opts = options()
    
    if opts.init:
        init(opts.project)
    if opts.build:
        build(opts.project, opts)
    if opts.serve:
        serve(opts.project, opts.port)

if __name__ == '__main__':
    
    main()
