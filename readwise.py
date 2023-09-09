import requests,sys

class ReadWise:
    def __init__(self, token):
        self.token = token


    def check_token(self):
        r = requests.get(url="https://readwise.io/api/v2/auth/",headers={"Authorization": "Token %s" % self.token})
        if r.status_code != 204:
            sys.exit("[+] Readwise token is outdated. Cannot continue working.")

    def highlight(self, **kwargs):
        # if smth is empty in the telegram post send empty string to Readwise 
        for v in kwargs.values():
            if v is None:
                v = ""
        r = requests.post(url="https://readwise.io/api/v2/highlights/",headers={"Authorization": "Token %s" % self.token},
        json={"highlights": [
                        {
                        "text": kwargs.get("text"),
                        "title": kwargs.get("title"),
                        "source_url": kwargs.get("source_url"),
                        "source_type": "telewise_bot",
                        "note": kwargs.get("note"),
                        "highlighted_at": kwargs.get("highlighted_at")
                        }
        ]}
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

        r = requests.post(
            url="https://readwise.io/api/v3/save/",
            headers={"Authorization": "Token %s" % self.token},
            json=payload
        )

        return r.status_code == 200 or r.status_code == 201
