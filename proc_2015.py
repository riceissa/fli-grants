#!/usr/bin/env python3
# License: CC0 https://creativecommons.org/publicdomain/zero/1.0/

from bs4 import BeautifulSoup


def main():
    with open("2015-grants.html", "r") as f:
        soup = BeautifulSoup(f, "lxml")
        project_grants, center_grants, conference_grants = soup.find_all("table")

        print("""insert into donations (donor, donee, donation_earmark,
        amount, donation_date,
        donation_date_precision, donation_date_basis, cause_area, url,
        donor_cause_area_url, notes, affected_countries, affected_states,
        affected_cities, affected_regions) values""")

        print_table_info(project_grants, "project grant", True)
        print_table_info(center_grants, "center grant")
        print_table_info(conference_grants, "conference and education grant")

        print(";")


def print_table_info(table, grants_type, first_group=False):
    """Find and return the fields we care about for the given table."""
    first = first_group

    for tr in table.find_all("tr"):
        cells = tr.find_all("td")
        if cells[0].text.strip() == "Primary Investigator":
            # This is the header row, so skip it
            continue
        investigator, institution = cells[0].text.strip().split(", ", maxsplit=1)
        project = cells[1].text.strip()
        url = cells[1].find("a").get("href")
        amount = cells[2].text.strip()
        assert amount.startswith("$"), amount
        amount = float(amount.replace("$", "").replace(",", ""))

        if investigator == "Katja Grace":
            institution = "AI Impacts"

        # cell[3] exists but contains the investigator email, which we
        # don't care about

        print(("    " if first else "    ,") + "(" + ",".join([
            mysql_quote("Future of Life Institute"),  # donor
            mysql_quote(institution),  # donee
            mysql_quote(investigator),  # donation_earmark
            str(amount),  # amount
            # The donation date is from
            # https://timelines.issarice.com/wiki/Timeline_of_AI_safety
            # (see the event for July 1, 2015).
            mysql_quote("2015-09-01"),  # donation_date
            mysql_quote("day"),  # donation_date_precision
            mysql_quote("donation log"),  # donation_date_basis
            mysql_quote("AI risk"),  # cause_area
            mysql_quote(url),  # url
            mysql_quote(""),  # donor_cause_area_url
            mysql_quote(("A {}. "
                         "Project title: {}.").format(grants_type,
                                                      investigator,
                                                      project)),  # notes
            mysql_quote(""),  # affected_countries
            mysql_quote(""),  # affected_states
            mysql_quote(""),  # affected_cities
            mysql_quote(""),  # affected_regions
        ]) + ")")
        first = False


def mysql_quote(x):
    '''
    Quote the string x using MySQL quoting rules. If x is the empty string,
    return "NULL". Probably not safe against maliciously formed strings, but
    whatever; our input is fixed and from a basically trustable source..
    '''
    if not x:
        return "NULL"
    x = x.replace("\\", "\\\\")
    x = x.replace("'", "''")
    x = x.replace("\n", "\\n")
    return "'{}'".format(x)


if __name__ == "__main__":
    main()
