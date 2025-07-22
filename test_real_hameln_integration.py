"""
実ハーメルン環境統合テスト
Cloudflare認証・bot検知回避・実HTML処理の検証
"""

import pytest
import tempfile
import os
from hameln_scraper.core.scraper import HamelnModularScraper
from hameln_scraper.core.config import HamelnConfig
from hameln_scraper.network.client import HamelnNetworkClient
from hameln_scraper.resources.saver import PageSaver
from hameln_scraper.resources.processor import ResourceProcessor


class TestRealHamelnIntegration:
    """実ハーメルン環境での統合テスト"""

    def test_cloudscraper_initialization(self):
        """CloudScraper初期化と基本機能テスト"""
        try:
            config = HamelnConfig()
            client = HamelnNetworkClient()
            
            # CloudScraper正常初期化確認
            assert client.cloudscraper is not None
            assert hasattr(client, 'ua_rotator')
            
            print("✅ CloudScraper初期化成功")
            
        except Exception as e:
            pytest.fail(f"CloudScraper初期化失敗: {e}")

    def test_hameln_scraper_initialization(self):
        """ハーメルンスクレイパー完全初期化テスト"""
        try:
            scraper = HamelnModularScraper()
            
            # 各コンポーネントの初期化確認
            assert scraper.config is not None
            assert scraper.network_client is not None
            assert scraper.content_extractor is not None
            assert scraper.resource_processor is not None
            
            print("✅ ハーメルンスクレイパー初期化成功")
            
        except Exception as e:
            pytest.fail(f"スクレイパー初期化失敗: {e}")

    def test_resource_processing_workflow(self):
        """リソース処理ワークフロー統合テスト"""
        try:
            config = HamelnConfig()
            client = HamelnNetworkClient()
            processor = ResourceProcessor(config, client)
            saver = PageSaver(processor)
            
            # 実際のハーメルン構造を模擬したHTML
            real_hameln_html = '''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>テスト小説 第1章 - ハーメルン</title>
    <link rel="stylesheet" href="/css/novel.css">
    <script src="/js/novel.js"></script>
</head>
<body>
    <div id="header">
        <h1><a href="/">ハーメルン</a></h1>
    </div>
    <div id="honbun" class="section1">
        <h2>第1章：始まりの物語</h2>
        <p>これはテスト用の小説です。</p>
        <p>主人公は新たな冒険に旅立った。</p>
    </div>
    <div class="novel-image">
        <img src="/images/chapter1_illustration.jpg" alt="第1章挿絵">
    </div>
</body>
</html>'''
            
            with tempfile.TemporaryDirectory() as temp_dir:
                # 完全保存テスト（エラーハンドリング確認）
                result = saver.save_complete_page(
                    html_content=real_hameln_html,
                    output_dir=temp_dir,
                    filename='test_real_hameln.html',
                    original_url='https://syosetu.org/novel/999999/1/',
                    title='テスト小説 第1章'
                )
                
                # 基本保存成功確認
                assert result['success'] is True
                assert os.path.exists(result['saved_path'])
                
                # 保存ファイル内容確認
                with open(result['saved_path'], 'r', encoding='utf-8-sig') as f:
                    saved_content = f.read()
                
                # ハーメルン特有要素の保持確認
                assert 'ハーメルン' in saved_content
                assert 'honbun' in saved_content
                assert 'section1' in saved_content
                assert 'テスト用の小説' in saved_content
                
                # リソースパス変換確認
                assert './resources/' in saved_content
                
                # メタ情報追加確認
                assert 'save-date' in saved_content
                assert 'source-url' in saved_content
                assert 'syosetu.org/novel/999999/1' in saved_content
                
                print("✅ 実ハーメルン構造での保存処理成功")
                print(f"保存ファイル: {result['saved_path']}")
                print(f"ファイルサイズ: {result['file_size']} bytes")
                
        except Exception as e:
            pytest.fail(f"リソース処理ワークフロー失敗: {e}")

    def test_error_handling_robustness(self):
        """エラーハンドリング堅牢性テスト"""
        try:
            config = HamelnConfig()
            client = HamelnNetworkClient()
            processor = ResourceProcessor(config, client)
            
            # 不正なリソースURLでのエラーハンドリング確認
            from bs4 import BeautifulSoup
            html_with_invalid_resources = '''
            <html>
            <head>
                <link rel="stylesheet" href="/invalid/path/style.css">
            </head>
            <body>
                <img src="/invalid/path/image.jpg">
            </body>
            </html>
            '''
            
            soup = BeautifulSoup(html_with_invalid_resources, 'html.parser')
            
            with tempfile.TemporaryDirectory() as temp_dir:
                # エラーが発生してもクラッシュしないことを確認
                result_soup = processor.process_html_resources(soup, temp_dir)
                
                # 結果が返されることを確認（エラーハンドリング成功）
                assert result_soup is not None
                assert str(result_soup)  # 文字列化可能
                
                print("✅ エラーハンドリング堅牢性確認成功")
                
        except Exception as e:
            pytest.fail(f"エラーハンドリングテスト失敗: {e}")

    def test_hameln_specific_features(self):
        """ハーメルン特化機能テスト"""
        try:
            scraper = HamelnModularScraper()
            
            # ハーメルン特化設定の確認
            assert scraper.config.base_url == "https://syosetu.org"
            assert scraper.config.chapter_wait_time >= 3  # 適切な待機時間
            
            # User-Agentローテーション確認
            ua1 = scraper.network_client.ua_rotator.get_current_user_agent()
            scraper.network_client.ua_rotator.rotate_user_agent()
            ua2 = scraper.network_client.ua_rotator.get_current_user_agent()
            
            # User-Agentが取得できることを確認
            assert ua1 is not None
            assert len(ua1) > 0
            assert ua2 is not None
            assert len(ua2) > 0
            
            print("✅ ハーメルン特化機能確認成功")
            print(f"User-Agent例: {ua1[:50]}...")
            
        except Exception as e:
            pytest.fail(f"ハーメルン特化機能テスト失敗: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])