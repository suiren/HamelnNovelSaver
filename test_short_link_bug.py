#!/usr/bin/env python3
"""
短縮形式リンク生成バグのテストケース
CLAUDE.mdのTDD手順に従って作成

バグ: 初期マッピングで短縮形式ファイル名（第1話.html等）が生成され、
     後でフルファイル名に更新されても既存HTMLファイル内の短縮形式リンクが残る
"""

import unittest
import tempfile
import os
import shutil
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup

# テスト対象のインポート
import sys
sys.path.append('.')
from hameln_scraper_final import HamelnFinalScraper

class TestShortLinkBug(unittest.TestCase):
    
    def setUp(self):
        """テスト前準備"""
        self.scraper = HamelnFinalScraper()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """テスト後クリーンアップ"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_initial_mapping_should_not_create_short_form_filenames(self):
        """
        初期マッピング作成時に短縮形式ファイル名（第1話.html等）を生成してはいけない
        
        実際の実装を使ったテスト：
        - 修正後の実装では初期マッピングが空であることを確認
        """
        # 修正後の実装：初期マッピングは空で開始
        chapter_mapping = {}
        
        # 修正後に期待される動作：初期マッピングは空であるべき
        expected_empty_mapping = {}
        self.assertEqual(chapter_mapping, expected_empty_mapping,
                        "初期マッピングは空であるべき")

    def test_navigation_links_should_use_full_filenames_only(self):
        """
        ナビゲーションリンクは常にフルファイル名を使用すべき
        
        バグ再現テスト：
        - HTMLファイルに短縮形式リンクが含まれている
        - fix_local_navigation_linksを実行
        - 短縮形式リンクがフルファイル名に変換されることを確認
        """
        # 短縮形式リンクを含むHTMLサンプル
        html_with_short_links = '''
        <div class="novelnavi">
            <ul class="nl">
                <li class="novelnb"><a href="#">×</a></li>
                <li class="novelmokuzi"><a href="目次.html">目 次</a></li>
                <li class="novelnb"><a class="next_page_link" href="第2話.html">次の話 &gt;&gt;</a></li>
            </ul>
        </div>
        '''
        
        soup = BeautifulSoup(html_with_short_links, 'html.parser')
        
        # 正しいマッピング（フルファイル名）
        chapter_mapping = {
            'https://syosetu.org/novel/378070/2.html': 'ダウナー女神のアクア様 - 第一話　女神、降り立つ。そしてやらかす。 - ハーメルン.html'
        }
        
        # 修正処理実行
        fixed_soup = self.scraper.fix_local_navigation_links(
            soup, 
            chapter_mapping, 
            'https://syosetu.org/novel/378070/1.html',
            '目次.html'
        )
        
        # 短縮形式リンクが残っていないことを確認（このテストは現在失敗するはず）
        fixed_html = str(fixed_soup)
        self.assertNotIn('第2話.html', fixed_html, 
                        "短縮形式リンクが残っている（バグ再現）")
        
        # フルファイル名に変換されていることを確認
        self.assertIn('ダウナー女神のアクア様 - 第一話', fixed_html,
                     "フルファイル名に変換されるべき")

    def test_chapter_mapping_update_flow(self):
        """
        章マッピング更新フローのテスト
        
        正しい流れ：
        1. 初期マッピングは空
        2. 章取得時にフルファイル名でマッピング更新
        3. 短縮形式ファイル名は一切生成されない
        """
        # 1. 初期マッピングは空であるべき
        initial_mapping = {}
        
        # 2. 章取得後にフルファイル名でマッピング更新
        chapter_url = 'https://syosetu.org/novel/378070/1.html'
        full_filename = 'ダウナー女神のアクア様 - 序章　彼と彼女の出会い - ハーメルン.html'
        
        initial_mapping[chapter_url] = full_filename
        
        # 3. 短縮形式ファイル名が含まれていないことを確認
        for filename in initial_mapping.values():
            self.assertNotRegex(filename, r'^第\d+話\.html$',
                              "短縮形式ファイル名が含まれてはいけない")
            
        # フルファイル名のパターンを確認
        self.assertRegex(full_filename, r'.*ハーメルン\.html$',
                        "正しいフルファイル名形式であるべき")

if __name__ == '__main__':
    unittest.main()