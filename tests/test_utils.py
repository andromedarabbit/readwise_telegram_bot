import unittest
import utils


class UtilsTests(unittest.IsolatedAsyncioTestCase):
    async def test_is_empty_text_with_url_only(self):
        text = 'https://youtu.be/x2wDVnwNkYQ?si=K7JpFGTx1nZJNfx9'
        urls = await utils.parse_urls(text)
        self.assertTrue(await utils.is_empty_text(text, urls))

    async def test_is_empty_text_with_webpage_title_only(self):
        text = '애플 시가총액 이틀 만에 무려 260조원 증발한 이유는   https://naver.me/FvFYjl1g'
        urls = await utils.parse_urls(text)
        self.assertTrue(await utils.is_empty_text(text, urls))


if __name__ == '__main__':
    unittest.main()
