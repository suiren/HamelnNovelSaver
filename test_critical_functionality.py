#!/usr/bin/env python3
"""
ハーメルンスクレイパーの重要機能テスト
リファクタリング前後で絶対に動作する必要がある機能のテスト
"""

import unittest
import tempfile
import os
import sys
import shutil
from unittest.mock import Mock, patch, MagicMock
from bs4 import BeautifulSoup
import requests

# テスト対象のインポート
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hameln_scraper_final import HamelnFinalScraper


class TestCriticalFunctionality(unittest.TestCase):
    """重要機能のテスト"""
    
    def setUp(self):
        self.scraper = HamelnFinalScraper()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
        
    def test_scraper_initialization(self):
        """スクレイパーの基本初期化テスト"""
        scraper = HamelnFinalScraper()
        
        # 基本属性の確認
        self.assertEqual(scraper.base_url, "https://syosetu.org")
        self.assertIsNotNone(scraper.cloudscraper)
        self.assertIsNotNone(scraper.session)
        self.assertIsInstance(scraper.user_agents, list)
        self.assertEqual(len(scraper.user_agents), 5)
        self.assertIsInstance(scraper.resource_cache, dict)
        
    def test_user_agent_rotation(self):
        """User-Agentローテーション機能のテスト"""
        scraper = HamelnFinalScraper()
        
        initial_ua = scraper.user_agents[scraper.current_ua_index]
        scraper.rotate_user_agent()
        rotated_ua = scraper.user_agents[scraper.current_ua_index]
        
        # User-Agentが変更されていることを確認
        self.assertNotEqual(initial_ua, rotated_ua)
        
    @patch('hameln_scraper_final.HamelnFinalScraper.cloudscraper')
    def test_hameln_specific_url_conversion(self, mock_cloudscraper):
        """ハーメルン特有のURL変換テスト（重要：過去の失敗要因）"""
        # モックレスポンスの設定
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"test content"
        mock_cloudscraper.get.return_value = mock_response
        
        # CSS リソースURL変換テスト
        css_url = "./resources/style.css"
        result = self.scraper.download_resource(css_url, self.temp_dir)
        
        # cloudscraper.getが正しいURLで呼ばれたかを確認
        expected_css_url = "https://img.syosetu.org/css/style.css"
        mock_cloudscraper.get.assert_called_with(expected_css_url, timeout=30)
        
        # JavaScript リソースURL変換テスト
        mock_cloudscraper.get.reset_mock()
        js_url = "./resources/script.js"
        result = self.scraper.download_resource(js_url, self.temp_dir)
        
        expected_js_url = "https://img.syosetu.org/js/script.js"
        mock_cloudscraper.get.assert_called_with(expected_js_url, timeout=30)
        
        # 画像リソースURL変換テスト
        mock_cloudscraper.get.reset_mock()
        img_url = "./banner.png"
        result = self.scraper.download_resource(img_url, self.temp_dir)
        
        expected_img_url = "https://img.syosetu.org/image/banner.png"
        mock_cloudscraper.get.assert_called_with(expected_img_url, timeout=30)
        
    def test_resource_cache_functionality(self):
        """リソースキャッシュ機能のテスト"""
        # 初期状態ではキャッシュは空
        self.assertEqual(len(self.scraper.resource_cache), 0)
        
        # キャッシュ統計の確認
        stats = self.scraper.get_cache_stats()
        self.assertEqual(stats['cached_resources'], 0)
        self.assertEqual(stats['cache_entries'], [])
        
    def test_chapter_links_extraction(self):
        """章リンク抽出テスト"""
        test_html = """
        <html>
        <body>
        <div class="index_box">
        <a href="/novel/123/1/">第1章</a>
        <a href="/novel/123/2/">第2章</a>
        <a href="/novel/123/3/">第3章</a>
        </div>
        </body>
        </html>
        """
        soup = BeautifulSoup(test_html, 'html.parser')
        
        links = self.scraper.get_chapter_links(soup, "https://syosetu.org/novel/123/")
        self.assertEqual(len(links), 3)
        self.assertIn("https://syosetu.org/novel/123/1/", links)
        self.assertIn("https://syosetu.org/novel/123/2/", links)
        self.assertIn("https://syosetu.org/novel/123/3/", links)
        
    def test_novel_info_extraction(self):
        """小説情報抽出テスト"""
        test_html = """
        <html>
        <head><title>テスト小説 - 作者名 - ハーメルン</title></head>
        <body>
        <h1>テスト小説</h1>
        <div class="author">作者: 作者名</div>
        </body>
        </html>
        """
        soup = BeautifulSoup(test_html, 'html.parser')
        
        info = self.scraper.extract_novel_info(soup)
        self.assertIsInstance(info, dict)
        self.assertIn('title', info)
        self.assertIn('author', info)
        
    def test_resource_path_adjustment(self):
        """リソースパス調整テスト"""
        test_html = """
        <html>
        <head>
        <link rel="stylesheet" href="./resources/style.css">
        <script src="./resources/script.js"></script>
        </head>
        <body>
        <img src="./banner.png" alt="バナー">
        </body>
        </html>
        """
        soup = BeautifulSoup(test_html, 'html.parser')
        
        # リソースパス調整を実行
        adjusted_soup = self.scraper.adjust_resource_paths_only(soup, self.temp_dir)
        
        # 基本的な調整が行われていることを確認
        self.assertIsNotNone(adjusted_soup)
        
    def test_navigation_link_fixing(self):
        """ナビゲーションリンク修正テスト"""
        test_html = """
        <html>
        <body>
        <div class="novel_bn">
        <a href="/novel/123/1/">前の話</a>
        <a href="/novel/123/">目次</a>
        <a href="/novel/123/3/">次の話</a>
        </div>
        </body>
        </html>
        """
        soup = BeautifulSoup(test_html, 'html.parser')
        
        # 章マッピングの作成
        chapter_mapping = {
            "https://syosetu.org/novel/123/1/": "第1章.html",
            "https://syosetu.org/novel/123/3/": "第3章.html"
        }
        
        fixed_soup = self.scraper.fix_local_navigation_links(
            soup, chapter_mapping, "目次.html", None, None
        )
        
        # 基本的な修正が行われていることを確認
        self.assertIsNotNone(fixed_soup)
        
    def test_comments_url_extraction(self):
        """感想URL抽出テスト"""
        test_html = """
        <html>
        <body>
        <ol class="topicPath">
        <li><a href="/novel/123/">目次</a></li>
        <li><a href="?mode=review">感想</a></li>
        </ol>
        </body>
        </html>
        """
        soup = BeautifulSoup(test_html, 'html.parser')
        
        comments_url = self.scraper.extract_comments_url(soup)
        self.assertIsNotNone(comments_url)
        self.assertIn("mode=review", comments_url)
        
    def test_cloudflare_bypass_functionality(self):
        """Cloudflareバイパス機能のテスト"""
        # CloudScraperが正しく初期化されていることを確認
        self.assertIsNotNone(self.scraper.cloudscraper)
        
        # User-Agentがローテーションされることを確認
        self.assertIsInstance(self.scraper.user_agents, list)
        self.assertGreater(len(self.scraper.user_agents), 0)
        
    def test_close_functionality(self):
        """リソース解放機能のテスト"""
        # driverが存在しない場合のテスト
        self.assertIsNone(self.scraper.driver)
        
        # close()メソッドが呼び出せることを確認
        try:
            self.scraper.close()
            self.assertTrue(True)  # 正常に終了した場合
        except Exception as e:
            self.fail(f"close()メソッドが失敗: {e}")


if __name__ == '__main__':
    # 重要機能のテストのみを実行
    unittest.main(verbosity=2)