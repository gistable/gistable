#  citeabook.py
#  
#  Licence AGPLv3 by rezemika.
#  

import sys
import requests
import datetime

# TODO : Check ISBN.

class Book:
    def __init__(self, book_json):
        # Google
        self.google_id = book_json["id"]
        # Meta
        meta = book_json["volumeInfo"]
        self.google_link = meta["previewLink"].replace("&source=gbs_api", "")
        self.title = meta["title"]
        self.publisher = meta["publisher"]
        self.authors = []
        for author in meta["authors"]:
            self.authors.append(author)
        self.publish_date = datetime.datetime.strptime(meta["publishedDate"], "%Y-%m-%d")
        try:
            self.pages = meta["pageCount"]
        except KeyError:
            self.pages = meta["printedPageCount"]
        self.language = meta["language"]
        # ISBNs
        isbns = []
        self.isbn10 = ''
        self.isbn13 = ''
        for identifier in meta["industryIdentifiers"]:
            if identifier["type"] == "ISBN_10":
                self.isbn10 = identifier["identifier"]
            elif identifier["type"] == "ISBN_13":
                self.isbn13 = identifier["identifier"]
        return

def format_plaintext(args, book):
    if book.isbn13:
        isbn = book.isbn13
    elif book.isbn10:
        isbn = book.isbn10
    else:
        isbn = "inconnu"
    format_string = "{author}. {title}. {publisher}; {year}{retrieve_date}. ISBN {isbn}."
    formatted_string = format_string.format(
        author=', '.join(book.authors),
        title=book.title,
        publisher=book.publisher,
        year=book.publish_date.year,
        retrieve_date='',  # TODO
        isbn=isbn
    )
    print(formatted_string)
    return

def format_markdown(args, book):
    if book.isbn13:
        isbn = book.isbn13
    elif book.isbn10:
        isbn = book.isbn10
    else:
        isbn = "inconnu"
    format_string = "{author}. [*{title}*]({link}). {publisher}; {year}{retrieve_date}. ISBN {isbn}."
    formatted_string = format_string.format(
        author=', '.join(book.authors),
        title=book.title,
        link=book.google_link,
        publisher=book.publisher,
        year=book.publish_date.year,
        retrieve_date='',  # TODO
        isbn=isbn
    )
    return formatted_string

def main(args):
    output_type = get_var_option(args, "out")[0]
    if not output_type:
        print("Error: Please specify an output type.")
        exit(0)
    if output_type not in ["markdown", "plaintext"]:
        print("Error: '{}' is not a valid output type.".format(output_type))
        exit(0)
    if output_type == "markdown":
        formater = format_markdown
    elif output_type == "plaintext":
        formater = format_plaintext
    
    isbn = get_var_option(args, "isbn")[0].replace('-', '')
    if not isbn:
        print("Error: Please specify an ISBN.")
        exit(0)
    if len(isbn) not in [10, 13]:
        print("Error: Invalid ISBN.")
        exit(0)
    
    json_book = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:" + isbn).json()
    book = Book(json_book["items"][0])
    print(formater(args, book))
    return

main_help = """\
CiteABook: A simple script which outputs a formatted string citing a book from its ISBN.

Usage: citeabook.py --out=<plaintext/markdown> --isbn=<ISBN>\
"""
__version__ = "0.1.0"

def command_parser(args):
    parsed_args = {"commands": [], "options": [], "var_options": [], "sysargv": args}
    args = args[1:]
    for arg in args:
        if arg.startswith('--'):
            if '=' not in arg:
                parsed_args["options"].append(arg[2:])
            else:
                option, var = arg.split('=', 1)
                parsed_args["var_options"].append((option[2:], var))
        else:
            parsed_args["commands"].append(arg)
    return parsed_args

def get_var_option(args, arg, default=''):
    output = ''
    if args["var_options"]:
        output = [couple[1] for couple in args["var_options"] if couple[0] == arg]
    if not output:
        return default
    else:
        return output

if __name__ == '__main__':
    args = command_parser(sys.argv)
    # Prints the main help if there is no command.
    if len(args["commands"]) == 0 and "help" in args["options"]:
        print(main_help)
        exit(0)
    # Prints the script's version.
    if "version" in args["options"]:
        print("CiteABook: v{}".format(__version__))
        exit(0)
    main(args)
    exit(0)
