#!/usr/bin/env python3
"""
Phase 3: HTML解析モジュールのTDDテストスイート
元ファイルの解析ロジックを抽出してテスト化
"""

import pytest
import sys
import os
from bs4 import BeautifulSoup
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class TestContentExtractor:
    """コンテンツ抽出モジュールのテスト"""
    
    def test_extract_chapter_content_with_honbun_id(self):
        """div#honbun を持つハーメルン2024年構造での本文抽出テスト"""
        html_content = """
        <html>
        <body>
            <div id="header">ヘッダー</div>
            <div id="honbun">
                これは小説の本文です。とても長い内容で、
                物語の重要な部分が含まれています。
                登場人物の心情や風景描写など、
                小説らしい文章が書かれています。
            </div>
            <div id="footer">フッター</div>
        </body>
        </html>
        """
        
        from hameln_scraper.parsing.content_extractor import ContentExtractor
        
        soup = BeautifulSoup(html_content, 'html.parser')
        extractor = ContentExtractor()
        
        # 現在の基本実装では失敗するはず（TDD: まずテスト失敗を確認）
        result = extractor.extract_chapter_content(soup, "https://test.example.com")
        
        # 期待値：本文が正しく抽出される（正規化は実装側で行われる）
        expected_content = "これは小説の本文です。とても長い内容で、 物語の重要な部分が含まれています。 登場人物の心情や風景描写など、 小説らしい文章が書かれています。"
        assert result == expected_content
    
    def test_extract_chapter_content_with_section_classes(self):
        """section1-9 クラスでの本文抽出テスト"""
        html_content = """
        <html>
        <body>
            <div class="section1">タイトル部分</div>
            <div class="section3">
                これは section3 の本文です。
                ハーメルンの古い構造での小説本文。
                十分な長さを持つコンテンツです。
            </div>
            <div class="section9">その他の情報</div>
        </body>
        </html>
        """
        
        from hameln_scraper.parsing.content_extractor import ContentExtractor
        
        soup = BeautifulSoup(html_content, 'html.parser')
        extractor = ContentExtractor()
        
        result = extractor.extract_chapter_content(soup, "https://test.example.com")
        
        # section3 の内容が抽出されるべき（正規化は実装側で行われる）
        expected_content = "これは section3 の本文です。 ハーメルンの古い構造での小説本文。 十分な長さを持つコンテンツです。"
        assert result == expected_content
    
    def test_extract_chapter_content_minimum_length_check(self):
        """最小文字数チェックのテスト"""
        html_content = """
        <html>
        <body>
            <div id="honbun">短い</div>
            <div class="section3">
                これは十分な長さを持つ本文コンテンツです。
                最小長チェックをパスするために必要な文字数を含んでいます。
            </div>
        </body>
        </html>
        """
        
        from hameln_scraper.parsing.content_extractor import ContentExtractor
        
        soup = BeautifulSoup(html_content, 'html.parser')
        extractor = ContentExtractor()
        
        result = extractor.extract_chapter_content(soup, "https://test.example.com")
        
        # 短いコンテンツは無視され、長いコンテンツが選択されるべき
        assert "十分な長さを持つ本文コンテンツ" in result
        assert "短い" not in result
    
    def test_extract_novel_info_title_extraction(self):
        """小説情報からタイトル抽出のテスト"""
        html_content = """
        <html>
        <head>
            <title>テスト小説タイトル - ハーメルン</title>
        </head>
        <body>
            <h1>テスト小説タイトル</h1>
            <div class="section1">タイトル情報エリア</div>
        </body>
        </html>
        """
        
        from hameln_scraper.parsing.content_extractor import ContentExtractor
        
        soup = BeautifulSoup(html_content, 'html.parser')
        extractor = ContentExtractor()
        
        # 新機能: extract_novel_info メソッドをテスト（まだ未実装）
        result = extractor.extract_novel_info(soup)
        
        # 期待値：タイトルが正しく抽出される
        assert result['title'] == "テスト小説タイトル"
        # ハーメルン特有の " - ハーメルン" が除去されることを確認
        assert " - ハーメルン" not in result['title']
    
    def test_extract_novel_info_author_extraction(self):
        """小説情報から作者抽出のテスト"""
        html_content = """
        <html>
        <body>
            <div class="novel-author">
                <a href="/user/12345">テスト作者</a>
            </div>
            <div class="p-novel-author">作者情報</div>
        </body>
        </html>
        """
        
        from hameln_scraper.parsing.content_extractor import ContentExtractor
        
        soup = BeautifulSoup(html_content, 'html.parser')
        extractor = ContentExtractor()
        
        result = extractor.extract_novel_info(soup)
        
        # 期待値：作者が正しく抽出される
        assert result['author'] == "テスト作者"


class TestUrlExtractor:
    """URL抽出モジュールのテスト"""
    
    def test_extract_chapter_links_basic(self):
        """基本的な章リンク抽出テスト"""
        html_content = """
        <html>
        <body>
            <div class="chapter-list">
                <a href="/novel/123456/1/">第1章</a>
                <a href="/novel/123456/2/">第2章</a>
                <a href="/novel/123456/3/">第3章</a>
            </div>
        </body>
        </html>
        """
        
        from hameln_scraper.parsing.url_extractor import UrlExtractor
        
        soup = BeautifulSoup(html_content, 'html.parser')
        extractor = UrlExtractor()
        
        # 新機能: get_chapter_links メソッドをテスト（まだ未実装）
        result = extractor.get_chapter_links(soup, "https://syosetu.org/novel/123456/")
        
        # 期待値：3つの章リンクが抽出される
        assert len(result) == 3
        assert "/novel/123456/1/" in result[0]['url']
        assert "/novel/123456/2/" in result[1]['url']
        assert "/novel/123456/3/" in result[2]['url']
    
    def test_extract_novel_info_url(self):
        """小説情報URL抽出テスト"""
        html_content = """
        <html>
        <body>
            <nav>
                <a href="/novel/123456/">目次</a>
                <a href="/novel/123456/info/">小説情報</a>
                <a href="/novel/123456/comments/">感想</a>
            </nav>
        </body>
        </html>
        """
        
        from hameln_scraper.parsing.url_extractor import UrlExtractor
        
        soup = BeautifulSoup(html_content, 'html.parser')
        extractor = UrlExtractor()
        
        result = extractor.extract_novel_info_url(soup)
        
        # 期待値：小説情報URLが抽出される
        assert result == "/novel/123456/info/"
    
    def test_extract_comments_url(self):
        """感想URL抽出テスト"""
        html_content = """
        <html>
        <body>
            <nav>
                <a href="/novel/123456/">目次</a>
                <a href="/novel/123456/info/">小説情報</a>
                <a href="/novel/123456/comments/">感想</a>
            </nav>
        </body>
        </html>
        """
        
        from hameln_scraper.parsing.url_extractor import UrlExtractor
        
        soup = BeautifulSoup(html_content, 'html.parser')
        extractor = UrlExtractor()
        
        result = extractor.extract_comments_url(soup)
        
        # 期待値：感想URLが抽出される
        assert result == "/novel/123456/comments/"


class TestPageValidator:
    """ページ検証モジュールのテスト"""
    
    def test_validate_page_basic_structure(self):
        """基本的なページ構造検証テスト"""
        html_content = """
        <html>
        <body>
            <div>十分なコンテンツを持つページです。これは小説のページで、適切な構造を持っています。読者が楽しめる内容となっています。</div>
        </body>
        </html>
        """
        
        from hameln_scraper.parsing.validator import PageValidator
        
        soup = BeautifulSoup(html_content, 'html.parser')
        validator = PageValidator()
        
        result = validator.validate_page(soup, "https://test.example.com")
        
        # 期待値：有効なページとして判定される
        assert result is True
    
    def test_validate_page_error_detection(self):
        """エラーページ検出テスト"""
        html_content = """
        <html>
        <head><title>404 - ページが見つかりませんでした</title></head>
        <body>
            <div>ページが見つかりませんでした</div>
        </body>
        </html>
        """
        
        from hameln_scraper.parsing.validator import PageValidator
        
        soup = BeautifulSoup(html_content, 'html.parser')
        validator = PageValidator()
        
        result = validator.validate_page(soup, "https://test.example.com")
        
        # 期待値：エラーページとして検出される
        assert result is False
    
    def test_is_likely_novel_content(self):
        """小説コンテンツ判定テスト"""
        from hameln_scraper.parsing.validator import PageValidator
        
        validator = PageValidator()
        
        # 小説らしいテキスト
        novel_text = "彼は窓の外を見つめていた。そして、その時ふと思い出したのである。"
        assert validator.is_likely_novel_content(novel_text) is True
        
        # 小説らしくないテキスト
        non_novel_text = "ユーザー登録 ログイン パスワード メールアドレス"
        assert validator.is_likely_novel_content(non_novel_text) is False
        
        # 短すぎるテキスト
        short_text = "短い"
        assert validator.is_likely_novel_content(short_text) is False


class TestIntegrationParsing:
    """解析モジュール統合テスト"""
    
    def test_full_parsing_workflow(self):
        """完全な解析ワークフローテスト"""
        # ハーメルンページを模擬したHTML
        hameln_page = """
        <html>
        <head>
            <title>テスト小説 - ハーメルン</title>
        </head>
        <body>
            <nav>
                <a href="/novel/123456/info/">小説情報</a>
                <a href="/novel/123456/comments/">感想</a>
            </nav>
            <h1>テスト小説</h1>
            <div class="novel-author">
                <a href="/user/789">テスト作者</a>
            </div>
            <div id="honbun">
                これは長い小説の本文です。物語の展開や登場人物の描写、
                心情の変化などが詳細に書かれています。読者が楽しめる
                エンターテイメント性の高い内容となっています。
            </div>
            <div class="chapter-nav">
                <a href="/novel/123456/1/">第1章</a>
                <a href="/novel/123456/2/">第2章</a>
            </div>
        </body>
        </html>
        """
        
        from hameln_scraper.parsing.content_extractor import ContentExtractor
        from hameln_scraper.parsing.url_extractor import UrlExtractor
        from hameln_scraper.parsing.validator import PageValidator
        
        soup = BeautifulSoup(hameln_page, 'html.parser')
        
        # 各モジュールが連携して動作することを確認
        validator = PageValidator()
        content_extractor = ContentExtractor()
        url_extractor = UrlExtractor()
        
        # 1. ページ検証
        assert validator.validate_page(soup, "https://syosetu.org/novel/123456/") is True
        
        # 2. 小説情報抽出
        novel_info = content_extractor.extract_novel_info(soup)
        assert novel_info['title'] == "テスト小説"
        assert novel_info['author'] == "テスト作者"
        
        # 3. 本文抽出
        content = content_extractor.extract_chapter_content(soup, "https://syosetu.org/novel/123456/1/")
        assert "これは長い小説の本文です" in content
        
        # 4. URL抽出
        info_url = url_extractor.extract_novel_info_url(soup)
        comments_url = url_extractor.extract_comments_url(soup)
        chapter_links = url_extractor.get_chapter_links(soup, "https://syosetu.org/novel/123456/")
        
        assert info_url == "/novel/123456/info/"
        assert comments_url == "/novel/123456/comments/"
        # URL抽出器は小説情報、感想、第1章、第2章の4つのリンクを発見する
        assert len(chapter_links) == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])