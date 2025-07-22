"""
実ハーメルンURL動作確認テスト
注意：このテストは実際のハーメルンサイトにアクセスします
"""

import pytest
import time
from bs4 import BeautifulSoup
from unittest.mock import patch

from hameln_scraper.core.config import HamelnConfig
from hameln_scraper.network.client import HamelnNetworkClient
from hameln_scraper.parsing.content_extractor import ContentExtractor
from hameln_scraper.parsing.url_extractor import UrlExtractor
from hameln_scraper.parsing.validator import PageValidator


class TestHamelnRealURL:
    """実ハーメルンURL動作テストクラス"""

    @pytest.fixture
    def hameln_modules(self):
        """ハーメルン関連モジュールのセットアップ"""
        config = HamelnConfig()
        config.delay_between_requests = 5  # 控えめなアクセス間隔
        
        return {
            'config': config,
            'network_client': HamelnNetworkClient(config),
            'content_extractor': ContentExtractor(),
            'url_extractor': UrlExtractor(),
            'validator': PageValidator()
        }

    @pytest.mark.skip(reason="実際のハーメルンアクセステスト - 手動実行用")
    def test_hameln_main_page_access(self, hameln_modules):
        """ハーメルンメインページアクセステスト"""
        network_client = hameln_modules['network_client']
        validator = hameln_modules['validator']
        
        try:
            # ハーメルンメインページにアクセス（最も安全）
            response = network_client.get_page("https://syosetu.org/")
            
            if response and response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # ページ検証
                is_valid = validator.validate_page(soup, "https://syosetu.org/")
                assert is_valid is True, "ハーメルンメインページが有効でない"
                
                # ハーメルンサイトの基本要素確認
                title = soup.find('title')
                assert title is not None, "titleタグが見つからない"
                assert 'ハーメルン' in title.get_text(), "ハーメルンサイトでない"
                
                print(f"✅ ハーメルンメインページアクセス成功")
                print(f"   - ステータス: {response.status_code}")
                print(f"   - タイトル: {title.get_text()[:50]}...")
                
            else:
                pytest.fail(f"ハーメルンメインページアクセス失敗: {response.status_code if response else 'No response'}")
                
        except Exception as e:
            pytest.fail(f"ハーメルンアクセス中にエラー: {e}")
        
        # アクセス間隔を守る
        time.sleep(5)

    def test_parsing_modules_with_mock_hameln_content(self, hameln_modules):
        """モックハーメルンコンテンツでの解析モジュールテスト"""
        # 実際のハーメルン構造を模擬したHTML
        mock_hameln_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>テスト小説 - ハーメルン</title>
            <meta charset="UTF-8">
        </head>
        <body>
            <header>
                <h1>ハーメルン</h1>
            </header>
            <main>
                <article>
                    <h1 class="novel-title">テスト小説</h1>
                    <div class="novel-author">
                        <a href="/user/123">テスト作者</a>
                    </div>
                    <div id="honbun">
                        これは実際のハーメルン構造を模擬したテスト本文です。
                        小説らしい内容で、十分な長さを持つコンテンツです。
                        章の内容や物語の展開が含まれています。
                    </div>
                    <nav class="chapter-nav">
                        <a href="/novel/123456/info/">小説情報</a>
                        <a href="/novel/123456/comments/">感想一覧</a>
                        <a href="/novel/123456/1/">第1話</a>
                        <a href="/novel/123456/2/">第2話</a>
                    </nav>
                </article>
            </main>
            <footer>
                <p>© ハーメルン</p>
            </footer>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(mock_hameln_html, 'html.parser')
        base_url = "https://syosetu.org/novel/123456/"
        
        validator = hameln_modules['validator']
        content_extractor = hameln_modules['content_extractor']
        url_extractor = hameln_modules['url_extractor']
        
        # 1. ページ検証
        is_valid = validator.validate_page(soup, base_url)
        assert is_valid is True, "ハーメルン模擬ページが無効"
        
        # 2. 小説情報抽出
        novel_info = content_extractor.extract_novel_info(soup)
        assert novel_info['title'] == "テスト小説", f"タイトル抽出失敗: {novel_info['title']}"
        assert novel_info['author'] == "テスト作者", f"作者抽出失敗: {novel_info['author']}"
        
        # 3. 本文抽出
        content = content_extractor.extract_chapter_content(soup, base_url)
        assert "これは実際のハーメルン構造を模擬した" in content, "本文抽出失敗"
        assert len(content) > 50, f"本文が短すぎる: {len(content)}文字"
        
        # 4. URL抽出
        info_url = url_extractor.extract_novel_info_url(soup)
        comments_url = url_extractor.extract_comments_url(soup)
        chapter_links = url_extractor.get_chapter_links(soup, base_url)
        
        assert info_url == "/novel/123456/info/", f"小説情報URL抽出失敗: {info_url}"
        assert comments_url == "/novel/123456/comments/", f"感想URL抽出失敗: {comments_url}"
        assert len(chapter_links) >= 2, f"章リンク抽出不足: {len(chapter_links)}個"
        
        print("✅ ハーメルン模擬コンテンツでの解析テスト成功")
        print(f"   - タイトル: {novel_info['title']}")
        print(f"   - 作者: {novel_info['author']}")
        print(f"   - 本文長: {len(content)}文字")
        print(f"   - 章リンク数: {len(chapter_links)}個")

    def test_network_client_configuration(self, hameln_modules):
        """ネットワーククライアント設定テスト"""
        network_client = hameln_modules['network_client']
        config = hameln_modules['config']
        
        # 設定値確認
        assert config.delay_between_requests >= 3, "アクセス間隔が短すぎる"
        assert hasattr(network_client, 'ua_rotator'), "User-Agentローテーター未設定"
        assert hasattr(network_client, 'decompressor'), "レスポンス圧縮解除器未設定"
        
        # User-Agent設定確認
        user_agent = network_client.ua_rotator.get_current_user_agent()
        assert user_agent is not None, "User-Agentが取得できない"
        assert len(user_agent) > 10, f"User-Agentが短すぎる: {user_agent}"
        
        print("✅ ネットワーククライアント設定確認完了")
        print(f"   - アクセス間隔: {config.delay_between_requests}秒")
        print(f"   - User-Agent: {user_agent[:50]}...")

    def test_error_recovery_simulation(self, hameln_modules):
        """エラー回復シミュレーションテスト"""
        content_extractor = hameln_modules['content_extractor']
        url_extractor = hameln_modules['url_extractor']
        validator = hameln_modules['validator']
        
        # 空のHTMLでのエラー回復テスト
        empty_soup = BeautifulSoup("<html></html>", 'html.parser')
        
        # 各モジュールが適切にエラーハンドリングするか確認
        assert validator.validate_page(empty_soup, "https://example.com") is False
        
        novel_info = content_extractor.extract_novel_info(empty_soup)
        assert novel_info['title'] == "不明なタイトル"
        assert novel_info['author'] == "不明な作者"
        
        content = content_extractor.extract_chapter_content(empty_soup, "https://example.com")
        assert content == ""
        
        chapter_links = url_extractor.get_chapter_links(empty_soup, "https://example.com")
        assert len(chapter_links) == 0
        
        print("✅ エラー回復シミュレーション成功")


if __name__ == "__main__":
    # 実際のハーメルンアクセステストはスキップ
    # 模擬テストのみ実行
    pytest.main([__file__, "-v", "-k", "not test_hameln_main_page_access"])