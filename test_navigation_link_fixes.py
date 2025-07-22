#!/usr/bin/env python3
"""
ナビゲーションリンク修正機能のテスト
目次・感想・小説情報ページでの縦書きページリンク修正とPDFダウンロード機能のテスト
"""

import unittest
import os
import tempfile
import shutil
from bs4 import BeautifulSoup
from hameln_scraper_final import HamelnFinalScraper
from unittest.mock import patch, Mock

class TestNavigationLinkFixes(unittest.TestCase):
    
    def setUp(self):
        """テスト開始前の設定"""
        self.scraper = HamelnFinalScraper()
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """テスト終了後のクリーンアップ"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_fix_vertical_links_in_index_page(self):
        """目次ページの縦書きリンク修正テスト"""
        # 目次ページのHTMLコンテンツ（縦書きリンクを含む）
        index_html = """
        <html>
        <head><title>ダウナー女神のアクア様 - 目次</title></head>
        <body>
            <ol class="topicPath">
                <li><a href="//syosetu.org/novel/378070/">目次</a></li>
                <li><a href="//syosetu.org/?mode=ss_detail&nid=378070">小説情報</a></li>
                <li><a href="//syosetu.org/?mode=ss_detail3&nid=378070">縦書き</a></li>
            </ol>
            <div class="novel-list">
                <ul>
                    <li><a href="//syosetu.org/novel/378070/1.html">第一話　女神、降り立つ。そしてやらかす。</a></li>
                    <li><a href="//syosetu.org/novel/378070/2.html">第二話　アクアが異世界転移者を呼び出すまで</a></li>
                </ul>
            </div>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(index_html, 'html.parser')
        
        # 目次ページの縦書きリンクを修正
        updated_soup = self.scraper.fix_vertical_links_in_all_pages(
            soup,
            index_file="目次.html",
            info_file="小説情報.html", 
            vertical_file="縦書き.html"
        )
        
        # 縦書きリンクが正しく修正されたかテスト
        vertical_link = updated_soup.find('a', string="縦書き")
        self.assertIsNotNone(vertical_link)
        self.assertEqual(vertical_link.get('href'), "縦書き.html")
        
        # 小説情報リンクも正しく修正されているかテスト
        info_link = updated_soup.find('a', string="小説情報")
        self.assertIsNotNone(info_link)
        self.assertEqual(info_link.get('href'), "小説情報.html")
        
    def test_fix_vertical_links_in_comments_page(self):
        """感想ページの縦書きリンク修正テスト"""
        # 感想ページのHTMLコンテンツ（縦書きリンクを含む）
        comments_html = """
        <html>
        <head><title>ダウナー女神のアクア様 - 感想</title></head>
        <body>
            <ol class="topicPath">
                <li><a href="//syosetu.org/novel/378070/">目次</a></li>
                <li><a href="//syosetu.org/?mode=ss_detail&nid=378070">小説情報</a></li>
                <li><a href="//syosetu.org/?mode=ss_detail3&nid=378070">縦書き</a></li>
            </ol>
            <div class="review-content">
                <p>この小説の感想内容</p>
            </div>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(comments_html, 'html.parser')
        
        # 感想ページの縦書きリンクを修正
        updated_soup = self.scraper.fix_vertical_links_in_all_pages(
            soup,
            index_file="目次.html",
            info_file="小説情報.html", 
            vertical_file="縦書き.html"
        )
        
        # 縦書きリンクが正しく修正されたかテスト
        vertical_link = updated_soup.find('a', string="縦書き")
        self.assertIsNotNone(vertical_link)
        self.assertEqual(vertical_link.get('href'), "縦書き.html")
        
    def test_fix_vertical_links_in_novel_info_page(self):
        """小説情報ページの縦書きリンク修正テスト"""
        # 小説情報ページのHTMLコンテンツ（縦書きリンクを含む）
        info_html = """
        <html>
        <head><title>ダウナー女神のアクア様 - 小説情報</title></head>
        <body>
            <ol class="topicPath">
                <li><a href="//syosetu.org/novel/378070/">目次</a></li>
                <li><a href="//syosetu.org/?mode=ss_detail&nid=378070">小説情報</a></li>
                <li><a href="//syosetu.org/?mode=ss_detail3&nid=378070">縦書き</a></li>
            </ol>
            <div class="novel-info">
                <p>小説の詳細情報</p>
            </div>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(info_html, 'html.parser')
        
        # 小説情報ページの縦書きリンクを修正
        updated_soup = self.scraper.fix_vertical_links_in_all_pages(
            soup,
            index_file="目次.html",
            info_file="小説情報.html", 
            vertical_file="縦書き.html"
        )
        
        # 縦書きリンクが正しく修正されたかテスト
        vertical_link = updated_soup.find('a', string="縦書き")
        self.assertIsNotNone(vertical_link)
        self.assertEqual(vertical_link.get('href'), "縦書き.html")
        
    def test_extract_pdf_links_from_vertical_page(self):
        """縦書きページからPDFリンクの抽出テスト"""
        # 縦書きページのHTMLコンテンツ（PDFリンクを含む）
        vertical_html = """
        <html>
        <head><title>ダウナー女神のアクア様 - 縦書き</title></head>
        <body>
            <div class="vertical-content">
                <p>縦書きコンテンツ</p>
                <a href="//syosetu.org/txtdownload.php?nid=378070&no=all&hankaku=0&code=sjis">SJIS版</a>
                <a href="//syosetu.org/txtdownload.php?nid=378070&no=all&hankaku=0&code=utf8">UTF-8版</a>
                <a href="//syosetu.org/pdfdownload.php?nid=378070&no=all">PDFダウンロード</a>
            </div>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(vertical_html, 'html.parser')
        
        # PDFリンクを抽出
        pdf_links = self.scraper.extract_pdf_links_from_vertical_page(soup)
        
        # 期待されるPDFリンク
        expected_links = [
            "//syosetu.org/txtdownload.php?nid=378070&no=all&hankaku=0&code=sjis",
            "//syosetu.org/txtdownload.php?nid=378070&no=all&hankaku=0&code=utf8", 
            "//syosetu.org/pdfdownload.php?nid=378070&no=all"
        ]
        
        self.assertEqual(len(pdf_links), 3)
        for expected_link in expected_links:
            self.assertIn(expected_link, pdf_links)
            
    @patch('hameln_scraper_final.HamelnFinalScraper.download_file')
    def test_download_and_localize_pdf_links(self, mock_download):
        """PDFリンクのダウンロード・ローカル化テスト"""
        # モックの設定
        mock_download.return_value = "/test/path/downloaded_file.txt"
        
        # 縦書きページのHTMLコンテンツ（PDFリンクを含む）
        vertical_html = """
        <html>
        <head><title>ダウナー女神のアクア様 - 縦書き</title></head>
        <body>
            <div class="vertical-content">
                <a href="//syosetu.org/txtdownload.php?nid=378070&no=all&hankaku=0&code=sjis">SJIS版</a>
                <a href="//syosetu.org/txtdownload.php?nid=378070&no=all&hankaku=0&code=utf8">UTF-8版</a>
            </div>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(vertical_html, 'html.parser')
        
        # PDFリンクのダウンロード・ローカル化を実行
        updated_soup = self.scraper.download_and_localize_pdf_links(
            soup, 
            self.test_dir,
            "ダウナー女神のアクア様"
        )
        
        # リンクがローカルファイルに更新されたかテスト
        links = updated_soup.find_all('a', href=True)
        for link in links:
            href = link.get('href')
            # ローカルファイルパス（相対パス）になっているかチェック
            self.assertFalse(href.startswith('//syosetu.org'))
            self.assertTrue(href.endswith('.txt') or href.endswith('.pdf'))
            
        # ダウンロード関数が呼び出されたかテスト
        self.assertGreater(mock_download.call_count, 0)
        
    def test_integration_all_page_navigation_fixes(self):
        """全ページのナビゲーションリンク修正統合テスト"""
        # 複数ページの修正を一括で処理するテスト
        pages_data = {
            "index.html": """
            <html><body>
                <ol class="topicPath">
                    <li><a href="//syosetu.org/novel/378070/">目次</a></li>
                    <li><a href="//syosetu.org/?mode=ss_detail&nid=378070">小説情報</a></li>
                    <li><a href="//syosetu.org/?mode=ss_detail3&nid=378070">縦書き</a></li>
                </ol>
            </body></html>
            """,
            "info.html": """
            <html><body>
                <ol class="topicPath">
                    <li><a href="//syosetu.org/novel/378070/">目次</a></li>
                    <li><a href="//syosetu.org/?mode=ss_detail&nid=378070">小説情報</a></li>
                    <li><a href="//syosetu.org/?mode=ss_detail3&nid=378070">縦書き</a></li>
                </ol>
            </body></html>
            """
        }
        
        # 各ページのナビゲーションリンクを修正
        for page_name, html_content in pages_data.items():
            soup = BeautifulSoup(html_content, 'html.parser')
            
            updated_soup = self.scraper.fix_vertical_links_in_all_pages(
                soup,
                index_file="目次.html",
                info_file="小説情報.html",
                vertical_file="縦書き.html"
            )
            
            # 各リンクが正しく修正されたかテスト
            vertical_link = updated_soup.find('a', string="縦書き")
            self.assertIsNotNone(vertical_link, f"{page_name}の縦書きリンクが見つかりません")
            self.assertEqual(vertical_link.get('href'), "縦書き.html", f"{page_name}の縦書きリンクが正しく修正されていません")

if __name__ == '__main__':
    unittest.main()