#!/usr/local/bin/python3

tags = {
    "Rechnung": "Rechnung",
    "Beleg": "Rechnung"
}
ocrLanguage = "deu"
verbose = False

import sys, subprocess

def run(*args):
    if verbose:
        print("running %r" % (args, ))
    result = subprocess.run(args, stdout=subprocess.PIPE)
    return result.stdout.decode(sys.getfilesystemencoding()).strip()

def ocr(theFile):
    return run("/usr/bin/osascript", "-l", "JavaScript", "-e", ("""
        app = Application("PDFScanner");
        try {
            process = app.ocr(Path("%(theFile)s"), {
              inLanguage: "%(ocrLanguage)s"
            });

            do {
              delay(1);
              status = app.statusOf(process);
            } while(status != "finished" && status != "error");

            error = app.errorFor(process);
            app.quit();
        } catch(e) {
            error = e;
        }

        error != null ? error : "";
    """ % { "theFile": theFile, "ocrLanguage": ocrLanguage }).replace("\n", " "))

def pdf_to_text(theFile):
    return run("/usr/local/bin/pdftotext", theFile, "-")

def find_tags(choices, text, max_dist=3):
    from fuzzysearch import find_near_matches
    ltext = text.lower()
    
    choicetype = type(choices)
    if choicetype is dict:
        choices = list(choices.items())
    lchoices = [choice.lower() if type(choice) != tuple else choice[0].lower() for choice in choices]
    
    for dist in range(0, max_dist + 1):
        lens = [len(find_near_matches(choice, ltext, max_l_dist=dist)) for choice in lchoices]
        tags = [choice for l, choice in zip(lens, choices) if l]
        if tags:
            break
    return choicetype(tags)

def tag(theFile, tags):
    return run("/usr/local/bin/tag", "--add", ",".join(tags), theFile)

def notify(title, message, theFile=None):
    icon = "/Applications/Preview.app/Contents/Resources/Preview.icns"
    notifier = ["/usr/local/bin/terminal-notifier", "-title", title, "-message", message, "-appIcon", icon]
    if theFile:
        from os.path import basename, abspath
        run("/usr/bin/qlmanage", "-ti", theFile, "-s", "512", "-o", "/tmp")
        notifier += ["-open", "file://" + abspath(theFile), "-contentImage", "/tmp/" + basename(theFile) + ".png"]
    run(*notifier)

def main():
    if verbose:
        print("Processing %r" % theFile)
    error = ocr(theFile)
    if error:
        notify("OCR error", error, theFile)
        sys.exit(1)

    text = pdf_to_text(theFile)
    if verbose:
        print("Found text %r" % text)
    theTags = find_tags(tags, text)
    if not theTags:
        notify("Tagging error", "Could not find tags for "+ theFile, theFile)
        sys.exit(1)
    
    reasons = {}
    for k, v in theTags.items():
        reasons.setdefault(v, []).append(k)
    
    tag(theFile, reasons.keys())
    notify("Finished", "Tagged " + theFile + " with " + ", ".join("{} because of Text '{}'".format(k, ", ".join(v)) for k, v in reasons.items()), theFile)

if __name__ == "__main__":
    theFile = sys.argv[1]
    main()
