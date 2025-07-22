#!/usr/bin/env python3
"""
ハーメルンスクレイパー完全テストスイート
リファクタリング前の全機能をテストし、リファクタリング後の動作保証を行う
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


class TestHamelnScraperInitialization(unittest.TestCase):
    """初期化・設定関連のテスト"""
    
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
        
        # 機能フラグの確認
        self.assertTrue(scraper.enable_novel_info_saving)
        self.assertTrue(scraper.enable_comments_saving)
        
        # ログ設定の確認
        self.assertIsNotNone(scraper.logger)
        
    def test_user_agent_rotation(self):
        """User-Agentローテーション機能のテスト"""
        scraper = HamelnFinalScraper()
        
        initial_ua = scraper.user_agents[scraper.current_ua_index]
        scraper.rotate_user_agent()
        rotated_ua = scraper.user_agents[scraper.current_ua_index]
        
        # User-Agentが変更されていることを確認
        self.assertNotEqual(initial_ua, rotated_ua)
        
        # 5回回転させて元に戻ることを確認
        for _ in range(4):
            scraper.rotate_user_agent()
        
        final_ua = scraper.user_agents[scraper.current_ua_index]
        self.assertEqual(initial_ua, final_ua)


class TestHamelnScraperNetworking(unittest.TestCase):
    """ネットワーク・HTTP関連のテスト"""
    
    def setUp(self):
        self.scraper = HamelnFinalScraper()
        
    def test_decompress_response(self):
        """レスポンス解凍機能のテスト"""
        # CloudScraperの自動解凍機能を考慮して、基本的な動作のみテスト
        # 実際のレスポンスオブジェクトの代わりにモックを使用
        test_html = "<html><body>テストコンテンツ</body></html>"
        
        # 通常のレスポンス（圧縮なし）
        mock_response = Mock()
        mock_response.text = test_html
        mock_response.content = test_html.encode('utf-8')
        mock_response.headers = {}
        
        result = self.scraper.decompress_response(mock_response)
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
    
    def test_validate_page(self):
        """ページ検証機能のテスト"""
        # 有効なHTMLページ
        valid_html = """
        <html>
        <head><title>テスト小説</title></head>
        <body>
        <h1>小説タイトル</h1>
        <div class="section1">本文内容</div>
        </body>
        </html>
        """
        valid_soup = BeautifulSoup(valid_html, 'html.parser')
        self.assertTrue(self.scraper.validate_page(valid_soup, "https://syosetu.org/novel/test/"))
        
        # 無効なHTMLページ（タイトルなし）
        invalid_html = "<html><body>内容のみ</body></html>"
        invalid_soup = BeautifulSoup(invalid_html, 'html.parser')
        self.assertFalse(self.scraper.validate_page(invalid_soup, "https://syosetu.org/novel/test/"))


class TestHamelnScraperHTMLParsing(unittest.TestCase):
    """HTML解析・抽出関連のテスト"""
    
    def setUp(self):
        self.scraper = HamelnFinalScraper()
        
    def test_extract_novel_info(self):
        """小説情報抽出のテスト"""
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
        self.assertEqual(info['title'], "テスト小説")
        self.assertEqual(info['author'], "作者名")
        
    def test_extract_chapter_content(self):
        """章内容抽出のテスト"""
        test_html = """
        <html>
        <body>
        <div class="section1">
        <p>第1段落の内容</p>
        <p>第2段落の内容</p>
        </div>
        </body>
        </html>
        """
        soup = BeautifulSoup(test_html, 'html.parser')
        
        content = self.scraper.extract_chapter_content(soup, "https://syosetu.org/novel/test/")
        self.assertIsNotNone(content)
        self.assertIn("第1段落の内容", content)
        self.assertIn("第2段落の内容", content)
        
    def test_get_chapter_links(self):
        """章リンク抽出のテスト"""
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


class TestHamelnScraperResourceManagement(unittest.TestCase):
    """リソース管理関連のテスト"""
    
    def setUp(self):
        self.scraper = HamelnFinalScraper()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
        
    def test_resource_cache_functionality(self):
        """リソースキャッシュ機能のテスト"""
        # 初期状態ではキャッシュは空
        self.assertEqual(len(self.scraper.resource_cache), 0)
        
        # キャッシュ統計の確認
        stats = self.scraper.get_cache_stats()
        self.assertEqual(stats['cached_resources'], 0)
        self.assertEqual(stats['cache_entries'], [])
        
    def test_adjust_resource_paths_only(self):
        """リソースパス調整のテスト"""
        test_html = """
        <html>
        <head>
        <link rel="stylesheet" href="./resources/style.css">
        <script src="./resources/script.js"></script>
        </head>
        <body>
        <img src="./image.png" alt="テスト画像">
        </body>
        </html>
        """
        soup = BeautifulSoup(test_html, 'html.parser')
        
        adjusted_soup = self.scraper.adjust_resource_paths_only(soup, self.temp_dir)
        
        # CSSリンクの確認
        css_link = adjusted_soup.find('link', {'rel': 'stylesheet'})
        self.assertIsNotNone(css_link)
        self.assertTrue(css_link['href'].startswith('./'))
        
        # スクリプトの確認
        script = adjusted_soup.find('script')
        self.assertIsNotNone(script)
        self.assertTrue(script['src'].startswith('./'))
        
        # 画像の確認
        img = adjusted_soup.find('img')
        self.assertIsNotNone(img)
        self.assertTrue(img['src'].startswith('./'))


class TestHamelnScraperFileOperations(unittest.TestCase):
    """ファイル操作関連のテスト"""
    
    def setUp(self):
        self.scraper = HamelnFinalScraper()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
        
    def test_create_complete_html(self):
        """完全HTML作成のテスト"""
        # 章データの作成
        chapters = [
            {'title': '第1章', 'content': '<p>第1章の内容</p>'},
            {'title': '第2章', 'content': '<p>第2章の内容</p>'}
        ]
        
        complete_html = self.scraper.create_complete_html(
            "テスト小説", "作者名", chapters, self.temp_dir
        )
        
        # 完全HTMLの基本構造確認
        self.assertIn('<html', complete_html)
        self.assertIn('</html>', complete_html)
        self.assertIn('テスト小説', complete_html)
        self.assertIn('作者名', complete_html)
        self.assertIn('第1章', complete_html)
        self.assertIn('第2章', complete_html)


class TestHamelnScraperNavigationFixes(unittest.TestCase):
    """ナビゲーションリンク修正関連のテスト"""
    
    def setUp(self):
        self.scraper = HamelnFinalScraper()
        
    def test_fix_local_navigation_links(self):
        """ローカルナビゲーションリンク修正のテスト"""
        test_html = """
        <html>
        <body>
        <div class="novel_bn">
        <a href="/novel/123/1/">前の話</a>
        <a href="/novel/123/index/">目次</a>
        <a href="/novel/123/3/">次の話</a>
        </div>
        </body>
        </html>
        """
        soup = BeautifulSoup(test_html, 'html.parser')
        
        # 章マッピングの作成
        chapter_mapping = {
            "https://syosetu.org/novel/123/1/": "chapter1.html",
            "https://syosetu.org/novel/123/3/": "chapter3.html"
        }
        
        fixed_soup = self.scraper.fix_local_navigation_links(
            soup, chapter_mapping, "index.html", None, None
        )
        
        # リンクが修正されていることを確認
        links = fixed_soup.find_all('a')
        self.assertTrue(any('chapter1.html' in link.get('href', '') for link in links))
        self.assertTrue(any('chapter3.html' in link.get('href', '') for link in links))


class TestHamelnScraperComments(unittest.TestCase):
    """感想処理関連のテスト"""
    
    def setUp(self):
        self.scraper = HamelnFinalScraper()
        
    def test_extract_comments_url(self):
        """感想URL抽出のテスト"""
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
        
    def test_detect_comments_pagination(self):
        """感想ページネーション検出のテスト"""
        test_html = """
        <html>
        <body>
        <div class="pager">
        <a href="?mode=review&page=1">1</a>
        <a href="?mode=review&page=2">2</a>
        <a href="?mode=review&page=3">3</a>
        </div>
        </body>
        </html>
        """
        soup = BeautifulSoup(test_html, 'html.parser')
        
        max_page = self.scraper.detect_comments_pagination(soup, "https://syosetu.org/novel/123/")
        self.assertEqual(max_page, 3)


class TestHamelnScraperIntegration(unittest.TestCase):
    """統合テスト"""
    
    def setUp(self):
        self.scraper = HamelnFinalScraper()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
        
    @patch('hameln_scraper_final.HamelnFinalScraper.get_page')
    def test_scrape_novel_single_page(self, mock_get_page):
        """単一ページ小説のスクレイピングテスト"""
        # モックレスポンスの設定
        test_html = """
        <html>
        <head><title>テスト小説 - 作者名 - ハーメルン</title></head>
        <body>
        <h1>テスト小説</h1>
        <div class="author">作者: 作者名</div>
        <div class="section1">
        <p>これは単一ページ小説のテストです。</p>
        </div>
        </body>
        </html>
        """
        mock_get_page.return_value = BeautifulSoup(test_html, 'html.parser')
        
        # スクレイピング実行（実際のメソッドシグネチャに合わせて修正）
        # scrape_novelメソッドは引数1つのみ
        with patch.object(self.scraper, 'save_novel_with_resources') as mock_save:
            mock_save.return_value = "test_file.html"
            result = self.scraper.scrape_novel("https://syosetu.org/novel/test/")
        
        # 結果の確認
        self.assertIsNotNone(result)


if __name__ == '__main__':
    # テストの実行
    unittest.main(verbosity=2)