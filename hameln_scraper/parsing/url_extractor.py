"""
URL抽出モジュール
"""

import logging
from bs4 import BeautifulSoup
from typing import Optional, List


class UrlExtractor:
    """URL抽出クラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def extract_novel_info_url(self, soup: BeautifulSoup) -> Optional[str]:
        """小説情報URLを抽出"""
        # 基本的な実装
        info_link = soup.find('a', href=lambda x: x and 'info' in x)
        return info_link.get('href') if info_link else None
    
    def extract_comments_url(self, soup: BeautifulSoup) -> Optional[str]:
        """感想URLを抽出"""
        # 基本的な実装
        comments_link = soup.find('a', href=lambda x: x and 'comments' in x)
        return comments_link.get('href') if comments_link else None