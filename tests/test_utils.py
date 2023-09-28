import unittest
import utils
from telegram import *
from urltitle import URLTitleReader


class UtilsTests(unittest.IsolatedAsyncioTestCase):
    async def test_is_empty_text_with_url_only(self):
        text = 'https://youtu.be/x2wDVnwNkYQ?si=K7JpFGTx1nZJNfx9'
        e = MessageEntity(length=48, offset=0, type='URL')
        urls = await utils.parse_urls(text)
        self.assertTrue(await utils.is_empty_text(text, urls, [e]))

    async def test_is_empty_text_with_webpage_title_only(self):
        text = '애플 시가총액 이틀 만에 무려 260조원 증발한 이유는   https://naver.me/FvFYjl1g'
        e = MessageEntity(length=25, offset=33, type='URL')
        urls = await utils.parse_urls(text)
        self.assertTrue(await utils.is_empty_text(text, urls, [e]))

    async def test_is_empty_text_with_webpage_title_only_2(self):
        text = """▶️ '휴짓조각'된 SK리츠 워런트, 정체성 파괴ㆍ끝없는 증자에 쌓이는 피로감
https://bit.ly/44D7zB2
#리츠, #SK리츠"""
        entities = (
            MessageEntity(length=22, offset=44, type='URL'),
            MessageEntity(length=3, offset=67, type='HASHTAG'),
            MessageEntity(length=5, offset=72, type='HASHTAG'),
        )
        urls = await utils.parse_urls(text)
        self.assertTrue(await utils.is_empty_text(text, urls, entities))

    async def test_is_empty_text_with_webpage_title_only_3(self):
        text = """ESS 이야기 4편

https://blog.naver.com/68083015/223213136444"""
        entities = (
            MessageEntity(length=44, offset=12, type='URL'),
        )
        urls = await utils.parse_urls(text)
        urls = await utils.filter_valid_urls(urls)
        self.assertTrue(await utils.is_empty_text(text, urls, entities))

    async def test_title(self):
        url = 'https://m.blog.naver.com/68083015/223213136444'

        reader = URLTitleReader(verify_ssl=True)
        title = reader.title(url)
        self.assertTrue('ESS 이야기 4편' in title)


if __name__ == '__main__':
    unittest.main()
