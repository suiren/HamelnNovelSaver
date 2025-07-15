"""
スクレイパー設定管理モジュール
"""

import logging
from dataclasses import dataclass
from typing import List


@dataclass
class ScraperConfig:
    """スクレイパー設定クラス"""
    
    # 基本設定
    base_url: str = "https://syosetu.org"
    debug_mode: bool = True
    
    # 機能制御フラグ
    enable_novel_info_saving: bool = True
    enable_comments_saving: bool = True
    
    # ネットワーク設定
    retry_count: int = 3
    request_delay: float = 3.0
    max_delay: float = 30.0
    
    # User-Agent設定
    user_agents: List[str] = None
    
    # ログ設定
    log_file: str = "hameln_scraper.log"
    debug_log_file: str = "hameln_debug.log"
    log_level: int = logging.DEBUG
    
    def __post_init__(self):
        """初期化後の処理"""
        if self.user_agents is None:
            self.user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]
    
    def setup_logging(self):
        """ログ設定を初期化"""
        logging.basicConfig(
            level=self.log_level if self.debug_mode else logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)