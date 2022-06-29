from dateutil import parser
from datetime import timezone


# def get_google_news_search_entries_from_date_to_date(_gn_obj, _search_term, start=None, end=None):
def get_entries(_gn_obj, _search_term, start=None, end=None, _when=None, _from=None, _to=None):
    """
    function get search term and retrieve entries from pyGoogleNews search object
    :param _gn_obj:         pyGoogleNews Object
    :param _search_term:    the actual term to search for in Google News (in our case - crypto coins)
    :param start:           start date 'YYYY-MM-DD'
    :param end:             start date 'YYYY-MM-DD'
    :param _when:           how far long to go in search: not always acting as expected -> no recommended
    :param _from:           start search from date : not always acting as expected -> no recommended
    :param _to:             search up to date: not always acting as expected -> no recommended
    :return: list of entries from pyGoogleSearch
    """
    # after:YYYY-MM-DD before:YYYY-MM-DD
    # using google 'smart' search using keywords 'after:' and  'before:'
    if start:
        _search_term += ' after:' + start
    if end:
        _search_term += ' before:' + end

    # ADD SOME TRY CATCH TO HANDLE CONNECTION LOSS
    search = _gn_obj.search(_search_term, when=_when, from_=_from, to_=_to)
    entries = search['entries']

    return entries


# def get_stories_from_entries(_entries):
def get_stories(_entries):
    """
    function extract stories from received pyGoogleSearch entries
    :param _entries: pyGoogleSearch entries
    :return: list of stories including story title, link, unique id, published time
    """
    stories = []
    for entry in _entries:
        story = {
            'title': entry['title'],
            'link': entry['link'],
            'id': entry['id'],
            'published': parser.parse(entry["published"]).replace(tzinfo=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            # 'published': entry['published']
        }
        stories.append(story)

    return stories


def get_titles(_stories):
    """
    function extract titles from received stories
    :param _stories: list of stories including story title, link, unique id, published time
    :return: list of titles
    """
    # Get the stories titles
    titles = []
    for story in _stories:
        titles.append(story['title'])

    return titles


def get_links(_stories):
    """
    function extract links from received stories
    :param _stories: list of stories including story title, link, unique id, published time
    :return: list of links
    """
    # Get the stories titles
    links = []
    for story in _stories:
        links.append(story['link'])

    return links


def get_published_time(_stories):
    """
    function extract published 'timestamps' from received stories
    :param _stories: list of stories including story title, link, unique id, published time
    :return: list of published 'timestamps'
    """
    # Get the stories titles
    published = []
    for story in _stories:
        published.append(story['published'])

    return published


def get_unique_ids(_stories):
    """
    function extract unique ids from received stories
    :param _stories: list of stories including story title, link, unique id, published time
    :return: list of unique ids
    """
    # Get the stories titles
    published = []
    for story in _stories:
        published.append(story['id'])

    return published


def get_titles_links_ahd_published_time_per_crypto(stories_per_crypto):
    """
    function extract titles, links, published 'timestamps' from received stories per crypto coin
    :param stories_per_crypto: list of stories including story title, link, unique id, published time per crypto coin
    :return: lists of titles, links, published 'timestamps'
    """
    titles_per_crypto = []
    links_per_crypto = []
    published_per_crypto = []

    for stories in stories_per_crypto:
        titles_per_crypto.append(get_titles(stories))
        links_per_crypto.append(get_links(stories))
        published_per_crypto.append(get_published_time(stories))

    return titles_per_crypto, links_per_crypto, published_per_crypto
