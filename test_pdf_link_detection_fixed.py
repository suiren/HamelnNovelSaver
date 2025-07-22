#!/usr/bin/env python3
"""
修正後のPDFリンク検出機能のテスト
ハーメルンの各種PDFダウンロードリンク形式に対応
"""

import unittest
import os
import tempfile
import shutil
from bs4 import BeautifulSoup
from hameln_scraper_final import HamelnFinalScraper
from unittest.mock import patch, Mock

class TestPDFLinkDetectionFixed(unittest.TestCase):
    
    def setUp(self):
        """テスト開始前の設定"""
        self.scraper = HamelnFinalScraper()
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """テスト終了後のクリーンアップ"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_comprehensive_pdf_link_detection(self):
        """包括的なPDFリンク検出テスト（修正後）"""
        # 様々な形式のPDFダウンロードリンクを含むHTMLページ
        comprehensive_html = """
        <html>
        <head><title>小説タイトル - 縦書き</title></head>
        <body>
            <div class="vertical-content">
                <!-- 従来型のリンク -->
                <a href="//syosetu.org/txtdownload.php?nid=378070&no=all&hankaku=0&code=sjis">SJIS版ダウンロード</a>
                <a href="//syosetu.org/pdfdownload.php?nid=378070&no=all">PDFダウンロード</a>
                
                <!-- ハーメルン実際の形式 -->
                <a href="/conv/pdf/378070_all.pdf" target="_blank">PDF版をダウンロード</a>
                <a href="/conv/txt/378070_all_sjis.txt" target="_blank">テキスト版(SJIS)</a>
                <a href="/conv/txt/378070_all_utf8.txt" target="_blank">テキスト版(UTF-8)</a>
                <a href="/conv/epub/378070_all.epub" target="_blank">EPUB版</a>
                
                <!-- API形式 -->
                <a href="//syosetu.org/api/download?format=pdf&nid=378070">API経由PDF</a>
                <a href="//syosetu.org/epubdownload.php?nid=378070">EPUBダウンロード</a>
                
                <!-- 非ダウンロードリンク（検出されないべき） -->
                <a href="//syosetu.org/novel/378070/">目次</a>
                <a href="//syosetu.org/?mode=ss_detail&nid=378070">小説情報</a>
            </div>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(comprehensive_html, 'html.parser')
        
        # 修正後のPDFリンク検出
        detected_links = self.scraper.extract_pdf_links_from_vertical_page(soup)
        
        # 期待される8つのダウンロードリンクが検出される
        self.assertEqual(len(detected_links), 8,
                        f"8つのダウンロードリンクが検出されるはず。実際: {len(detected_links)}")
        
        # 検出されるべきリンク
        expected_download_links = [
            "//syosetu.org/txtdownload.php?nid=378070&no=all&hankaku=0&code=sjis",
            "//syosetu.org/pdfdownload.php?nid=378070&no=all",
            "/conv/pdf/378070_all.pdf",
            "/conv/txt/378070_all_sjis.txt",
            "/conv/txt/378070_all_utf8.txt",
            "/conv/epub/378070_all.epub",
            "//syosetu.org/api/download?format=pdf&nid=378070",
            "//syosetu.org/epubdownload.php?nid=378070"
        ]
        
        for expected_link in expected_download_links:
            self.assertIn(expected_link, detected_links,
                         f"期待されるダウンロードリンクが検出されていません: {expected_link}")
        
        # 検出されないべきリンク
        non_download_links = [
            "//syosetu.org/novel/378070/",
            "//syosetu.org/?mode=ss_detail&nid=378070"
        ]
        
        for non_download_link in non_download_links:
            self.assertNotIn(non_download_link, detected_links,
                           f"非ダウンロードリンクが誤って検出されています: {non_download_link}")
    
    def test_real_hameln_structure_detection(self):
        """実際のハーメルン構造でのPDFリンク検出テスト"""
        realistic_html = """
        <html>
        <head><title>小説タイトル - 縦書き</title></head>
        <body>
            <div class="ss">
                <div class="novel_bn">
                    <a href="/conv/pdf/123456_all.pdf" target="_blank">PDF版をダウンロード</a>
                    <a href="/conv/txt/123456_all_sjis.txt" target="_blank">テキスト版(SJIS)</a>
                    <a href="/conv/txt/123456_all_utf8.txt" target="_blank">テキスト版(UTF-8)</a>
                    <a href="/conv/epub/123456_all.epub" target="_blank">EPUB版</a>
                </div>
            </div>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(realistic_html, 'html.parser')
        
        # 修正後は4つのリンクが検出される
        detected_links = self.scraper.extract_pdf_links_from_vertical_page(soup)
        self.assertEqual(len(detected_links), 4,
                        f"4つのハーメルン形式ダウンロードリンクが検出されるはず。実際: {len(detected_links)}")
        
        # 全ての期待されるリンクが検出される
        expected_links = [
            "/conv/pdf/123456_all.pdf",
            "/conv/txt/123456_all_sjis.txt", 
            "/conv/txt/123456_all_utf8.txt",
            "/conv/epub/123456_all.epub"
        ]
        
        for expected_link in expected_links:
            self.assertIn(expected_link, detected_links,
                         f"期待されるハーメルン形式リンクが検出されていません: {expected_link}")
    
    @patch('hameln_scraper_final.HamelnFinalScraper.download_file')
    def test_fixed_pdf_download_integration(self, mock_download):
        """修正後のPDFダウンロード統合テスト"""
        # モックの設定
        mock_download.return_value = os.path.join(self.test_dir, "downloaded_file.pdf")
        
        # ハーメルン形式のPDFリンクを含むHTML
        html_with_pdf_links = """
        <html>
        <body>
            <div class="ss">
                <a href="/conv/pdf/123456_all.pdf">PDF版</a>
                <a href="/conv/txt/123456_all.txt">テキスト版</a>
            </div>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(html_with_pdf_links, 'html.parser')
        
        # PDFダウンロード・ローカル化を実行
        updated_soup = self.scraper.download_and_localize_pdf_links(
            soup, 
            self.test_dir,
            "テスト小説"
        )
        
        # ダウンロード関数が呼び出されたかテスト
        self.assertEqual(mock_download.call_count, 2,
                        "2つのファイルがダウンロードされるはず")
        
        # リンクがローカル化されたかテスト
        links = updated_soup.find_all('a', href=True)
        for link in links:
            href = link.get('href')
            # ローカルファイル名になっているかチェック
            self.assertFalse(href.startswith('/conv/'),
                           f"リンクがローカル化されていません: {href}")
    
    def test_edge_cases_and_variations(self):
        """エッジケースと様々なバリエーションのテスト"""
        edge_cases_html = """
        <html>
        <body>
            <!-- 大文字小文字の混在 -->
            <a href="/CONV/PDF/test.pdf">大文字PDF</a>
            <a href="/Conv/Txt/test.txt">混在テキスト</a>
            
            <!-- ファイル名のバリエーション -->
            <a href="/conv/pdf/novel_123_chapter_all.pdf">長いファイル名PDF</a>
            <a href="/conv/epub/short.epub">短いファイル名EPUB</a>
            
            <!-- パラメータ付きURL -->
            <a href="/conv/txt/test.txt?format=sjis&encoding=shift_jis">パラメータ付きTXT</a>
            
            <!-- 類似但し非対象のURL -->
            <a href="/conversation/pdf/not_download.html">対話ページ（非対象）</a>
            <a href="/convert_service/pdf_viewer.php">変換サービス（非対象）</a>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(edge_cases_html, 'html.parser')
        
        detected_links = self.scraper.extract_pdf_links_from_vertical_page(soup)
        
        # 検出されるべきリンク（部分文字列マッチで検出される）
        expected_detected = [
            "/CONV/PDF/test.pdf",  # 大文字でも検出
            "/Conv/Txt/test.txt",  # 混在でも検出
            "/conv/pdf/novel_123_chapter_all.pdf",  # 長いファイル名も検出
            "/conv/epub/short.epub",  # 短いファイル名も検出
            "/conv/txt/test.txt?format=sjis&encoding=shift_jis"  # パラメータ付きも検出
        ]
        
        for expected_link in expected_detected:
            self.assertIn(expected_link, detected_links,
                         f"エッジケースのリンクが検出されていません: {expected_link}")
        
        # 類似但し対象外のリンクは検出されない
        non_target_links = [
            "/conversation/pdf/not_download.html",  # conversationは対象外
            "/convert_service/pdf_viewer.php"  # convert_serviceは対象外
        ]
        
        for non_target_link in non_target_links:
            self.assertNotIn(non_target_link, detected_links,
                           f"非対象リンクが誤って検出されています: {non_target_link}")

if __name__ == '__main__':
    unittest.main()