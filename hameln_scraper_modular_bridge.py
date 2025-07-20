"""
ハーメルンスクレイパー互換ブリッジ
既存のhameln_scraper_final.pyと新しいモジュール構造の橋渡し

このファイルは段階的移行のための互換性レイヤーです。
既存のGUIアプリケーション（hameln_gui.py）が新しいモジュール構造を
透明に使用できるようにします。
"""

from hameln_scraper.core.scraper import HamelnModularScraper
from typing import Dict, Optional, Any, Callable


class HamelnFinalScraper(HamelnModularScraper):
    """
    hameln_scraper_final.py完全互換クラス
    
    既存のGUIアプリケーション用の完全後方互換性を提供します。
    内部的には新しいHamelnModularScraperを使用していますが、
    外部インターフェースは従来のHamelnFinalScraperと同一です。
    """
    
    def __init__(self, base_url: str = "https://syosetu.org"):
        """hameln_scraper_final.pyと同じ初期化インターフェース"""
        super().__init__(base_url)
        
        # 追加の互換性プロパティ
        self.base_url = base_url
        self.resource_cache = self.resource_downloader.resource_cache
        
        self.debug_log("HamelnFinalScraper互換ブリッジ初期化完了")
        self.debug_log("新しいモジュール構造（Phase 1-4統合）を内部使用")
    
    def scrape_novel(self, url: str, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        小説スクレイピング（GUI互換メソッド）
        
        hameln_gui.pyから呼び出される主要メソッドです。
        内部的には新しいHamelnModularScraperを使用していますが、
        インターフェースは完全に互換性があります。
        
        Args:
            url: 小説のURL
            progress_callback: 進捗コールバック関数（GUI用）
            
        Returns:
            Dict[str, Any]: スクレイピング結果
        """
        self.debug_log(f"GUI互換レイヤー経由でスクレイピング開始: {url}")
        
        # 親クラス（HamelnModularScraper）のメソッドを呼び出し
        result = super().scrape_novel(url, progress_callback)
        
        if result['success']:
            self.debug_log(f"GUI互換レイヤー経由でスクレイピング完了: {result['title']}")
        else:
            self.debug_log(f"GUI互換レイヤー経由でスクレイピングエラー: {result.get('error')}", "ERROR")
        
        return result
    
    def get_page(self, url: str, timeout: int = 30) -> Dict[str, Any]:
        """ページ取得（GUI互換メソッド）"""
        self.debug_log(f"GUI互換レイヤー経由でページ取得: {url}")
        return super().get_page(url, timeout)
    
    def close(self):
        """リソース解放（GUI互換メソッド）"""
        self.debug_log("GUI互換レイヤー経由でリソース解放")
        super().close()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """キャッシュ統計取得（GUI互換メソッド）"""
        stats = super().get_cache_stats()
        
        # 追加の互換性情報
        stats['bridge_info'] = {
            'using_modular_architecture': True,
            'phase1_config': True,
            'phase2_network': True,
            'phase3_parsing': True,
            'phase4_resources': True,
            'compatibility_layer': 'active'
        }
        
        return stats
    
    # hameln_scraper_final.pyに存在する追加プロパティのエミュレーション
    @property
    def driver(self):
        """Seleniumドライバー互換プロパティ（現在は未使用）"""
        return None
    
    @property
    def cloudscraper(self):
        """CloudScraper互換プロパティ"""
        return self.network_client.cloudscraper
    
    @property
    def session(self):
        """リクエストセッション互換プロパティ"""
        return self.network_client.session
    
    def rotate_user_agent(self):
        """User-Agentローテーション互換メソッド"""
        return self.user_agent_rotator.rotate_user_agent()
    
    def validate_page(self, html_content: str, url: str) -> bool:
        """ページ検証互換メソッド"""
        from bs4 import BeautifulSoup
        
        # 文字列HTMLをBeautifulSoupオブジェクトに変換
        if isinstance(html_content, str):
            soup = BeautifulSoup(html_content, 'html.parser')
        else:
            soup = html_content
        
        # PageValidatorはboolを直接返す
        return self.page_validator.validate_page(soup, url)
    
    def analyze_page_content(self, html_content: str, url: str) -> Dict[str, Any]:
        """ページ内容分析互換メソッド"""
        # 小説情報抽出と章内容抽出を組み合わせた分析
        novel_info = self.extract_novel_info(html_content, url)
        chapter_content = self.extract_chapter_content(html_content, url)
        
        return {
            'novel_info': novel_info,
            'chapter_content': chapter_content,
            'analysis_type': 'modular_bridge_analysis'
        }


# エクスポート用のエイリアス
__all__ = ['HamelnFinalScraper']