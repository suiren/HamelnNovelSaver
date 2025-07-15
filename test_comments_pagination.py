#!/usr/bin/env python3
"""
感想ページの複数ページ取得機能のテストケース
TDD手順に従って、実装前にテストを作成
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from bs4 import BeautifulSoup
import sys
import os

# テスト対象のモジュールをインポート
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from hameln_scraper_final import HamelnFinalScraper

class TestCommentsPagination(unittest.TestCase):
    """感想ページの複数ページ取得機能のテストクラス"""
    
    def setUp(self):
        """テストの準備"""
        self.scraper = HamelnFinalScraper()
        self.test_base_url = "https://syosetu.org/novel/123456/?mode=review"
        
    def test_detect_comments_pagination_single_page(self):
        """単一ページの感想ページのテスト"""
        # モックHTMLを作成（ページネーションなし）
        html_content = """
        <html>
        <body>
            <div class="review-item">感想1</div>
            <div class="review-item">感想2</div>
        </body>
        </html>
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 期待値: 1ページのみ
        result = self.scraper.detect_comments_pagination(soup, self.test_base_url)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.test_base_url)
        
    def test_detect_comments_pagination_multiple_pages(self):
        """複数ページの感想ページのテスト"""
        # モックHTMLを作成（ページネーションあり）
        html_content = """
        <html>
        <body>
            <div class="review-item">感想1</div>
            <div class="pagination">
                <a href="?mode=review&page=1">1</a>
                <a href="?mode=review&page=2">2</a>
                <a href="?mode=review&page=3">3</a>
            </div>
        </body>
        </html>
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 期待値: 3ページ
        result = self.scraper.detect_comments_pagination(soup, self.test_base_url)
        
        self.assertEqual(len(result), 3)
        # ページ番号ベースで検証
        page_numbers = [self.scraper.extract_page_number(url) for url in result]
        self.assertIn(1, page_numbers)
        self.assertIn(2, page_numbers)
        self.assertIn(3, page_numbers)
        
    def test_detect_comments_pagination_hameln_specific_pattern(self):
        """ハーメルン特有のページネーションパターンのテスト"""
        # ハーメルンのページネーションパターンを模擬
        html_content = """
        <html>
        <body>
            <div class="review-item">感想1</div>
            <div class="page-nav">
                <a href="/novel/123456/?mode=review&page=1">1</a>
                <a href="/novel/123456/?mode=review&page=2">2</a>
                <a href="/novel/123456/?mode=review&page=3">3</a>
                <a href="/novel/123456/?mode=review&page=4">4</a>
                <a href="/novel/123456/?mode=review&page=5">5</a>
            </div>
        </body>
        </html>
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 期待値: 5ページ
        result = self.scraper.detect_comments_pagination(soup, self.test_base_url)
        
        self.assertEqual(len(result), 5)
        # ページ番号ベースで検証
        page_numbers = [self.scraper.extract_page_number(url) for url in result]
        self.assertIn(1, page_numbers)
        self.assertIn(2, page_numbers)
        self.assertIn(3, page_numbers)
        self.assertIn(4, page_numbers)
        self.assertIn(5, page_numbers)
        
    @patch('hameln_scraper_final.HamelnFinalScraper.get_page')
    def test_get_all_comments_pages_multiple_pages(self, mock_get_page):
        """複数ページの感想取得統合テスト"""
        # 1ページ目のモックレスポンス
        page1_html = """
        <html>
        <body>
            <div class="review-item">感想1</div>
            <div class="review-item">感想2</div>
            <div class="pagination">
                <a href="?mode=review&page=1">1</a>
                <a href="?mode=review&page=2">2</a>
            </div>
        </body>
        </html>
        """
        page1_soup = BeautifulSoup(page1_html, 'html.parser')
        
        # 2ページ目のモックレスポンス
        page2_html = """
        <html>
        <body>
            <div class="review-item">感想3</div>
            <div class="review-item">感想4</div>
            <div class="pagination">
                <a href="?mode=review&page=1">1</a>
                <a href="?mode=review&page=2">2</a>
            </div>
        </body>
        </html>
        """
        page2_soup = BeautifulSoup(page2_html, 'html.parser')
        
        # モックの設定
        mock_get_page.side_effect = [page1_soup, page2_soup]
        
        # テスト実行
        result = self.scraper.get_all_comments_pages(self.test_base_url)
        
        # 結果検証
        self.assertIsNotNone(result)
        # 統合されたページには両方のページの感想が含まれる
        integrated_text = str(result)
        self.assertIn("感想1", integrated_text)
        self.assertIn("感想2", integrated_text)
        self.assertIn("感想3", integrated_text)
        self.assertIn("感想4", integrated_text)
        
    def test_extract_page_number(self):
        """ページ番号抽出のテスト"""
        # 正常なURLからページ番号を抽出
        url1 = "https://syosetu.org/novel/123456/?mode=review&page=3"
        result1 = self.scraper.extract_page_number(url1)
        self.assertEqual(result1, 3)
        
        # ページ番号がないURLの場合
        url2 = "https://syosetu.org/novel/123456/?mode=review"
        result2 = self.scraper.extract_page_number(url2)
        self.assertEqual(result2, 1)
        
        # 無効なURLの場合
        url3 = "invalid-url"
        result3 = self.scraper.extract_page_number(url3)
        self.assertEqual(result3, 1)
        
    def test_extract_comments_content(self):
        """感想コンテンツ抽出のテスト"""
        # 感想コンテンツを含むHTML
        html_content = """
        <html>
        <body>
            <div class="review-item">とても面白い作品でした</div>
            <div class="review-item">続きが気になります</div>
            <div class="other-content">関係ない内容</div>
        </body>
        </html>
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # テスト実行
        result = self.scraper.extract_comments_content(soup)
        
        # 結果検証
        self.assertEqual(len(result), 2)
        self.assertIn("とても面白い作品でした", str(result[0]))
        self.assertIn("続きが気になります", str(result[1]))

if __name__ == '__main__':
    print("感想ページ複数ページ取得機能のテストを実行中...")
    unittest.main(verbosity=2)