#!/usr/bin/env python3
"""
縦書きページでのPDFリンク検出失敗問題の再現テスト
実際のハーメルンの縦書きページのPDFリンク構造に基づくテストケース
"""

import unittest
import os
import tempfile
import shutil
from bs4 import BeautifulSoup
from hameln_scraper_final import HamelnFinalScraper
from unittest.mock import patch, Mock

class TestPDFLinkDetectionIssue(unittest.TestCase):
    
    def setUp(self):
        """テスト開始前の設定"""
        self.scraper = HamelnFinalScraper()
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """テスト終了後のクリーンアップ"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_current_pdf_detection_failure(self):
        """現在の実装でPDFリンクが検出されない問題の再現テスト"""
        # 実際のハーメルン縦書きページに存在する可能性のあるPDFリンク構造
        vertical_html_with_various_pdf_links = """
        <html>
        <head><title>ダウナー女神のアクア様 - 縦書き</title></head>
        <body>
            <div class="vertical-content">
                <p>縦書きコンテンツ</p>
                <!-- 既存の検出条件でマッチするリンク -->
                <a href="//syosetu.org/txtdownload.php?nid=378070&no=all&hankaku=0&code=sjis">SJIS版ダウンロード</a>
                <a href="//syosetu.org/pdfdownload.php?nid=378070&no=all">PDFダウンロード</a>
                
                <!-- 検出されない可能性のあるリンク（問題の原因） -->
                <a href="//syosetu.org/conv/pdf/378070_all.pdf">PDF版</a>
                <a href="//syosetu.org/conv/epub/378070_all.epub">EPUB版</a>
                <a href="//syosetu.org/api/download?format=pdf&nid=378070">API経由PDF</a>
                <a href="/conv/txt/378070_sjis.txt">相対パスTXT</a>
            </div>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(vertical_html_with_various_pdf_links, 'html.parser')
        
        # 現在の実装でPDFリンクを抽出
        current_detected_links = self.scraper.extract_pdf_links_from_vertical_page(soup)
        
        # 現在の実装では2つのリンクのみ検出される（txtdownload.php と pdfdownload.php）
        self.assertEqual(len(current_detected_links), 2, 
                        f"現在の実装では2つのリンクのみ検出されるはず。実際: {len(current_detected_links)}")
        
        # 検出されるべきリンク
        expected_detected = [
            "//syosetu.org/txtdownload.php?nid=378070&no=all&hankaku=0&code=sjis",
            "//syosetu.org/pdfdownload.php?nid=378070&no=all"
        ]
        
        for expected_link in expected_detected:
            self.assertIn(expected_link, current_detected_links, 
                         f"期待されるリンクが検出されていません: {expected_link}")
        
        # 検出されないリンク（問題となっているリンク）
        undetected_links = [
            "//syosetu.org/conv/pdf/378070_all.pdf",
            "//syosetu.org/conv/epub/378070_all.epub", 
            "//syosetu.org/api/download?format=pdf&nid=378070",
            "/conv/txt/378070_sjis.txt"
        ]
        
        for undetected_link in undetected_links:
            self.assertNotIn(undetected_link, current_detected_links,
                           f"このリンクは現在の実装では検出されないはず: {undetected_link}")
    
    def test_improved_pdf_detection_should_work(self):
        """改善後のPDFリンク検出が動作するはずのテスト（期待される動作）"""
        # 同じHTMLを使用
        vertical_html_with_various_pdf_links = """
        <html>
        <head><title>ダウナー女神のアクア様 - 縦書き</title></head>
        <body>
            <div class="vertical-content">
                <p>縦書きコンテンツ</p>
                <a href="//syosetu.org/txtdownload.php?nid=378070&no=all&hankaku=0&code=sjis">SJIS版ダウンロード</a>
                <a href="//syosetu.org/pdfdownload.php?nid=378070&no=all">PDFダウンロード</a>
                <a href="//syosetu.org/conv/pdf/378070_all.pdf">PDF版</a>
                <a href="//syosetu.org/conv/epub/378070_all.epub">EPUB版</a>
                <a href="//syosetu.org/api/download?format=pdf&nid=378070">API経由PDF</a>
                <a href="/conv/txt/378070_sjis.txt">相対パスTXT</a>
            </div>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(vertical_html_with_various_pdf_links, 'html.parser')
        
        # 改善されたPDFリンク検出関数（実装前なので手動でテスト）
        improved_detected_links = self._extract_pdf_links_improved(soup)
        
        # 改善後は6つ全てのリンクが検出される
        self.assertEqual(len(improved_detected_links), 6,
                        f"改善後は6つ全てのリンクが検出されるはず。実際: {len(improved_detected_links)}")
        
        # 全てのダウンロードリンクが検出される
        all_expected_links = [
            "//syosetu.org/txtdownload.php?nid=378070&no=all&hankaku=0&code=sjis",
            "//syosetu.org/pdfdownload.php?nid=378070&no=all",
            "//syosetu.org/conv/pdf/378070_all.pdf",
            "//syosetu.org/conv/epub/378070_all.epub",
            "//syosetu.org/api/download?format=pdf&nid=378070",
            "/conv/txt/378070_sjis.txt"
        ]
        
        for expected_link in all_expected_links:
            self.assertIn(expected_link, improved_detected_links,
                         f"改善後は全てのリンクが検出されるはず: {expected_link}")
    
    def _extract_pdf_links_improved(self, soup):
        """改善されたPDFリンク検出のテスト用実装"""
        pdf_links = []
        
        # 改善された検索条件
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href and (
                'download' in href or 
                'txtdownload' in href or 
                'pdfdownload' in href or
                '/conv/pdf/' in href or
                '/conv/epub/' in href or
                '/conv/txt/' in href or
                'epubdownload' in href
            ):
                pdf_links.append(href)
        
        return pdf_links
    
    def test_real_hameln_vertical_page_structure(self):
        """実際のハーメルン縦書きページの構造に基づくテスト"""
        # 実際のハーメルンの縦書きページで見つかる可能性のあるPDFリンク
        realistic_vertical_html = """
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
                <div class="novel_text">
                    <p>縦書きで表示される小説本文</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(realistic_vertical_html, 'html.parser')
        
        # 現在の実装では検出されない
        current_links = self.scraper.extract_pdf_links_from_vertical_page(soup)
        self.assertEqual(len(current_links), 0, 
                        "現在の実装では実際のハーメルン形式のPDFリンクは検出されない")
        
        # 改善後は4つのリンクが検出される
        improved_links = self._extract_pdf_links_improved(soup)
        self.assertEqual(len(improved_links), 4,
                        f"改善後は4つのリンクが検出されるはず。実際: {len(improved_links)}")

if __name__ == '__main__':
    unittest.main()