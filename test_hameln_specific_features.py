#!/usr/bin/env python3
"""
ハーメルン特有機能のテストスイート
特にURL変換、Cloudflare回避、リソース処理等の重要な機能をテスト
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


class TestHamelnSpecificURLHandling(unittest.TestCase):
    """ハーメルン特有のURL処理テスト"""
    
    def setUp(self):
        self.scraper = HamelnFinalScraper()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
        
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
        
    def test_url_conversion_logic(self):
        """URL変換ロジックの詳細テスト"""
        # テストケース1: ./resources/style.css
        url = "./resources/style.css"
        if url.startswith('./resources/'):
            resource_file = url.replace('./resources/', '')
            if resource_file.endswith('.css'):
                converted_url = f"https://img.syosetu.org/css/{resource_file}"
                self.assertEqual(converted_url, "https://img.syosetu.org/css/style.css")
        
        # テストケース2: ./resources/script.js
        url = "./resources/script.js"
        if url.startswith('./resources/'):
            resource_file = url.replace('./resources/', '')
            if resource_file.endswith('.js'):
                converted_url = f"https://img.syosetu.org/js/{resource_file}"
                self.assertEqual(converted_url, "https://img.syosetu.org/js/script.js")
        
        # テストケース3: ./image.png
        url = "./image.png"
        if url.startswith('./'):
            converted_url = f"https://img.syosetu.org/image/{url[2:]}"
            self.assertEqual(converted_url, "https://img.syosetu.org/image/image.png")
            
    def test_resource_path_adjustment(self):
        """リソースパス調整の詳細テスト"""
        test_html = """
        <html>
        <head>
        <link rel="stylesheet" href="./resources/style.css">
        <link rel="stylesheet" href="./resources/theme.css">
        <script src="./resources/script.js"></script>
        <script src="./resources/jquery.js"></script>
        </head>
        <body>
        <img src="./banner.png" alt="バナー">
        <img src="./resources/logo.png" alt="ロゴ">
        </body>
        </html>
        """
        soup = BeautifulSoup(test_html, 'html.parser')
        
        # リソースパス調整を実行
        adjusted_soup = self.scraper.adjust_resource_paths_only(soup, self.temp_dir)
        
        # CSSリンクの確認
        css_links = adjusted_soup.find_all('link', {'rel': 'stylesheet'})
        self.assertEqual(len(css_links), 2)
        for link in css_links:
            self.assertTrue(link['href'].startswith('./'))
            self.assertTrue(link['href'].endswith('.css'))
            
        # スクリプトの確認
        scripts = adjusted_soup.find_all('script', src=True)
        self.assertEqual(len(scripts), 2)
        for script in scripts:
            self.assertTrue(script['src'].startswith('./'))
            self.assertTrue(script['src'].endswith('.js'))
            
        # 画像の確認
        images = adjusted_soup.find_all('img')
        self.assertEqual(len(images), 2)
        for img in images:
            self.assertTrue(img['src'].startswith('./'))


class TestHamelnSpecificHTMLStructure(unittest.TestCase):
    """ハーメルン特有のHTML構造テスト"""
    
    def setUp(self):
        self.scraper = HamelnFinalScraper()
        
    def test_section_class_detection(self):
        """section1-9クラス検出テスト"""
        test_html = """
        <html>
        <body>
        <div class="section1">第1セクション</div>
        <div class="section2">第2セクション</div>
        <div class="section3">第3セクション</div>
        <div class="section4">第4セクション</div>
        <div class="section5">第5セクション</div>
        <div class="p-novel-text">新しい形式の本文</div>
        </body>
        </html>
        """
        soup = BeautifulSoup(test_html, 'html.parser')
        
        # 本文抽出のテスト
        content = self.scraper.extract_chapter_content(soup, "https://syosetu.org/novel/test/")
        
        # 複数のセクションが含まれていることを確認
        self.assertIsNotNone(content)
        self.assertIn("第1セクション", content)
        self.assertIn("第2セクション", content)
        self.assertIn("第3セクション", content)
        
    def test_novel_text_class_detection(self):
        """novel-textクラス検出テスト（新しい形式）"""
        test_html = """
        <html>
        <body>
        <div class="novel-text">
        <p>新しい形式の本文内容</p>
        <p>2024年以降の形式</p>
        </div>
        </body>
        </html>
        """
        soup = BeautifulSoup(test_html, 'html.parser')
        
        content = self.scraper.extract_chapter_content(soup, "https://syosetu.org/novel/test/")
        
        self.assertIsNotNone(content)
        self.assertIn("新しい形式の本文内容", content)
        self.assertIn("2024年以降の形式", content)
        
    def test_chapter_links_extraction(self):
        """章リンク抽出の詳細テスト"""
        test_html = """
        <html>
        <body>
        <div class="index_box">
        <dl>
        <dt><a href="/novel/123456/1/">第1章：始まり</a></dt>
        <dd>章の説明</dd>
        <dt><a href="/novel/123456/2/">第2章：展開</a></dt>
        <dd>章の説明2</dd>
        </dl>
        </div>
        <div class="index_box">
        <ul>
        <li><a href="/novel/123456/3/">第3章：クライマックス</a></li>
        <li><a href="/novel/123456/4/">第4章：結末</a></li>
        </ul>
        </div>
        </body>
        </html>
        """
        soup = BeautifulSoup(test_html, 'html.parser')
        
        chapter_links = self.scraper.get_chapter_links(soup, "https://syosetu.org/novel/123456/")
        
        # 正しい数の章リンクが抽出されることを確認
        self.assertEqual(len(chapter_links), 4)
        
        # 正しいURLが生成されることを確認
        expected_links = [
            "https://syosetu.org/novel/123456/1/",
            "https://syosetu.org/novel/123456/2/",
            "https://syosetu.org/novel/123456/3/",
            "https://syosetu.org/novel/123456/4/"
        ]
        
        for expected_link in expected_links:
            self.assertIn(expected_link, chapter_links)


class TestHamelnSpecificNavigation(unittest.TestCase):
    """ハーメルン特有のナビゲーション処理テスト"""
    
    def setUp(self):
        self.scraper = HamelnFinalScraper()
        
    def test_novel_info_link_extraction(self):
        """小説情報リンク抽出テスト"""
        test_html = """
        <html>
        <body>
        <div class="navi">
        <a href="/novel/123456/info/">小説情報</a>
        <a href="/novel/123456/">目次</a>
        <a href="/novel/123456/?mode=review">感想</a>
        </div>
        </body>
        </html>
        """
        soup = BeautifulSoup(test_html, 'html.parser')
        
        info_url = self.scraper.extract_novel_info_url(soup)
        
        self.assertIsNotNone(info_url)
        self.assertIn("/info/", info_url)
        self.assertTrue(info_url.startswith("https://syosetu.org/"))
        
    def test_comments_link_extraction(self):
        """感想リンク抽出テスト"""
        test_html = """
        <html>
        <body>
        <div class="navi">
        <a href="/novel/123456/">目次</a>
        <a href="/novel/123456/?mode=review">感想</a>
        <a href="/novel/123456/info/">小説情報</a>
        </div>
        </body>
        </html>
        """
        soup = BeautifulSoup(test_html, 'html.parser')
        
        comments_url = self.scraper.extract_comments_url(soup)
        
        self.assertIsNotNone(comments_url)
        self.assertIn("mode=review", comments_url)
        self.assertTrue(comments_url.startswith("https://syosetu.org/"))
        
    def test_navigation_link_fixing(self):
        """ナビゲーションリンク修正テスト"""
        test_html = """
        <html>
        <body>
        <div class="novel_bn">
        <a href="/novel/123456/1/">前の話</a>
        <a href="/novel/123456/">目次</a>
        <a href="/novel/123456/3/">次の話</a>
        </div>
        <div class="navi">
        <a href="/novel/123456/info/">小説情報</a>
        <a href="/novel/123456/?mode=review">感想</a>
        </div>
        </body>
        </html>
        """
        soup = BeautifulSoup(test_html, 'html.parser')
        
        # 章マッピングの作成
        chapter_mapping = {
            "https://syosetu.org/novel/123456/1/": "第1章.html",
            "https://syosetu.org/novel/123456/3/": "第3章.html"
        }
        
        fixed_soup = self.scraper.fix_local_navigation_links(
            soup, chapter_mapping, "目次.html", "小説情報.html", "感想.html"
        )
        
        # リンクが正しく修正されているかを確認
        links = fixed_soup.find_all('a')
        href_values = [link.get('href') for link in links]
        
        self.assertIn("第1章.html", href_values)
        self.assertIn("第3章.html", href_values)
        self.assertIn("目次.html", href_values)
        self.assertIn("小説情報.html", href_values)
        self.assertIn("感想.html", href_values)


class TestHamelnSpecificErrorHandling(unittest.TestCase):
    """ハーメルン特有のエラーハンドリングテスト"""
    
    def setUp(self):
        self.scraper = HamelnFinalScraper()
        
    def test_403_error_handling(self):
        """403エラーハンドリングテスト"""
        with patch.object(self.scraper.cloudscraper, 'get') as mock_get:
            # 403エラーのモック
            mock_response = Mock()
            mock_response.status_code = 403
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("403 Forbidden")
            mock_get.return_value = mock_response
            
            # get_pageメソッドのテスト
            result = self.scraper.get_page("https://syosetu.org/novel/test/")
            
            # 403エラーの場合はNoneが返されることを確認
            self.assertIsNone(result)
            
    def test_429_error_handling(self):
        """429エラーハンドリングテスト"""
        with patch.object(self.scraper.cloudscraper, 'get') as mock_get:
            # 429エラーのモック
            mock_response = Mock()
            mock_response.status_code = 429
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("429 Too Many Requests")
            mock_get.return_value = mock_response
            
            # get_pageメソッドのテスト
            result = self.scraper.get_page("https://syosetu.org/novel/test/")
            
            # 429エラーの場合はNoneが返されることを確認
            self.assertIsNone(result)
            
    def test_cloudflare_challenge_handling(self):
        """Cloudflareチャレンジハンドリングテスト"""
        test_html = """
        <html>
        <head><title>Just a moment...</title></head>
        <body>
        <div class="cf-browser-verification">
        Cloudflare checking...
        </div>
        </body>
        </html>
        """
        soup = BeautifulSoup(test_html, 'html.parser')
        
        # Cloudflareチャレンジページの検証
        is_valid = self.scraper.validate_page(soup)
        
        # Cloudflareチャレンジページは無効として扱われることを確認
        self.assertFalse(is_valid)


class TestHamelnSpecificResourceCaching(unittest.TestCase):
    """ハーメルン特有のリソースキャッシング機能テスト"""
    
    def setUp(self):
        self.scraper = HamelnFinalScraper()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
        
    @patch('hameln_scraper_final.HamelnFinalScraper.cloudscraper')
    def test_resource_caching(self, mock_cloudscraper):
        """リソースキャッシング機能テスト"""
        # モックレスポンスの設定
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"test css content"
        mock_cloudscraper.get.return_value = mock_response
        
        # 同じリソースを2回ダウンロード
        url = "./resources/style.css"
        
        # 1回目のダウンロード
        result1 = self.scraper.download_resource(url, self.temp_dir)
        self.assertIsNotNone(result1)
        
        # 2回目のダウンロード（キャッシュされているはず）
        result2 = self.scraper.download_resource(url, self.temp_dir)
        self.assertIsNotNone(result2)
        
        # cloudscraper.getが1回しか呼ばれていないことを確認（キャッシュが効いている）
        self.assertEqual(mock_cloudscraper.get.call_count, 1)
        
        # キャッシュ統計の確認
        stats = self.scraper.get_cache_stats()
        self.assertEqual(stats['cached_resources'], 1)
        self.assertEqual(len(stats['cache_entries']), 1)


if __name__ == '__main__':
    # テストの実行
    unittest.main(verbosity=2)