import unittest
import utils
from telegram import *


class UtilsTests(unittest.IsolatedAsyncioTestCase):
    async def test_is_empty_text_with_url_only(self):
        text = 'https://youtu.be/x2wDVnwNkYQ?si=K7JpFGTx1nZJNfx9'
        e = MessageEntity(length=48, offset=0, type='URL')
        urls = await utils.parse_urls(text)
        self.assertTrue(await utils.is_empty_text(text, urls, [e]))


class ExtractUrlMetadataTests(unittest.TestCase):
    """Test cases for extract_url_metadata() function."""

    def test_naver_blog_korean_content(self):
        """Test extraction from Naver blog with Korean content."""
        url = 'https://m.blog.naver.com/68083015/223213136444'
        metadata = utils.extract_url_metadata(url)

        # Should extract title from either OG or <title>
        title = metadata["og_title"] or metadata["title"]
        self.assertTrue('ESS 이야기 4편' in title)
        self.assertIn('all_metadata', metadata)

    def test_news_hada_io_problematic_url(self):
        """Test extraction from news.hada.io (the original timeout issue)."""
        url = 'https://news.hada.io/topic?id=26155'
        metadata = utils.extract_url_metadata(url)

        # Should successfully extract title without timeout
        title = metadata["og_title"] or metadata["title"]
        self.assertIsNotNone(title)
        self.assertNotEqual(title, "")

    def test_youtube_url(self):
        """Test extraction from YouTube URL."""
        url = 'https://youtu.be/x2wDVnwNkYQ?si=K7JpFGTx1nZJNfx9'
        metadata = utils.extract_url_metadata(url)

        # YouTube has good OG metadata
        title = metadata["og_title"] or metadata["title"]
        self.assertIsNotNone(title)
        self.assertNotEqual(title, "")

    def test_github_url(self):
        """Test extraction from GitHub (has good metadata)."""
        url = 'https://github.com/scrapinghub/extruct'
        metadata = utils.extract_url_metadata(url)

        # GitHub has both OG and JSON-LD
        title = metadata["og_title"] or metadata["title"]
        self.assertIn('extruct', title.lower())
        self.assertIsNotNone(metadata["all_metadata"])

    def test_invalid_url_returns_empty_metadata(self):
        """Test that invalid/unreachable URLs return empty metadata gracefully."""
        url = 'https://this-domain-definitely-does-not-exist-12345.com'
        metadata = utils.extract_url_metadata(url)

        # Should return empty dict on error
        self.assertEqual(metadata["title"], "")
        self.assertEqual(metadata["og_title"], "")
        self.assertEqual(metadata["description"], "")
        self.assertEqual(metadata["image"], "")

    def test_metadata_structure(self):
        """Test that metadata dict has all required keys."""
        url = 'https://github.com/scrapinghub/extruct'
        metadata = utils.extract_url_metadata(url)

        # Check all required keys exist
        required_keys = ["title", "og_title", "description", "image", "all_metadata"]
        for key in required_keys:
            self.assertIn(key, metadata)

    def test_timeout_parameter(self):
        """Test that timeout parameter is respected (short timeout)."""
        url = 'https://httpbin.org/delay/10'  # This endpoint delays 10 seconds
        metadata = utils.extract_url_metadata(url, timeout=2)  # 2 second timeout

        # Should return empty metadata due to timeout
        self.assertEqual(metadata["title"], "")

    def test_http_error_handling(self):
        """Test that HTTP errors are handled gracefully."""
        url = 'https://httpbin.org/status/404'
        metadata = utils.extract_url_metadata(url)

        # Should return empty metadata on 404
        self.assertEqual(metadata["title"], "")

    def test_all_metadata_contains_extruct_output(self):
        """Test that all_metadata contains the raw extruct output."""
        url = 'https://github.com/scrapinghub/extruct'
        metadata = utils.extract_url_metadata(url)

        # all_metadata should contain extruct's output
        self.assertIsInstance(metadata["all_metadata"], dict)
        # extruct returns dict with keys like 'opengraph', 'json-ld', etc.
        self.assertTrue(len(metadata["all_metadata"]) > 0 or metadata["title"] != "")


if __name__ == '__main__':
    unittest.main()


if __name__ == '__main__':
    unittest.main()
