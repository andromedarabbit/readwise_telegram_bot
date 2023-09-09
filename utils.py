import logging
import re
import urllib

import tldextract
from urlextract import URLExtract
import textdistance as td
from urltitle import URLTitleReader
from telegram import *
from cleantext import clean

_logger = logging.getLogger()
_extractor = URLExtract()
_reader = URLTitleReader(verify_ssl=True)


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


async def is_empty_text(text: str, urls: list[str], entities: tuple[MessageEntity]):
    for e in reversed(entities):
        text = text[:e.offset] + text[(e.offset + e.length + 1):]

    text = clean(text, to_ascii=False, no_emoji=True, no_line_breaks=True, no_punct=True, no_currency_symbols=True)
    if len(text) == 0:
        return True

    for url in urls:
        title = _reader.title(await _parse_url(url))
        title = clean(title, to_ascii=False, no_emoji=True, no_line_breaks=True, no_punct=True, no_currency_symbols=True)
        if not title:
            continue

        # NOTE 더 좋은 방법을 나중에 찾자
        if len(text) < len(title):
            title = title[:len(text)]
        else:
            text = text[:len(title)]

        similarity = td.levenshtein.normalized_similarity(text, title)
        if similarity > 0.75:
            return True

    return False


def get_tags(msg: Message):
    tags = msg.parse_entities([MessageEntity.HASHTAG])
    if not tags:
        tags = msg.parse_caption_entities([MessageEntity.HASHTAG])

    if not tags:
        return []

    return [tag.replace('#', '') for tag in tags.values()]

