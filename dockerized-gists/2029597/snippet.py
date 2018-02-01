import re


def tracking_link_html(tracking_number):
    regex_handlers = [
        (r'\b(1Z ?[0-9A-Z]{3} ?[0-9A-Z]{3} ?[0-9A-Z]{2} ?[0-9A-Z]{4} ?[0-9A-Z]{3} ?[0-9A-Z]|[\dT]\d\d\d ?\d\d\d\d ?\d\d\d)\b', ups_link),
        (r'(\b96\d{20}\b)|(\b\d{15}\b)|(\b\d{12}\b)', fedex_link),
        (r'\b((98\d\d\d\d\d?\d\d\d\d|98\d\d) ?\d\d\d\d ?\d\d\d\d( ?\d\d\d)?)\b', fedex_link),
        (r'^[0-9]{12}$', fedex_link),
        (r'^[0-9]{10}$', dhl_link)
    ]

    for regex, link_method in regex_handlers:
        if re.match(regex, tracking_number):
            return link_method()  # return the link
    return tracking_number  # return the tracking number as a string


def fedex_link(tracking_number):
    return '<a href="http://www.fedex.com/Tracking?tracknumbers=%(num)s&action=track&language=english" target="_blank">%(num)s</a>' % {'num': tracking_number}


def ups_link(tracking_number):
    return '<a href="http://wwwapps.ups.com/WebTracking/processInputRequest?InquiryNumber1=%(num)s&sort_by=status&tracknums_displayed=1&TypeOfInquiryNumber=T&track.x=0&track.y=0" target="_blank">%(num)s</a>' % {'num': tracking_number}


def dhl_link(tracking_number):
    return '<a href="http://www.dhl.com/content/g0/en/express/tracking.shtml?brand=DHL&AWB=%(num)s" target="_blank">%(num)s</a>' % {'num': tracking_number}
