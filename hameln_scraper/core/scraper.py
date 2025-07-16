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
from ..comments.handler import CommentsHandler
from ..resources.processor import ResourceProcessor
from ..novel.processor import NovelProcessor
from ..output.file_manager import FileManager


class HamelnScraper:
    """ハーメルンスクレイパー - リファクタリング版"""
    
    def __init__(self, config: Optional[ScraperConfig] = None):
        self.config = config or ScraperConfig()
        self.logger = self.config.setup_logging()
        
        # 各モジュールを初期化
        self.network_client = NetworkClient(self.config)
        self.file_manager = FileManager(self.config)
        self.comments_handler = CommentsHandler(self.config, self.network_client, self.file_manager)
        self.resource_processor = ResourceProcessor(self.config, self.network_client)
        self.novel_processor = NovelProcessor(self.config, self.network_client)

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
    
    def detect_comments_pagination(self, soup, base_url=""):
        """感想ページのページネーションを検出"""
        return self.comments_handler.detect_comments_pagination(soup, base_url)
    
    def extract_page_number(self, url):
        """URLからページ番号を抽出"""
        return self.comments_handler.extract_page_number(url)
    
    def get_all_comments_pages(self, base_url, output_dir=None, title=None, index_file_name=None):
        """複数ページの感想を全て取得して統合"""
        return self.comments_handler.get_all_comments_pages(base_url)
    
    def extract_comments_content(self, soup):
        """感想コンテンツを抽出"""
        return self.comments_handler.extract_comments_content(soup)
    
    def save_comments_page(self, comments_url, output_dir, title, index_file_name=None):
        """感想ページを保存"""
        return self.comments_handler.save_comments_page(comments_url, output_dir, title, index_file_name)
    
    def get_page(self, url, **kwargs):
        """ページを取得"""
        return self.network_client.get_page(url, **kwargs)
    
    def download_resource(self, url, output_dir, **kwargs):
        """リソースをダウンロード"""
        return self.resource_processor.download_resource(url, output_dir, **kwargs)
    
    def process_html_resources(self, soup, base_url, output_dir, **kwargs):
        """HTMLリソースを処理"""
        return self.resource_processor.process_html_resources(soup, base_url, output_dir, **kwargs)
    
    def extract_novel_info(self, soup):
        """小説情報を抽出"""
        return self.novel_processor.extract_novel_info(soup)
    
    def get_chapter_links(self, soup, base_url):
        """章リンクを取得"""
        return self.novel_processor.get_chapter_links(soup, base_url)
    
    def extract_chapter_content(self, soup):
        """章コンテンツを抽出"""
        return self.novel_processor.extract_chapter_content(soup)
    
    def save_complete_page(self, url, output_dir, filename, **kwargs):
        """完全なページを保存"""
        return self.file_manager.save_complete_page(url, output_dir, filename, **kwargs)
    
    def fix_local_navigation_links(self, soup, chapter_mapping):
        """ローカルナビゲーションリンクを修正"""
        return self.file_manager.fix_local_navigation_links(soup, chapter_mapping)

    
    def close(self):
        """リソースをクリーンアップ"""
        if self.network_client:
            self.network_client.close()
        self.logger.info("スクレイパー終了")
