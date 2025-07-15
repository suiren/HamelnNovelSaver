"""
ページ検証モジュール
"""

import logging
from bs4 import BeautifulSoup


class PageValidator:
    """ページ検証クラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 除外キーワード
        self.exclude_keywords = [
            'アクセス解析', 'Google Analytics', 'advertisement',
            'ページが見つかりませんでした', '404', 'Not Found',
            'メンテナンス中', 'maintenance', 'エラーが発生しました'
        ]
    
    def validate_page(self, soup: BeautifulSoup, url: str) -> bool:
        """
        ページの有効性を検証
        
        Args:
            soup: BeautifulSoupオブジェクト
            url: ページURL
            
        Returns:
            bool: ページが有効かどうか
        """
        if not soup:
            return False
        
        # 基本的な構造チェック
        if not soup.find('body'):
            self.logger.warning(f"bodyタグが見つかりません: {url}")
            return False
        
        # エラーページチェック
        page_text = soup.get_text()
        for keyword in self.exclude_keywords:
            if keyword in page_text:
                self.logger.warning(f"除外キーワード検出: {keyword} in {url}")
                return False
        
        # 最小コンテンツ長チェック
        if len(page_text.strip()) < 100:
            self.logger.warning(f"コンテンツが短すぎます: {len(page_text)} 文字")
            return False
        
        return True
    
    def is_likely_novel_content(self, text: str) -> bool:
        """
        小説コンテンツの可能性を判定
        
        Args:
            text: 判定するテキスト
            
        Returns:
            bool: 小説コンテンツの可能性があるかどうか
        """
        if not text or len(text.strip()) < 50:
            return False
        
        # 小説らしい特徴をチェック
        novel_indicators = [
            '。', '、', 'だった', 'である', 'していた',
            'という', 'ところ', 'それは', 'そして', 'しかし'
        ]
        
        indicator_count = sum(1 for indicator in novel_indicators if indicator in text)
        return indicator_count >= 3