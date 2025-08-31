from bs4 import BeautifulSoup, Tag

def is_element_hidden(element: Tag) -> bool:
    """
    Checks if an element is hidden via inline CSS styles, including its parents.
    """
    for parent in [element] + list(element.parents):
        style = parent.get('style', '').lower().replace(' ', '')
        if 'display:none' in style or 'visibility:hidden' in style:
            return True
    return False

def remove_honeypots(soup: BeautifulSoup) -> BeautifulSoup:
    """
    Finds and removes likely "honeypot" links from a parsed HTML document.

    A honeypot link is an <a> tag that is not visible to a human user,
    designed to trap web scrapers.

    This function targets links that are explicitly hidden using inline CSS
    styles like 'display: none' or 'visibility: hidden', checking both the
    element itself and its parent containers.
    """
    # Find all links in the document
    links = soup.find_all('a')

    for link in links:
        if is_element_hidden(link):
            link.decompose()

    return soup
