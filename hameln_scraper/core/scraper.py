"""
メインスクレイパークラス - リファクタリング版
元のHamelnFinalScraperの機能を分割・整理
"""

import logging
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup

from .config import ScraperConfig
from ..network.client import NetworkClient
from ..parsing.validator import PageValidator


class HamelnScraper:
    """ハーメルンスクレイパー - リファクタリング版"""
    
    def __init__(self, config: Optional[ScraperConfig] = None):
        self.config = config or ScraperConfig()
        self.logger = self.config.setup_logging()
        
        # 各モジュールを初期化
        self.network_client = NetworkClient(self.config)
        self.validator = PageValidator()
        
        self.logger.info("ハーメルンスクレイパー初期化完了（リファクタリング版）")
    
    def scrape_novel(self, novel_url: str) -> Dict[str, Any]:
        """
        小説を取得（メイン機能）
        
        Args:
            novel_url: 小説のURL
            
        Returns:
            Dict[str, Any]: 取得結果
        """
        self.logger.info(f"小説取得開始: {novel_url}")
        
        try:
            # メインページ取得
            html_content = self.network_client.get_page(novel_url)
            if not html_content:
                return {"success": False, "error": "ページ取得失敗"}
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # ページ検証
            if not self.validator.validate_page(soup, novel_url):
                return {"success": False, "error": "無効なページ"}
            
            # 基本情報抽出
            title = self._extract_title(soup)
            author = self._extract_author(soup)
            
            self.logger.info(f"小説情報取得: {title} by {author}")
            
            return {
                "success": True,
                "title": title,
                "author": author,
                "url": novel_url,
                "html_content": html_content
            }
            
        except Exception as e:
            self.logger.error(f"小説取得エラー: {e}")
            return {"success": False, "error": str(e)}
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """タイトルを抽出"""
        # 複数のセレクターを試行
        selectors = [
            'h1',
            '.novel-title',
            '.title',
            'title'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element and element.get_text().strip():
                return element.get_text().strip()
        
        return "不明なタイトル"
    
    def _extract_author(self, soup: BeautifulSoup) -> str:
        """作者を抽出"""
        # 複数のセレクターを試行
        selectors = [
            '.author',
            '.novel-author',
            'a[href*="/user/"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element and element.get_text().strip():
                return element.get_text().strip()
        
        return "不明な作者"
    
    def close(self):
        """リソースをクリーンアップ"""
        if self.network_client:
            self.network_client.close()
        self.logger.info("スクレイパー終了")