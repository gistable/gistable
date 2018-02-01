"""

Free to use under the MIT license

Builds a static site from a list of Markdown source files. The source
files should have the same directory structure as the desired output.

Files are rendered using Markdown2 and can declare metadata variables:

    ---
    template: index.html
    title: My Title
    ---

    # your makdown doc from here on

Site templates are stored in the `templates` folder and should be Jinja2
templates. Apart from the `template` meta variable in markdown documents, 
any variables supplied in the Markdown meta will be available in the 
template under the same name. The variable `title` given above can therefore
be accessed.

The static site will be exported to the `build` directory
"""

from jinja2 import Environment, FileSystemLoader, TemplateNotFound
import markdown2
import os
import shutil

# include additional markdown 2 extras here (e.g. tables, footnotes etc)
MARKDOWN_EXTRAS = ['metadata']

# folders that should be copied from your `src` directory to the `build` directory
STATIC_DIRS = ['images']

def files_with_extension(dir, ext):
    """
    Gets all files in the given directory with the given extension
    """
    return [x for x in os.listdir(dir) if x.endswith(ext)]

def copy_directory(src, dst):
    """
    Copies all the contents from the source directory to the output directory
    """

    print "Copying {0} to {1}".format(src, dst)

    try:
        shutil.copytree(src, dst)
    except OSError as e:
        print "  > There was an error copying the files from {0} to {1}".format(src, dst)
        print "  > {0}".format(e)

def get_templates(path):
    """
    Compiles all the templates in the template directory and
    returns a dictionary of Jinja2 `Template` objects with the
    file names as the keys
    """
    return Environment(loader=FileSystemLoader(path))

def build_directory(templates, input_path):
    """
    Takes all the *.md files in the given directory, builds them into
    HTML and renders them using the Jinja templates. The rendered markdown
    is available in the Jinja templates as the `content` variable.

    ::warning:: There can only be one `src` folder in the path, as the script
    directly replaces `src` with `build` once to find the output path
    """
    print "Looking for Markdown files in {0}".format(input_path)
    files = files_with_extension(input_path, ".md")
    op_dir = input_path.replace("src","build", 1)

    if not os.path.isdir(op_dir):
        os.mkdir(op_dir)
        os.chmod(op_dir, 0o777)

    for f in files:
        print "Converting {0}".format(f)

        ip_path = os.path.join(input_path, f)
        with open(ip_path, 'r') as ip:
            raw_html = markdown2.markdown(ip.read(), extras=MARKDOWN_EXTRAS)

        try:
            template = raw_html.metadata['template']
        except KeyError:
            print "WARNING: No template specified for {0}, using index.html".format(f)
            template = "index.html"

        try:
            tpl = templates.get_template(template)
        except TemplateNotFound:
            raise Exception("Unable to locate the template {0} for file {1}. Aborting".format(template, f))

        context = raw_html.metadata
        context['content'] = raw_html
        result = tpl.render(context)

        op_path = os.path.join(op_dir, f.replace(".md", ".html"))
        print "Writing to {0}".format(op_path)

        with open(op_path, 'w+') as op:
            op.write(result)

        print "  > Rendered files at {0} to {1}".format(ip_path, op_path)

    print "Folder complete"

def build_site(template_dir, ip_dir, clean=True):
    """
    Gets all the markdown files in the `src` directory, renders them using the template
    given in metadata (or `index.html`) if no template given, and then throws them in the
    same directory structure in the `build` folder.

    Additionally everything in the `templates/static` folder is copied to `build/static`
    """

    # delete the old build
    if clean:
        op_dir = ip_dir.replace("src", "build", 1)
        print "Cleaning out old files from {0}".format(op_dir)

        try:
            shutil.rmtree(op_dir)
        except Exception as e:
            print "  > ERROR - Unable to clean the old build directory"
            print "  > {0}".format(e)

        try:
            os.mkdir(op_dir)
            os.chmod(op_dir, 0o777)
            print "Created output directory"
        except Exception as e:
            print "  > ERROR - Unable to create a directory at {0}".format(op_dir)
            print "  > {0}".format(e)


    # copy the `templates/static` folder to `build/static`
    src = os.path.join(template_dir, "static")
    dst = os.path.join(ip_dir.replace("src", "build", 1), "static")
    copy_directory(src, dst)

    # copy all the static files
    for sd in STATIC_DIRS:
        src = os.path.join(ip_dir, sd)
        dst = os.path.join(ip_dir.replace("src", "build", 1), sd)
        copy_directory(src, dst)

    # load the templates
    templates = get_templates(template_dir)

    # Do the root directory
    build_directory(templates, ip_dir)

    # get all the source directories
    for path, dir, files in os.walk(ip_dir):
        for d in dir:
            build_directory(templates, os.path.join(path, d))

    print "Site build complete"


if __name__ == '__main__':

    # get the input and template dir paths
    dir = os.getcwd()
    template_dir = os.path.join(dir, "templates")
    input = os.path.join(dir, "src")

    # build the site
    build_site(template_dir, input)
