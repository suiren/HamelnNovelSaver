#!/usr/bin/env python3
"""
統合成功テスト：修正後の統合動作を確認
"""

import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class TestIntegrationSuccess:
    """修正後の統合成功をテスト"""
    
    def test_scraper_integration_now_works(self):
        """修正後のscraper.pyが正常に統合されることを確認"""
        # scraper.py のインポートが成功することをテスト
        from hameln_scraper.core.scraper import HamelnScraper
        
        # インスタンス化テスト
        scraper = HamelnScraper()
        assert scraper is not None
        assert hasattr(scraper, 'scrape_novel')
        assert hasattr(scraper, 'close')
        
        scraper.close()
    
    def test_correct_imports_after_fix(self):
        """修正後に正しいクラスがインポートされることを確認"""
        # scraper.py の内容確認
        with open('hameln_scraper/core/scraper.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 正しいインポート文が存在することを確認
        assert 'from .config import HamelnConfig' in content
        assert 'from ..network.client import HamelnNetworkClient' in content
        
        # 実際にこれらのクラスがインポートできることを確認
        from hameln_scraper.core.config import HamelnConfig
        from hameln_scraper.network.client import HamelnNetworkClient
        
        # インスタンス化テスト
        config = HamelnConfig()
        client = HamelnNetworkClient()
        
        assert config.validate_config() is True
        assert client.get_status()['cloudscraper_initialized'] is True
        
        client.close()
    
    def test_full_integration_workflow(self):
        """完全な統合ワークフローをテスト"""
        from hameln_scraper.core.scraper import HamelnScraper
        from hameln_scraper.core.config import HamelnConfig
        
        # カスタム設定でスクレイパー作成
        config = HamelnConfig()
        scraper = HamelnScraper(config)
        
        # スクレイパーの基本動作確認
        assert scraper.network_client is not None
        assert scraper.validator is not None
        assert scraper.config is not None
        
        # ネットワーククライアントの状態確認
        status = scraper.network_client.get_status()
        assert status['cloudscraper_initialized'] is True
        assert status['user_agent_count'] == 5
        
        scraper.close()
    
    def test_all_modules_can_be_imported(self):
        """すべてのモジュールが正常にインポートできることを確認"""
        from hameln_scraper.core.scraper import HamelnScraper
        from hameln_scraper.core.config import HamelnConfig
        from hameln_scraper.network.client import HamelnNetworkClient
        from hameln_scraper.network.user_agent import UserAgentRotator
        from hameln_scraper.network.compression import ResponseDecompressor
        from hameln_scraper.parsing.validator import PageValidator
        from hameln_scraper.parsing.content_extractor import ContentExtractor
        from hameln_scraper.parsing.url_extractor import UrlExtractor
        
        # すべてのクラスがインスタンス化可能
        scraper = HamelnScraper()
        config = HamelnConfig()
        client = HamelnNetworkClient()
        ua_rotator = UserAgentRotator()
        decompressor = ResponseDecompressor()
        validator = PageValidator()
        content_extractor = ContentExtractor()
        url_extractor = UrlExtractor()
        
        # 基本機能テスト
        assert config.validate_config() is True
        assert client.get_status()['cloudscraper_initialized'] is True
        assert len(ua_rotator.get_current_user_agent()) > 0
        assert hasattr(decompressor, 'decompress_response')
        assert hasattr(validator, 'validate_page')
        assert hasattr(content_extractor, 'extract_content')
        assert hasattr(url_extractor, 'extract_urls')
        
        # クリーンアップ
        scraper.close()
        client.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])