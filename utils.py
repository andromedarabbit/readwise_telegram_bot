import logging
import re
import urllib

import tldextract
from urlextract import URLExtract

_logger = logging.getLogger()
_extractor = URLExtract()


def _find_js_redirect(r):
    try:
        content = r.read().decode()

        match = re.search(r'''^\s*window.location.href\s*=\s*["'](http[s*]://.*)["'].*;''', content,
                          re.IGNORECASE | re.MULTILINE)
        if match and match.regs and len(match.regs) > 0:
            return match.group(1)

        return None
    except BaseException as err:
        _logger.warning(err)
        return None


async def _parse_url(url):
    text = "http://" + url if "://" not in url else url

    try:
        req = urllib.request.Request(text)
        req.add_header('User-Agent',
                       'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:90.0) Gecko/20100101 Firefox/90.0')
        r = urllib.request.urlopen(req, timeout=5)

        js_redirect = _find_js_redirect(r)
        if js_redirect:
            return js_redirect

        return r.url
    except BaseException as err:
        _logger.warning(err)
        return text


async def parse_urls(text):
    try:
        urls = _extractor.find_urls(text)
    except (TypeError, AttributeError) as err:
        _logger.warning(err)
        return []

    if not urls or len(urls) == 0:
        return []

    return list(set(urls))


def _is_unsupported(url: str):
    urls_unsupported = [
        'truefriend.com',
        'github.com/unchartedsky/pdfthis',
        'samsungpop.com/streamdocs',
    ]

    for url_unsupported in urls_unsupported:
        if url_unsupported in url:
            return True

    return False


async def filter_valid_urls(urls: list[str]):
    allowed = []
    for url in urls:
        link = await _parse_url(url)
        if not link:
            continue

        url = "http://" + url if "://" not in link else link

        if _is_unsupported(url):
            continue

        url.replace('://blog.naver.com', '://m.blog.naver.com')
        url.replace('://cafe.naver.com', '://m.cafe.naver.com')
        url.replace('://post.naver.com', '://m.post.naver.com')

        r = tldextract.extract(url)
        if not r:
            continue
        if not r.registered_domain:
            continue
        # if r.registered_domain.casefold() == "t.me".casefold():
        #     continue

        allowed.append(url)

    return list(set(allowed))


def is_empty_text(text: str, urls: list[str]):
    for url in urls:
        text = text.replace(url, '')
    text = text.strip()
    return len(text) == 0
