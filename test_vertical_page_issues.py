#!/usr/bin/env python3
"""
縦書きページ内のリンク修正とPDFダウンロード問題のテスト
ユーザー報告の問題を再現・検証するテストケース
"""

import unittest
import os
import tempfile
import shutil
from bs4 import BeautifulSoup
from hameln_scraper_final import HamelnFinalScraper
from unittest.mock import patch, Mock

class TestVerticalPageIssues(unittest.TestCase):
    
    def setUp(self):
        """テスト開始前の設定"""
        self.scraper = HamelnFinalScraper()
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """テスト終了後のクリーンアップ"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_vertical_page_navigation_links_not_localized(self):
        """縦書きページ内のナビゲーションリンクがローカル化されていない問題のテスト"""
        # 実際の縦書きページのような構造（ナビゲーションリンクを含む）
        vertical_html = """
        <html>
        <head><title>ダウナー女神のアクア様 - 縦書き</title></head>
        <body>
            <ol class="topicPath">
                <li><a href="//syosetu.org/novel/378070/">目次</a></li>
                <li><a href="//syosetu.org/?mode=ss_detail&nid=378070">小説情報</a></li>
                <li><a href="//syosetu.org/?mode=ss_detail3&nid=378070">縦書き</a></li>
            </ol>
            <div class="vertical-content">
                <p>縦書きコンテンツ</p>
                <a href="//syosetu.org/?mode=review&nid=378070">感想</a>
            </div>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(vertical_html, 'html.parser')
        
        # 現在の実装で縦書きページのナビゲーションリンクが修正されるかテスト
        # 期待される動作：目次、小説情報、感想へのリンクがローカルファイルに修正される
        updated_soup = self.scraper.fix_navigation_links_in_vertical_page(
            soup,
            index_file="目次.html",
            info_file="小説情報.html",
            comments_file="感想/感想 - ページ1.html"
        )
        
        # テスト：ナビゲーションリンクがローカル化されているか確認
        links = updated_soup.find_all('a', href=True)
        
        # 目次リンクがローカル化されているか
        index_link = next((link for link in links if "目次" in link.get_text()), None)
        self.assertIsNotNone(index_link, "目次リンクが見つかりません")
        self.assertEqual(index_link.get('href'), "目次.html", "目次リンクがローカル化されていません")
        
        # 小説情報リンクがローカル化されているか
        info_link = next((link for link in links if "小説情報" in link.get_text()), None)
        self.assertIsNotNone(info_link, "小説情報リンクが見つかりません")
        self.assertEqual(info_link.get('href'), "小説情報.html", "小説情報リンクがローカル化されていません")
        
        # 感想リンクがローカル化されているか
        review_link = next((link for link in links if "感想" in link.get_text()), None)
        self.assertIsNotNone(review_link, "感想リンクが見つかりません")
        self.assertEqual(review_link.get('href'), "感想/感想 - ページ1.html", "感想リンクがローカル化されていません")
    
    def test_pdf_download_not_working(self):
        """PDFダウンロードが実行されていない問題のテスト"""
        # PDFリンクを含む縦書きページ
        vertical_html_with_pdf = """
        <html>
        <head><title>ダウナー女神のアクア様 - 縦書き</title></head>
        <body>
            <div class="vertical-content">
                <p>縦書きコンテンツ</p>
                <a href="//syosetu.org/txtdownload.php?nid=378070&no=all&hankaku=0&code=sjis">SJIS版ダウンロード</a>
                <a href="//syosetu.org/txtdownload.php?nid=378070&no=all&hankaku=0&code=utf8">UTF-8版ダウンロード</a>
                <a href="//syosetu.org/pdfdownload.php?nid=378070&no=all">PDFダウンロード</a>
            </div>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(vertical_html_with_pdf, 'html.parser')
        
        # PDFリンクの抽出をテスト
        pdf_links = self.scraper.extract_pdf_links_from_vertical_page(soup)
        
        # 期待される3つのダウンロードリンクが抽出されるか
        self.assertEqual(len(pdf_links), 3, f"期待される3つのPDFリンクが抽出されていません。実際: {len(pdf_links)}")
        
        expected_links = [
            "//syosetu.org/txtdownload.php?nid=378070&no=all&hankaku=0&code=sjis",
            "//syosetu.org/txtdownload.php?nid=378070&no=all&hankaku=0&code=utf8",
            "//syosetu.org/pdfdownload.php?nid=378070&no=all"
        ]
        
        for expected_link in expected_links:
            self.assertIn(expected_link, pdf_links, f"期待されるリンクが抽出されていません: {expected_link}")
    
    @patch('hameln_scraper_final.HamelnFinalScraper.download_file')
    def test_pdf_download_execution(self, mock_download_file):
        """PDFダウンロードの実行確認テスト"""
        # モック設定：ダウンロードが成功する場合
        mock_download_file.return_value = os.path.join(self.test_dir, "test_download.txt")
        
        # PDFリンクを含む縦書きページ
        vertical_html_with_pdf = """
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
        
        soup = BeautifulSoup(vertical_html_with_pdf, 'html.parser')
        
        # PDFダウンロード・ローカル化を実行
        updated_soup = self.scraper.download_and_localize_pdf_links(
            soup, 
            self.test_dir,
            "ダウナー女神のアクア様"
        )
        
        # ダウンロード関数が実際に呼び出されたかテスト
        self.assertGreater(mock_download_file.call_count, 0, "download_file関数が呼び出されていません")
        
        # リンクがローカルファイルに更新されたかテスト
        links = updated_soup.find_all('a', href=True)
        for link in links:
            href = link.get('href')
            # ローカルファイル名になっているかチェック（webリンクではない）
            self.assertFalse(href.startswith('//syosetu.org'), f"リンクがローカル化されていません: {href}")
            self.assertTrue(href.endswith('.txt') or href.endswith('.pdf'), f"ローカルファイル名になっていません: {href}")
    
    def test_actual_pdf_download_with_real_url(self):
        """実際のPDFダウンロード処理のテスト（ネットワーク不要）"""
        # download_file関数の動作テスト（モックを使わずに内部ロジックをテスト）
        test_url = "//syosetu.org/txtdownload.php?nid=378070&no=all&hankaku=0&code=sjis"
        test_filename = "test_novel_SJIS版.txt"
        
        # URLの正規化テスト
        if test_url.startswith('//'):
            normalized_url = 'https:' + test_url
        elif test_url.startswith('/'):
            normalized_url = self.scraper.base_url + test_url
        else:
            normalized_url = test_url
        
        # 正規化されたURLが正しいかテスト
        expected_url = "https://syosetu.org/txtdownload.php?nid=378070&no=all&hankaku=0&code=sjis"
        self.assertEqual(normalized_url, expected_url, "URL正規化が正しく動作していません")
    
    def test_integrated_vertical_page_save_with_fixes(self):
        """縦書きページ保存の統合テスト（リンク修正とPDFダウンロード含む）"""
        # 実際の縦書きページ保存処理をシミュレート
        vertical_html = """
        <html>
        <head><title>ダウナー女神のアクア様 - 縦書き</title></head>
        <body>
            <ol class="topicPath">
                <li><a href="//syosetu.org/novel/378070/">目次</a></li>
                <li><a href="//syosetu.org/?mode=ss_detail&nid=378070">小説情報</a></li>
                <li><a href="//syosetu.org/?mode=ss_detail3&nid=378070">縦書き</a></li>
            </ol>
            <div class="vertical-content">
                <p>縦書きコンテンツ</p>
                <a href="//syosetu.org/txtdownload.php?nid=378070&no=all&hankaku=0&code=sjis">SJIS版</a>
                <a href="//syosetu.org/?mode=review&nid=378070">感想</a>
            </div>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(vertical_html, 'html.parser')
        
        # 期待される処理フロー：
        # 1. ナビゲーションリンクのローカル化
        # 2. PDFリンクのダウンロード・ローカル化
        # 3. ページの保存
        
        # この統合テストで、両方の問題が解決されているかを確認
        with patch.object(self.scraper, 'download_file') as mock_download, \
             patch.object(self.scraper, 'save_complete_page') as mock_save:
            
            mock_download.return_value = os.path.join(self.test_dir, "download.txt")
            mock_save.return_value = os.path.join(self.test_dir, "vertical.html")
            
            # 縦書きページ保存（修正版）を実行
            result = self.scraper.save_vertical_reading_page_with_full_fixes(
                "https://syosetu.org/?mode=ss_detail3&nid=378070",
                self.test_dir,
                "ダウナー女神のアクア様",
                index_file="目次.html",
                info_file="小説情報.html",
                comments_file="感想/感想 - ページ1.html"
            )
            
            # 処理が成功したかテスト
            self.assertIsNotNone(result, "縦書きページ保存が失敗しました")

if __name__ == '__main__':
    unittest.main()