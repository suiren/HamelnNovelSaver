"""
ハーメルン小説スクレイパー - リファクタリング版
モジュール分割による保守性向上
"""

from .core.scraper import HamelnScraper
from .core.config import ScraperConfig

__version__ = "2.0.0"
__all__ = ["HamelnScraper", "ScraperConfig"]