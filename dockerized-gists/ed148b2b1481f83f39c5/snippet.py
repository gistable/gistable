import re
import click

# (1) My gettext helpers are _() and _n(), replace them by yours if necessary.
# (2) I've used the exact same messages in translations, you can adapt them.

def translate_click_exception(e):
    """
    Analyse a click exception, translate its message using gettext
    and re-raise it in current language.
    """
    if isinstance(e, click.exceptions.UsageError):
        match = re.search(
            r"^Got unexpected extra argument(s?) \((.+?)\)$",
            e.message)
        if(match):
            # Complex plural form will not be handled properly, as we have
            # no exact way to know how much extra arguments have been
            # passed. Using 2 as the threshold.
            raise click.exceptions.UsageError(_n(
                "Got unexpected extra argument (%s)",
                "Got unexpected extra arguments (%s)",
                2 if match.group(1) else 1)
                % match.group(2))

        if(e.message == "Missing command."):
            raise click.exceptions.UsageError(_("Missing command."))

        match = re.search(r"^No such command \"(.+?)\"\.$", e.message)
        if(match):
            raise click.exceptions.UsageError(
                _('No such command "%s".')
                % match.group(1))

        raise e
    if isinstance(e, click.exceptions.BadParameter):
        def translate_file_type(type):
            if(type == "Path"):
                return _("Path")
            elif(type == "Directory"):
                return _("Path")
            else:
                return _("File")

        match = re.search(
            r"^invalid choice: (.+?)\. \(choose from (.+?)%s\)$",
            e.message)
        if(match):
            raise click.exceptions.BadParameter(_(
                "invalid choice: %s. (choose from %s)")
                % (match.group(1), match.group(2)))

        match = re.search(r"^(.+?) is not a valid integer$", e.message)
        if(match):
            raise click.exceptions.BadParameter(_(
                "%s is not a valid integer")
                % match.group(1))

        match = re.search(
            r"^(.+?) is bigger than the maximum valid value (.+?)\.$",
            e.message)
        if(match):
            raise click.exceptions.BadParameter(_(
                "%s is bigger than the maximum valid value %s.")
                % (match.group(1), match.group(2)))

        match = re.search(
            r"^(.+?) is smaller than the minimum valid value (.+?)\.$",
            e.message)
        if(match):
            raise click.exceptions.BadParameter(_(
                "%s is smaller than the minimum valid value %s.")
                % (match.group(1), match.group(2)))

        match = re.search(
            r"^(.+?) is not in the valid range of (.+?) to (.+?)\.$",
            e.message)
        if(match):
            raise click.exceptions.BadParameter(_(
                "%s is not in the valid range of %s to %s.")
                % (match.group(1), match.group(2), match.group(3)))

        match = re.search(r"^(.+?) is not a valid boolean$", e.message)
        if(match):
            raise click.exceptions.BadParameter(_(
                "%s is not a valid boolean")
                % match.group(1))

        match = re.search(
            r"^(.+?) is not a valid floating point value$",
            e.message)
        if(match):
            raise click.exceptions.BadParameter(_(
                "%s is not a valid floating point value")
                % match.group(1))

        match = re.search(r"^(.+?) is not a valid UUID value$", e.message)
        if(match):
            raise click.exceptions.BadParameter(_(
                "%s is not a valid UUID value")
                % match.group(1))

        match = re.search(r"^Could not open file: (.+?): (.+?)$", e.message)
        if(match):
            # Second string will not be localized
            raise click.exceptions.BadParameter(_(
                "Could not open file: %s: %s")
                % (match.group(1), match.group(2)))

        match = re.search(r"^(.+?) \"(.+?)\" does not exist\.$", e.message)
        if(match):
            raise click.exceptions.BadParameter(_(
                '%s "%s" does not exist.')
                % (translate_file_type(match.group(1)), match.group(2)))

        match = re.search(r"^(.+?) \"(.+?)\" is a file\.$", e.message)
        if(match):
            raise click.exceptions.BadParameter(_(
                '%s "%s" is a file.')
                % (translate_file_type(match.group(1)), match.group(2)))

        match = re.search(r"^(.+?) \"(.+?)\" is a directory\.$", e.message)
        if(match):
            raise click.exceptions.BadParameter(_(
                '%s "%s" is a directory.')
                % (translate_file_type(match.group(1)), match.group(2)))

        match = re.search(r"^(.+?) \"(.+?)\" is not writable\.$", e.message)
        if(match):
            raise click.exceptions.BadParameter(_(
                '%s "%s" is not writable.')
                % (translate_file_type(match.group(1)), match.group(2)))

        match = re.search(r"^(.+?) \"(.+?)\" is not readable\.$", e.message)
        if(match):
            raise click.exceptions.BadParameter(_(
                '%s "%s" is not readable.')
                % (translate_file_type(match.group(1)), match.group(2)))
        raise e
    if isinstance(e, click.exceptions.Abort):
        raise click.exceptions.Abort(_("Execution aborted."))
    raise e


def standard_execution(
    self, args=None, prog_name=None,
    complete_var=None, standalone_mode=False, **extra
):
    """
    Monkey patch click.Command.main to invert the default value of
    standalone_mode param so that exceptions are not trapped by
    click library.
    """
    super(click.Command, self).main(
        args, prog_name, complete_var, standalone_mode, **extra)


click.Command.main = standard_execution


try:
    # Replace by your main command.
    cli()
except click.exceptions.ClickException as e:
    translate_click_exception(e)