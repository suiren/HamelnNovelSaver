#!/usr/bin/env python3
"""
統合テスト：クリティカル問題の再現とテスト
発見された問題：
1. scraper.py が NetworkClient（存在しない）をインポート → 実際は HamelnNetworkClient
2. scraper.py が ScraperConfig（存在しない）をインポート → 実際は HamelnConfig
"""

import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class TestIntegrationCriticalIssues:
    """統合時のクリティカル問題をテスト"""
    
    def test_network_client_class_name_mismatch(self):
        """ネットワーククライアントのクラス名不整合を検証"""
        # 実際に存在するクラスを確認
        from hameln_scraper.network.client import HamelnNetworkClient
        
        # 存在するクラスの動作確認
        client = HamelnNetworkClient()
        assert client is not None
        assert hasattr(client, 'get_page')
        assert hasattr(client, 'get_status')
        client.close()
        
        # scraper.py がインポートしようとする NetworkClient は存在しない
        with pytest.raises(ImportError):
            from hameln_scraper.network.client import NetworkClient
    
    def test_config_class_name_mismatch(self):
        """設定クラスのクラス名不整合を検証"""
        # 実際に存在するクラスを確認
        from hameln_scraper.core.config import HamelnConfig
        
        # 存在するクラスの動作確認
        config = HamelnConfig()
        assert config is not None
        assert hasattr(config, 'validate_config')
        assert config.validate_config() is True
        
        # scraper.py がインポートしようとする ScraperConfig は存在しない
        with pytest.raises(ImportError):
            from hameln_scraper.core.config import ScraperConfig
    
    def test_scraper_integration_fails(self):
        """現在のscraper.pyが統合に失敗することを確認"""
        # scraper.py のインポートが失敗することをテスト
        with pytest.raises(ImportError):
            from hameln_scraper.core.scraper import HamelnScraper
    
    def test_correct_imports_work_independently(self):
        """正しいインポートが個別に動作することを確認"""
        # 個別モジュールは正常に動作する
        from hameln_scraper.network.client import HamelnNetworkClient
        from hameln_scraper.core.config import HamelnConfig
        from hameln_scraper.network.user_agent import UserAgentRotator
        from hameln_scraper.network.compression import ResponseDecompressor
        
        # 各クラスのインスタンス化テスト
        config = HamelnConfig()
        client = HamelnNetworkClient()
        ua_rotator = UserAgentRotator()
        decompressor = ResponseDecompressor()
        
        # 基本動作確認
        assert config.validate_config() is True
        assert client.get_status()['cloudscraper_initialized'] is True
        assert len(ua_rotator.get_current_user_agent()) > 0
        assert hasattr(decompressor, 'decompress_response')
        
        client.close()
    
    def test_scraper_imports_nonexistent_classes(self):
        """scraper.pyが存在しないクラスをインポートしていることを確認"""
        # scraper.py の内容確認
        try:
            with open('hameln_scraper/core/scraper.py', 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 問題のあるインポート文が存在することを確認
            assert 'from .config import ScraperConfig' in content
            assert 'from ..network.client import NetworkClient' in content
            
            # 実際にはこれらのクラスは存在しない
            with pytest.raises(ImportError):
                from hameln_scraper.core.config import ScraperConfig
                
            with pytest.raises(ImportError):
                from hameln_scraper.network.client import NetworkClient
                
        except FileNotFoundError:
            pytest.fail("scraper.py が見つかりません")


class TestModuleStructureAnalysis:
    """モジュール構造の分析テスト"""
    
    def test_network_module_structure(self):
        """ネットワークモジュールの構造確認"""
        import hameln_scraper.network
        
        # 期待されるクラスが存在することを確認
        assert hasattr(hameln_scraper.network, 'HamelnNetworkClient')
        assert hasattr(hameln_scraper.network, 'UserAgentRotator')
        assert hasattr(hameln_scraper.network, 'ResponseDecompressor')
    
    def test_core_module_structure(self):
        """コアモジュールの構造確認"""
        import hameln_scraper.core
        
        # 期待されるクラスが存在することを確認  
        assert hasattr(hameln_scraper.core, 'HamelnConfig')
        # HamelnScraper は現在インポートエラーで利用不可
    
    def test_parsing_module_structure(self):
        """解析モジュールの構造確認"""
        import hameln_scraper.parsing
        
        # 基本構造の確認
        assert hasattr(hameln_scraper.parsing, 'PageValidator')
        assert hasattr(hameln_scraper.parsing, 'ContentExtractor')
        assert hasattr(hameln_scraper.parsing, 'UrlExtractor')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])