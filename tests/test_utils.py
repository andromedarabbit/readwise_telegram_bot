import unittest
import utils


class UtilsTests(unittest.IsolatedAsyncioTestCase):
    async def test_something(self):
        text = 'https://youtu.be/x2wDVnwNkYQ?si=K7JpFGTx1nZJNfx9'
        urls = await utils.parse_urls(text)
        self.assertTrue(utils.is_empty_text(text, urls))


if __name__ == '__main__':
    unittest.main()
