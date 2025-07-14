#!/usr/bin/env python3
"""
小説情報・感想保存機能のテストケース
CLAUDE.mdのTDD手順に従って作成

新機能: 小説情報ページと感想ページも自動保存する機能
"""

import unittest
import tempfile
import os
import shutil
from unittest.mock import Mock, patch, MagicMock
from bs4 import BeautifulSoup

# テスト対象のインポート
import sys
sys.path.append('.')
from hameln_scraper_final import HamelnFinalScraper

class TestNovelInfoCommentsFeature(unittest.TestCase):
    
    def setUp(self):
        """テスト前準備"""
        self.scraper = HamelnFinalScraper()
        self.temp_dir = tempfile.mkdtemp()
        
        # テスト用のURL
        self.novel_id = "378070"
        self.base_url = f"https://syosetu.org/novel/{self.novel_id}/"
        self.info_url = f"https://syosetu.org/?mode=ss_detail&nid={self.novel_id}"
        self.comments_url = f"https://syosetu.org/?mode=review&nid={self.novel_id}"
        
    def tearDown(self):
        """テスト後クリーンアップ"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_should_extract_novel_info_url_from_index_page(self):
        """
        目次ページから小説情報ページのURLを正しく抽出できるべき
        
        現在の実装では実行されない機能（このテストは失敗するはず）
        """
        # 目次ページのサンプルHTML（topicPathに小説情報リンクを含む）
        index_html = f'''
        <ol class="topicPath">
            <li><a href="{self.base_url}">目次</a></li>
            <li><a href="{self.info_url}">小説情報</a></li>
            <li><a href="{self.comments_url}">感想</a></li>
        </ol>
        '''
        
        soup = BeautifulSoup(index_html, 'html.parser')
        
        # 新機能: 小説情報URLを抽出（まだ実装されていない）
        extracted_info_url = self.scraper.extract_novel_info_url(soup)
        
        # 期待値との比較（このテストは現在失敗するはず）
        self.assertEqual(extracted_info_url, self.info_url,
                        "小説情報URLが正しく抽出されるべき")

    def test_should_extract_comments_url_from_index_page(self):
        """
        目次ページから感想ページのURLを正しく抽出できるべき
        
        現在の実装では実行されない機能（このテストは失敗するはず）
        """
        # 目次ページのサンプルHTML
        index_html = f'''
        <ol class="topicPath">
            <li><a href="{self.base_url}">目次</a></li>
            <li><a href="{self.info_url}">小説情報</a></li>
            <li><a href="{self.comments_url}">感想</a></li>
        </ol>
        '''
        
        soup = BeautifulSoup(index_html, 'html.parser')
        
        # 新機能: 感想URLを抽出（まだ実装されていない）
        extracted_comments_url = self.scraper.extract_comments_url(soup)
        
        # 期待値との比較（このテストは現在失敗するはず）
        self.assertEqual(extracted_comments_url, self.comments_url,
                        "感想URLが正しく抽出されるべき")

    @patch.object(HamelnFinalScraper, 'get_page')
    @patch.object(HamelnFinalScraper, 'save_complete_page')
    def test_should_save_novel_info_page(self, mock_save_page, mock_get_page):
        """
        小説情報ページを取得・保存できるべき
        
        現在の実装では実行されない機能（このテストは失敗するはず）
        """
        # モックの設定
        mock_info_soup = BeautifulSoup('<html><body>小説情報ページ</body></html>', 'html.parser')
        mock_get_page.return_value = mock_info_soup
        mock_save_page.return_value = "/test/path/小説情報.html"
        
        # 新機能: 小説情報ページ保存（まだ実装されていない）
        result = self.scraper.save_novel_info_page(self.info_url, self.temp_dir, "テスト小説")
        
        # メソッドが呼ばれたことを確認（このテストは現在失敗するはず）
        mock_get_page.assert_called_once_with(self.info_url)
        mock_save_page.assert_called_once()
        self.assertIsNotNone(result, "小説情報ページが保存されるべき")

    @patch.object(HamelnFinalScraper, 'get_page')
    @patch.object(HamelnFinalScraper, 'save_complete_page')
    def test_should_save_comments_page(self, mock_save_page, mock_get_page):
        """
        感想ページを取得・保存できるべき
        
        現在の実装では実行されない機能（このテストは失敗するはず）
        """
        # モックの設定
        mock_comments_soup = BeautifulSoup('<html><body>感想ページ</body></html>', 'html.parser')
        mock_get_page.return_value = mock_comments_soup
        mock_save_page.return_value = "/test/path/感想.html"
        
        # 新機能: 感想ページ保存（まだ実装されていない）
        result = self.scraper.save_comments_page(self.comments_url, self.temp_dir, "テスト小説")
        
        # メソッドが呼ばれたことを確認（このテストは現在失敗するはず）
        mock_get_page.assert_called_once_with(self.comments_url)
        mock_save_page.assert_called_once()
        self.assertIsNotNone(result, "感想ページが保存されるべき")

    @patch.object(HamelnFinalScraper, 'save_novel_info_page')
    @patch.object(HamelnFinalScraper, 'save_comments_page')
    @patch.object(HamelnFinalScraper, 'extract_novel_info_url')
    @patch.object(HamelnFinalScraper, 'extract_comments_url')
    def test_scrape_novel_should_save_info_and_comments(self, mock_extract_comments, 
                                                       mock_extract_info, mock_save_comments, 
                                                       mock_save_info):
        """
        scrape_novel実行時に小説情報と感想も自動保存されるべき
        
        現在の実装では実行されない機能（このテストは失敗するはず）
        """
        # モックの設定
        mock_extract_info.return_value = self.info_url
        mock_extract_comments.return_value = self.comments_url
        mock_save_info.return_value = "/test/path/小説情報.html"
        mock_save_comments.return_value = "/test/path/感想.html"
        
        # 目次ページのサンプル
        index_html = f'''
        <html><body>
        <span>テスト小説</span>
        <ol class="topicPath">
            <li><a href="{self.info_url}">小説情報</a></li>
            <li><a href="{self.comments_url}">感想</a></li>
        </ol>
        </body></html>
        '''
        index_soup = BeautifulSoup(index_html, 'html.parser')
        
        # scrape_novelメソッドをパッチして部分的にテスト（複数章として設定）
        fake_chapter_links = [f"{self.base_url}1.html", f"{self.base_url}2.html"]
        with patch.object(self.scraper, 'get_page', return_value=index_soup), \
             patch.object(self.scraper, 'get_chapter_links', return_value=fake_chapter_links), \
             patch.object(self.scraper, 'extract_novel_info', return_value={'title': 'テスト小説', 'author': 'テスト作者'}), \
             patch.object(self.scraper, 'save_complete_page', return_value="/test/index.html"), \
             patch.object(self.scraper, 'process_html_resources'):
            
            # 新機能フラグを有効化してテスト
            self.scraper.enable_novel_info_saving = True
            self.scraper.enable_comments_saving = True
            
            # 新機能が統合されたscrape_novel実行
            self.scraper.scrape_novel(self.base_url)
            
            # 小説情報と感想の保存が実行されたことを確認
            mock_extract_info.assert_called_once()
            mock_extract_comments.assert_called_once()
            mock_save_info.assert_called_once()
            mock_save_comments.assert_called_once()

if __name__ == '__main__':
    unittest.main()