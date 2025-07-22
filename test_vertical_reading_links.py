#!/usr/bin/env python3
"""
縦書きリンクと小説情報ページリンクの保存機能テスト
"""

import unittest
import os
import tempfile
import shutil
from bs4 import BeautifulSoup
from hameln_scraper_final import HamelnFinalScraper
from unittest.mock import patch, Mock

class TestVerticalReadingLinks(unittest.TestCase):
    
    def setUp(self):
        """テスト開始前の設定"""
        self.scraper = HamelnFinalScraper()
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """テスト終了後のクリーンアップ"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_extract_vertical_reading_link(self):
        """縦書きリンクの抽出テスト"""
        # テスト用のHTMLを作成（実際のハーメルンページ構造に基づく）
        html_content = """
        <html>
        <head><title>テスト小説</title></head>
        <body>
            <ol class="topicPath">
                <li><a href="//syosetu.org/novel/378070/">目次</a></li>
                <li><a href="//syosetu.org/?mode=ss_detail&amp;nid=378070">小説情報</a></li>
                <li><a href="//syosetu.org/?mode=ss_detail3&amp;nid=378070">縦書き</a></li>
            </ol>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 縦書きリンクを抽出する機能をテスト
        vertical_link = self.scraper.extract_vertical_reading_link(soup)
        
        # 期待される結果
        expected_link = "//syosetu.org/?mode=ss_detail3&nid=378070"
        self.assertEqual(vertical_link, expected_link)
        
    def test_extract_novel_info_link(self):
        """小説情報リンクの抽出テスト"""
        html_content = """
        <html>
        <head><title>テスト小説</title></head>
        <body>
            <ol class="topicPath">
                <li><a href="//syosetu.org/novel/378070/">目次</a></li>
                <li><a href="//syosetu.org/?mode=ss_detail&amp;nid=378070">小説情報</a></li>
                <li><a href="//syosetu.org/?mode=ss_detail3&amp;nid=378070">縦書き</a></li>
            </ol>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 小説情報リンクを抽出する機能をテスト
        info_link = self.scraper.extract_novel_info_link(soup)
        
        # 期待される結果
        expected_link = "//syosetu.org/?mode=ss_detail&nid=378070"
        self.assertEqual(info_link, expected_link)
        
    def test_extract_additional_links_from_vertical_page(self):
        """縦書きページ内の追加リンクの抽出テスト"""
        # 縦書きページの内容（仮想的なページ構造）
        vertical_page_html = """
        <html>
        <head><title>テスト小説 - 縦書き</title></head>
        <body>
            <div class="vertical-content">
                <p>縦書きテキストコンテンツ</p>
                <a href="//syosetu.org/?mode=review&nid=378070">感想</a>
                <a href="//syosetu.org/?mode=rating_input&nid=378070">評価</a>
            </div>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(vertical_page_html, 'html.parser')
        
        # 縦書きページ内の追加リンクを抽出する機能をテスト
        additional_links = self.scraper.extract_additional_links_from_vertical_page(soup)
        
        # 期待される結果（感想と評価のリンク）
        expected_links = [
            "//syosetu.org/?mode=review&nid=378070",
            "//syosetu.org/?mode=rating_input&nid=378070"
        ]
        
        self.assertEqual(len(additional_links), 2)
        self.assertIn("//syosetu.org/?mode=review&nid=378070", additional_links)
        self.assertIn("//syosetu.org/?mode=rating_input&nid=378070", additional_links)
        
    @patch('hameln_scraper_final.HamelnFinalScraper.get_page')
    @patch('hameln_scraper_final.HamelnFinalScraper.save_complete_page')
    def test_save_vertical_reading_page(self, mock_save_complete_page, mock_get_page):
        """縦書きページの保存テスト"""
        # モックの設定
        mock_soup = Mock()
        mock_soup.find_all.return_value = []  # 空のリストを返す
        mock_get_page.return_value = mock_soup
        mock_save_complete_page.return_value = "/test/path/vertical.html"
        
        # 縦書きページ保存機能をテスト
        vertical_url = "https://syosetu.org/?mode=ss_detail3&nid=378070"
        result = self.scraper.save_vertical_reading_page(
            vertical_url, 
            self.test_dir, 
            "テスト小説"
        )
        
        # 保存が成功したかテスト
        self.assertIsNotNone(result)
        self.assertIn('file_path', result)
        self.assertIn('additional_links', result)
        mock_get_page.assert_called_once_with(vertical_url)
        
    @patch('hameln_scraper_final.HamelnFinalScraper.get_page')
    @patch('hameln_scraper_final.HamelnFinalScraper.save_complete_page')
    def test_save_novel_info_page_with_vertical_link(self, mock_save_complete_page, mock_get_page):
        """小説情報ページの保存テスト（縦書きリンクを含む）"""
        # モックの設定
        mock_soup = Mock()
        mock_soup.find_all.return_value = []  # 空のリストを返す
        mock_get_page.return_value = mock_soup
        mock_save_complete_page.return_value = "/test/path/info.html"
        
        # 小説情報ページ保存機能をテスト
        info_url = "https://syosetu.org/?mode=ss_detail&nid=378070"
        result = self.scraper.save_novel_info_page_with_vertical_link(
            info_url, 
            self.test_dir, 
            "テスト小説"
        )
        
        # 保存が成功したかテスト
        self.assertIsNotNone(result)
        self.assertEqual(result, "/test/path/info.html")
        mock_get_page.assert_called_once_with(info_url)
        
    def test_process_vertical_reading_links_integration(self):
        """縦書きリンク処理の統合テスト"""
        # 章ページの内容（縦書きリンクを含む）
        chapter_html = """
        <html>
        <head><title>テスト小説 - 第1話</title></head>
        <body>
            <ol class="topicPath">
                <li><a href="//syosetu.org/novel/378070/">目次</a></li>
                <li><a href="//syosetu.org/?mode=ss_detail&amp;nid=378070">小説情報</a></li>
                <li><a href="//syosetu.org/?mode=ss_detail3&amp;nid=378070">縦書き</a></li>
            </ol>
            <div class="novel-content">
                <p>小説の本文がここに入ります。</p>
            </div>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(chapter_html, 'html.parser')
        
        # 縦書きリンクの処理を実行する機能をテスト
        with patch.object(self.scraper, 'save_vertical_reading_page') as mock_save_vertical, \
             patch.object(self.scraper, 'save_novel_info_page_with_vertical_link') as mock_save_info:
            
            mock_save_vertical.return_value = "/test/vertical.html"
            mock_save_info.return_value = "/test/info.html"
            
            result = self.scraper.process_vertical_reading_links(
                soup, 
                self.test_dir, 
                "テスト小説"
            )
            
            # 処理が成功したかテスト
            self.assertIsNotNone(result)
            self.assertIn('vertical_page', result)
            self.assertIn('info_page', result)
            
            # 各保存メソッドが呼び出されたかテスト
            mock_save_vertical.assert_called_once()
            mock_save_info.assert_called_once()
            
    def test_update_navigation_links_with_vertical_pages(self):
        """ナビゲーションリンクの更新テスト（縦書きページ対応）"""
        # 修正前のHTMLコンテンツ
        html_content = """
        <html>
        <head><title>テスト小説</title></head>
        <body>
            <ol class="topicPath">
                <li><a href="//syosetu.org/novel/378070/">目次</a></li>
                <li><a href="//syosetu.org/?mode=ss_detail&amp;nid=378070">小説情報</a></li>
                <li><a href="//syosetu.org/?mode=ss_detail3&amp;nid=378070">縦書き</a></li>
            </ol>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # リンクの更新を実行
        updated_soup = self.scraper.update_navigation_links_with_vertical_pages(
            soup, 
            "目次.html",
            "小説情報.html", 
            "縦書き.html"
        )
        
        # リンクが正しく更新されたかテスト
        links = updated_soup.find_all('a')
        
        # 目次リンクの確認
        index_link = next((link for link in links if "目次" in link.get_text()), None)
        self.assertIsNotNone(index_link)
        self.assertEqual(index_link.get('href'), "目次.html")
        
        # 小説情報リンクの確認
        info_link = next((link for link in links if "小説情報" in link.get_text()), None)
        self.assertIsNotNone(info_link)
        self.assertEqual(info_link.get('href'), "小説情報.html")
        
        # 縦書きリンクの確認
        vertical_link = next((link for link in links if "縦書き" in link.get_text()), None)
        self.assertIsNotNone(vertical_link)
        # 縦書きリンクは update_navigation_links_with_vertical_pages により更新される
        self.assertEqual(vertical_link.get('href'), "縦書き.html")

if __name__ == '__main__':
    unittest.main()