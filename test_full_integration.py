"""
Phase 3 完全統合テスト
新しい解析モジュールと既存モジュールの統合確認
"""

import pytest
from bs4 import BeautifulSoup
from unittest.mock import Mock, patch

from hameln_scraper.core.config import HamelnConfig
from hameln_scraper.core.scraper import HamelnScraper
from hameln_scraper.network.client import HamelnNetworkClient
from hameln_scraper.parsing.content_extractor import ContentExtractor
from hameln_scraper.parsing.url_extractor import UrlExtractor
from hameln_scraper.parsing.validator import PageValidator


class TestFullIntegration:
    """完全統合テストクラス"""

    def test_all_modules_initialization(self):
        """全モジュールの初期化テスト"""
        config = HamelnConfig()
        assert config is not None
        
        network_client = HamelnNetworkClient(config)
        assert network_client is not None
        
        content_extractor = ContentExtractor()
        assert content_extractor is not None
        
        url_extractor = UrlExtractor()
        assert url_extractor is not None
        
        validator = PageValidator()
        assert validator is not None
        
        scraper = HamelnScraper(config)
        assert scraper is not None

    def test_parsing_workflow_integration(self):
        """解析ワークフロー統合テスト"""
        # モックHTMLページ（ハーメルンページ形式）
        hameln_html = """
        <html>
        <head>
            <title>統合テスト小説 - ハーメルン</title>
        </head>
        <body>
            <h1>統合テスト小説</h1>
            <div class="novel-author">
                <a href="/user/12345">統合テスト作者</a>
            </div>
            <div id="honbun">
                これは統合テストの本文です。全てのモジュールが正常に連携して
                動作することを確認するためのテストコンテンツです。
                十分な長さを持ち、小説らしい文章構造になっています。
            </div>
            <nav>
                <a href="/novel/999/info/">小説情報</a>
                <a href="/novel/999/comments/">感想</a>
                <a href="/novel/999/1/">第1章</a>
                <a href="/novel/999/2/">第2章</a>
            </nav>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(hameln_html, 'html.parser')
        base_url = "https://syosetu.org/novel/999/"
        
        # 1. ページ検証
        validator = PageValidator()
        assert validator.validate_page(soup, base_url) is True
        
        # 2. コンテンツ抽出
        content_extractor = ContentExtractor()
        
        # 小説情報抽出
        novel_info = content_extractor.extract_novel_info(soup)
        assert novel_info['title'] == "統合テスト小説"
        assert novel_info['author'] == "統合テスト作者"
        
        # 本文抽出
        content = content_extractor.extract_chapter_content(soup, base_url)
        assert "これは統合テストの本文です" in content
        assert len(content) > 50
        
        # 3. URL抽出
        url_extractor = UrlExtractor()
        
        info_url = url_extractor.extract_novel_info_url(soup)
        comments_url = url_extractor.extract_comments_url(soup)
        chapter_links = url_extractor.get_chapter_links(soup, base_url)
        
        assert info_url == "/novel/999/info/"
        assert comments_url == "/novel/999/comments/"
        assert len(chapter_links) >= 2  # 少なくとも第1章、第2章

    def test_scraper_with_parsing_modules(self):
        """メインスクレイパーと解析モジュールの統合テスト"""
        config = HamelnConfig()
        scraper = HamelnScraper(config)
        
        # 解析モジュールがスクレイパーからアクセス可能か確認
        assert hasattr(scraper, 'config')
        assert scraper.config is not None
        
        # ネットワーククライアントとの統合
        assert hasattr(scraper, 'network_client')
        assert scraper.network_client is not None

    @patch('hameln_scraper.network.client.HamelnNetworkClient.get_page')
    def test_end_to_end_parsing_simulation(self, mock_get_page):
        """エンドツーエンド解析シミュレーション"""
        # モックレスポンス設定
        mock_html = """
        <html>
        <head><title>E2Eテスト小説 - ハーメルン</title></head>
        <body>
            <h1>E2Eテスト小説</h1>
            <div class="novel-author"><a href="/user/555">E2E作者</a></div>
            <div id="honbun">
                エンドツーエンドテストの本文です。実際のワークフローで
                全てのモジュールが協調して動作することを確認します。
            </div>
        </body>
        </html>
        """
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = mock_html
        mock_response.headers = {'content-type': 'text/html'}
        mock_get_page.return_value = mock_response
        
        # 統合ワークフロー実行
        config = HamelnConfig()
        scraper = HamelnScraper(config)
        
        # ページ取得（モック）
        response = scraper.network_client.get_page("https://syosetu.org/novel/555/")
        assert response.status_code == 200
        
        # 解析処理
        soup = BeautifulSoup(response.text, 'html.parser')
        
        validator = PageValidator()
        content_extractor = ContentExtractor()
        url_extractor = UrlExtractor()
        
        # 統合解析実行
        assert validator.validate_page(soup, "https://syosetu.org/novel/555/")
        
        novel_info = content_extractor.extract_novel_info(soup)
        assert novel_info['title'] == "E2Eテスト小説"
        assert novel_info['author'] == "E2E作者"
        
        content = content_extractor.extract_chapter_content(soup, "https://syosetu.org/novel/555/")
        assert "エンドツーエンドテストの本文です" in content

    def test_error_handling_integration(self):
        """エラーハンドリング統合テスト"""
        # 不正なHTMLでの動作確認
        invalid_html = "<html><body></body></html>"
        soup = BeautifulSoup(invalid_html, 'html.parser')
        
        validator = PageValidator()
        content_extractor = ContentExtractor()
        url_extractor = UrlExtractor()
        
        # 各モジュールがエラーを適切に処理するか確認
        assert validator.validate_page(soup, "https://example.com") is False
        
        novel_info = content_extractor.extract_novel_info(soup)
        assert novel_info['title'] == "不明なタイトル"
        assert novel_info['author'] == "不明な作者"
        
        content = content_extractor.extract_chapter_content(soup, "https://example.com")
        assert content == ""
        
        info_url = url_extractor.extract_novel_info_url(soup)
        comments_url = url_extractor.extract_comments_url(soup)
        chapter_links = url_extractor.get_chapter_links(soup, "https://example.com")
        
        assert info_url is None
        assert comments_url is None
        assert len(chapter_links) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])