#!/usr/bin/env python3
"""
統合テスト集約版
旧ファイル統合:
- test_integration_critical_issues.py
- test_integration_success.py
- test_full_integration.py
- test_phase4_integration.py
- test_modular_scraper_integration.py
- test_real_hameln_integration.py
"""

import pytest
import sys
import os
import tempfile
import shutil
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 基本インポートテスト用
try:
    from hameln_scraper_final import HamelnFinalScraper
    HAS_LEGACY_SCRAPER = True
except ImportError:
    HAS_LEGACY_SCRAPER = False

try:
    from hameln_scraper.core.scraper import HamelnScraper
    from hameln_scraper.core.config import HamelnConfig
    HAS_MODULAR_SCRAPER = True
except ImportError:
    HAS_MODULAR_SCRAPER = False


class TestCriticalIssueResolution:
    """統合時のクリティカル問題解決テスト（旧：test_integration_critical_issues）"""
    
    def test_network_client_availability(self):
        """ネットワーククライアントの可用性確認"""
        if HAS_MODULAR_SCRAPER:
            from hameln_scraper.network.client import HamelnNetworkClient
            client = HamelnNetworkClient()
            assert client is not None
            assert hasattr(client, 'get_page')
            client.close()
    
    def test_config_class_availability(self):
        """設定クラスの可用性確認"""
        if HAS_MODULAR_SCRAPER:
            config = HamelnConfig()
            assert config is not None
            assert hasattr(config, 'base_url')
            assert hasattr(config, 'user_agents')


class TestIntegrationSuccess:
    """修正後の統合成功確認（旧：test_integration_success）"""
    
    @pytest.mark.skipif(not HAS_LEGACY_SCRAPER, reason="HamelnFinalScraper not available")
    def test_legacy_scraper_integration(self):
        """レガシースクレイパーの統合確認"""
        scraper = HamelnFinalScraper()
        assert scraper is not None
        assert hasattr(scraper, 'base_url')
        assert hasattr(scraper, 'debug_mode')
        if hasattr(scraper, 'close'):
            scraper.close()
    
    @pytest.mark.skipif(not HAS_MODULAR_SCRAPER, reason="Modular scraper not available")  
    def test_modular_scraper_integration(self):
        """モジュラースクレイパーの統合確認"""
        config = HamelnConfig()
        scraper = HamelnScraper(config)
        assert scraper is not None
        if hasattr(scraper, 'close'):
            scraper.close()


class TestFullIntegrationWorkflow:
    """フル統合ワークフローテスト（旧：test_full_integration）"""
    
    @pytest.mark.skipif(not HAS_LEGACY_SCRAPER, reason="HamelnFinalScraper not available")
    def test_basic_scraping_workflow(self):
        """基本的なスクレイピングワークフローテスト"""
        scraper = HamelnFinalScraper()
        temp_dir = tempfile.mkdtemp()
        
        try:
            # 基本初期化確認
            assert scraper.base_url == "https://syosetu.org"
            assert isinstance(scraper.debug_mode, bool)
            
            # User-Agentローテーション機能テスト
            if hasattr(scraper, 'user_agents') and hasattr(scraper, 'rotate_user_agent'):
                initial_ua_index = getattr(scraper, 'current_ua_index', 0)
                scraper.rotate_user_agent()
                after_ua_index = getattr(scraper, 'current_ua_index', 0)
                assert after_ua_index != initial_ua_index or len(scraper.user_agents) == 1
            
        finally:
            shutil.rmtree(temp_dir)
            if hasattr(scraper, 'close'):
                scraper.close()


class TestModularIntegration:
    """モジュラー統合テスト（旧：test_modular_scraper_integration, test_phase4_integration）"""
    
    @pytest.mark.skipif(not HAS_MODULAR_SCRAPER, reason="Modular components not available")
    def test_phase_modules_integration(self):
        """各Phase モジュールの統合確認"""
        # Phase 1: Config
        config = HamelnConfig() 
        assert config.validate_config()
        
        # Phase 2: Network (availability check)
        try:
            from hameln_scraper.network.client import HamelnNetworkClient
            from hameln_scraper.network.user_agent import UserAgentRotator
            network_available = True
        except ImportError:
            network_available = False
        
        # Phase 3: Parsing (availability check)
        try:
            from hameln_scraper.parsing.content_extractor import ContentExtractor
            from hameln_scraper.parsing.url_extractor import UrlExtractor  
            parsing_available = True
        except ImportError:
            parsing_available = False
        
        # Phase 4: Resources (availability check)
        try:
            from hameln_scraper.resources.downloader import ResourceDownloader
            from hameln_scraper.resources.processor import ResourceProcessor
            resources_available = True
        except ImportError:
            resources_available = False
        
        # 統合確認
        if network_available and parsing_available and resources_available:
            main_scraper = HamelnScraper(config)
            assert main_scraper is not None


class TestRealHamelnCompatibility:
    """実ハーメルン互換性テスト（旧：test_real_hameln_integration）"""
    
    @pytest.mark.skipif(not HAS_LEGACY_SCRAPER, reason="HamelnFinalScraper not available")
    def test_hameln_url_compatibility(self):
        """ハーメルンURL互換性テスト"""
        scraper = HamelnFinalScraper()
        
        # 基本URL構造の確認
        assert scraper.base_url in ["https://syosetu.org", "http://syosetu.org"]
        
        # Cloudflareバイパス機能の存在確認
        assert hasattr(scraper, 'cloudscraper') or hasattr(scraper, 'session')
        
        if hasattr(scraper, 'close'):
            scraper.close()
    
    @pytest.mark.skipif(not HAS_LEGACY_SCRAPER, reason="HamelnFinalScraper not available")
    def test_html_parsing_structure(self):
        """HTML解析構造の確認"""
        scraper = HamelnFinalScraper()
        
        # HTML解析メソッドの存在確認
        html_methods = ['extract_chapter_content', 'extract_novel_info', 'get_chapter_links']
        existing_methods = [method for method in html_methods if hasattr(scraper, method)]
        
        # 少なくとも1つのHTML解析メソッドが存在することを確認
        assert len(existing_methods) > 0, f"HTML解析メソッドが見つかりません。確認されたメソッド: {existing_methods}"
        
        if hasattr(scraper, 'close'):
            scraper.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])