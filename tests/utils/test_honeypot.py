import pathlib
from bs4 import BeautifulSoup
from paddock_parser.utils.honeypot import remove_honeypots

def test_remove_honeypots():
    """
    Tests that the honeypot removal utility correctly identifies and removes
    links that are hidden via inline styles, including those in parent containers.
    """
    # Path to the HTML fixture
    fixture_path = pathlib.Path(__file__).parent / "honeypot_sample.html"

    # Read the HTML content
    with open(fixture_path, "r") as f:
        html_content = f.read()

    # Create a soup object
    soup = BeautifulSoup(html_content, "lxml")

    # --- Assert initial state ---
    initial_links = soup.find_all('a')
    assert len(initial_links) == 5
    assert initial_links[0].get('href') == '/visible-link-1'
    assert initial_links[1].get('href') == '/honeypot-1'
    assert initial_links[2].get('href') == '/visible-link-2'
    assert initial_links[3].get('href') == '/honeypot-2'
    assert initial_links[4].get('href') == '/honeypot-3'

    # --- Run the function ---
    cleaned_soup = remove_honeypots(soup)

    # --- Assert final state ---
    final_links = cleaned_soup.find_all('a')
    assert len(final_links) == 2

    final_hrefs = [link.get('href') for link in final_links]
    assert '/visible-link-1' in final_hrefs
    assert '/visible-link-2' in final_hrefs
    assert '/honeypot-1' not in final_hrefs
    assert '/honeypot-2' not in final_hrefs
    assert '/honeypot-3' not in final_hrefs
