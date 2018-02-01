from bs4 import BeautifulSoup
import re
import requests


# Global parameters: CAMPUSonline"s base URL and its export URL
CO_BASE_URL = "https://campus.tum.de/tumonline/"
CO_EXPORT_URL = "wbKalender.wbExport?pMode=T"
APPOINTMENTS_PREFIX = "^Termine der LV.*"


def get_schedule_pages(target_url, pattern_courses):
    # Compile the course regex
    re_courses = re.compile(
        APPOINTMENTS_PREFIX + pattern_courses,
        re.IGNORECASE
        )
    with requests.Session() as s:
        r = s.get(CO_BASE_URL + target_url)
    soup = BeautifulSoup(r.content, "html.parser")
    # Get all links if their title is not empty and matches the regex
    links = (
        l for l in soup.find_all("a")
        if l.get("title") is not None and re_courses.search(l.get("title"))
        )
    # Return all hrefs with the prefixes base CAMPUSonline URL
    return [CO_BASE_URL + l.get("href") for l in links]


def scrape_appointment_ids(courses_url):
    appointment_ids = []
    for c in courses_url:
        with requests.Session() as s:
            r = s.get(c)
        soup = BeautifulSoup(r.content, "html.parser")
        # Find all elements of class "input" and
        # return their "value" if "name" matches "pTerminNr"
        appointment_ids.extend(
            e.get("value") for e in soup.find_all("input")
            if e.get("name") == "pTerminNr"
            )
    return appointment_ids


def send_export_post(appointment_ids):
    # "99" is a literal for ics export
    payload = {
        "pMaskAction": "DOWNLOAD",
        "pOutputFormat": "99",
        "pTerminNr": appointment_ids,
        }
    with requests.Session() as s:
        cal = s.post(CO_BASE_URL + CO_EXPORT_URL, data=payload).content
    return cal


if __name__ == "__main__":
    # Your organisation"s URL
    organisation_url = "wblvangebot.wbshowlvoffer?porgnr=15272"
    # Regex pattern for courses
    pattern_courses = "|".join([
        "übung",
        "tutorium",
        "vorlesung",
        "repetitorium",
        "praktikum",
        "exercise",
        "course",
        "lecture",
    ])
    pattern_courses = "(" + pattern_courses + ")"
    # Filename for the ics calendar
    cal_filename = "all_appointments.ics"

    sp_links = get_schedule_pages(organisation_url, pattern_courses)
    ids = scrape_appointment_ids(sp_links)
    all_cal = send_export_post(ids)

    with open(cal_filename, "wb") as f:
        f.write(all_cal)
