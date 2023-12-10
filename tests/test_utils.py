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

    async def test_title(self):
        url = 'https://m.blog.naver.com/68083015/223213136444'

        reader = URLTitleReader(verify_ssl=True)
        title = reader.title(url)
        self.assertTrue('ESS 이야기 4편' in title)


if __name__ == '__main__':
    unittest.main()
