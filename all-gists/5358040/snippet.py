from django import template

register = template.Library()

@register.simple_tag
def format_date_range(date_from, date_to, separator=" - ",
    format_str="%B %d, %Y", year_f=", %Y", month_f="%B", date_f=" %d"):
    """ Takes a start date, end date, separator and formatting strings and
        returns a pretty date range string
    """
    if (date_to and date_to != date_from):
        from_format = to_format = format_str
        if (date_from.year == date_to.year):
            from_format = from_format.replace(year_f, '')
            if (date_from.month == date_to.month):
                to_format = to_format.replace(month_f, '')
        return separator.join((date_from.strftime(from_format), date_to.strftime(to_format)))
    else:
        return date_from.strftime(format_str)