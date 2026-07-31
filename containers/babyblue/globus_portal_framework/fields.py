import os
from urllib.parse import urlsplit, urlunsplit, urlencode, urlparse, parse_qs
import datetime
from typing import List, Mapping, Any


def globus_app_link(result):
    """A Globus Webapp link for the transfer/sync button on the detail page"""
    url = result[0]["url"]
    parsed_url = urlparse(url)
    query_params = {
        "origin_id": parse_qs(parsed_url.query)['origin_id'][0],
        "origin_path": parse_qs(parsed_url.query)['origin_path'][0],
    }
    return urlunsplit(
        ("https", "app.globus.org", "file-manager", urlencode(query_params), "")
    )


# This does not work for folders!
def https_url(result):
    """Add a direct download link to files over HTTPS"""
    path = urlsplit(result[0]["url"]).path
    return urlunsplit(("https", "g-a63a05.9601a.bd7c.data.globus.org", path, "", ""))



def search_highlights(result: List[Mapping[str, Any]]) -> List[Mapping[str, dict]]:
    """Prepare the most useful pieces of information for users on the search results page."""
    search_highlights = list()
    for name in ["BarcodeNumberIdentifier", "Bagging-Date", "AccessionNumberCollection", "OriginatingUnitDepartment", "AlternateID"]:
        value = result[0].get(name)
        value_type = "str"

        # Parse a date if it's a date. All dates expected isoformat
        if name == "Bagging-Date":
            value = datetime.datetime.fromisoformat(value)
            value_type = "date"
        elif name == "tags":
            value = ", ".join(value)

        # Add the value to the list
        search_highlights.append(
            {
                "name": name,
                "title": name.capitalize(),
                "value": value,
                "type": value_type,
            }
        )
    return search_highlights
