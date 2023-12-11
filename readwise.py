import requests, sys
import datetime
import logging

_logger = logging.getLogger()


class ReadWise:
    def __init__(self, token):
        self.token = token

    def check_token(self):
        r = requests.get(url="https://readwise.io/api/v2/auth/", headers={"Authorization": "Token %s" % self.token})
        if r.status_code != 204:
            sys.exit("[+] Readwise token is outdated. Cannot continue working.")

    def highlight(self, **kwargs):
        # if smth is empty in the telegram post send empty string to Readwise 
        for v in kwargs.values():
            if v is None:
                v = ""
        r = requests.post(url="https://readwise.io/api/v2/highlights/",headers={"Authorization": "Token %s" % self.token},
        json={"highlights": [{
                "text": kwargs.get("text"),
                "title": kwargs.get("title"),
                "source_url": kwargs.get("source_url"),
                "source_type": "telewise_bot",
                "note": kwargs.get("note"),
                "highlighted_at": kwargs.get("highlighted_at")
            }] }
        )

    def save(self, **kwargs):
        # if smth is empty in the telegram post send empty string to Readwise 
        for v in kwargs.values():
            if v is None:
                v = ""

        payload = {
            "url": kwargs.get("url"),
            "html": kwargs.get("html"),
            "title": kwargs.get("title"),
            "summary": kwargs.get("summary"),
            "should_clean_html": True,
            "tags": kwargs.get("tags"),
        }

        published_date = kwargs.get('published_date')
        if published_date:
            payload['published_date'] = published_date.isoformat() if isinstance(published_date, datetime.datetime) else published_date

        author = kwargs.get('author')
        if author:
            payload['author'] = author

        r = requests.post(
            url="https://readwise.io/api/v3/save/",
            headers={"Authorization": "Token %s" % self.token},
            json=payload
        )

        if r.status_code != 200 and r.status_code != 201:
            _logger.warning(r.text)
            _logger.debug(kwargs)
            return ''

        data = r.json()
        if not data:
            return ''
        return data.get('url')
