"""
ネットワーククライアント管理
CloudScraper と Selenium の統合管理
"""

import time
import logging
import cloudscraper
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Optional, Union
import requests

from .user_agent import UserAgentRotator
from .compression import ResponseDecompressor


class NetworkClient:
    """ネットワーククライアント統合管理クラス"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.ua_rotator = UserAgentRotator(config.user_agents)
        self.decompressor = ResponseDecompressor()
        
        # クライアント初期化
        self.cloudscraper = None
        self.driver = None
        self.session = requests.Session()
        
        self._setup_scrapers()
    
    def _setup_scrapers(self):
        """スクレイパーを設定"""
        try:
            self.logger.info("CloudScraper初期化開始")
            
            # CloudScraper設定
            self.cloudscraper = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'mobile': False
                },
                debug=self.config.debug_mode
            )
            
            # セッション設定
            self.cloudscraper.headers.update({
                'User-Agent': self.ua_rotator.get_current(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'ja-JP,ja;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            })
            
            self.logger.info("CloudScraper設定完了")
            
            # Selenium設定（オプション）
            try:
                self._setup_selenium()
            except Exception as e:
                self.logger.info(f"Chrome/Chromiumが見つからないため、CloudScraperのみ使用: {e}")
                
        except Exception as e:
            self.logger.error(f"スクレイパー設定エラー: {e}")
            raise
    
    def _setup_selenium(self):
        """Selenium WebDriverを設定"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument(f'--user-agent={self.ua_rotator.get_current()}')
        
        self.driver = uc.Chrome(options=chrome_options)
        self.logger.info("Selenium WebDriver設定完了")
    
    def rotate_user_agent(self):
        """User-Agentをローテーション"""
        new_ua = self.ua_rotator.rotate()
        if self.cloudscraper:
            self.cloudscraper.headers.update({'User-Agent': new_ua})
        self.logger.debug(f"User-Agent切り替え: {new_ua[:50]}...")
    
    def get_page(self, url: str, retry_count: int = None) -> Optional[str]:
        """
        ページを取得（CloudScraper + Seleniumフォールバック）
        
        Args:
            url: 取得するURL
            retry_count: リトライ回数
            
        Returns:
            str: ページ内容（HTML）
        """
        if retry_count is None:
            retry_count = self.config.retry_count
            
        for attempt in range(retry_count):
            try:
                # CloudScraperで取得試行
                response = self._get_with_cloudscraper(url)
                if response:
                    return response
                
                # Seleniumフォールバック
                if self.driver:
                    response = self._get_with_selenium(url)
                    if response:
                        return response
                
                # 失敗時の待機
                if attempt < retry_count - 1:
                    delay = min(self.config.request_delay * (attempt + 1), self.config.max_delay)
                    self.logger.warning(f"取得失敗、{delay}秒後にリトライ (試行 {attempt + 1}/{retry_count})")
                    time.sleep(delay)
                    self.rotate_user_agent()
                    
            except Exception as e:
                self.logger.error(f"ページ取得エラー (試行 {attempt + 1}): {e}")
                if attempt < retry_count - 1:
                    time.sleep(self.config.request_delay)
        
        self.logger.error(f"ページ取得失敗: {url}")
        return None
    
    def _get_with_cloudscraper(self, url: str) -> Optional[str]:
        """CloudScraperでページ取得"""
        try:
            response = self.cloudscraper.get(url, timeout=30)
            if response.status_code == 200:
                return self.decompressor.decompress(response)
            else:
                self.logger.warning(f"CloudScraper取得失敗: {response.status_code}")
                return None
        except Exception as e:
            self.logger.debug(f"CloudScraper エラー: {e}")
            return None
    
    def _get_with_selenium(self, url: str) -> Optional[str]:
        """Seleniumでページ取得"""
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            return self.driver.page_source
        except Exception as e:
            self.logger.debug(f"Selenium エラー: {e}")
            return None
    
    def get_resource(self, url: str) -> Optional[bytes]:
        """
        リソースファイル（画像、CSS、JS等）をダウンロード
        
        Args:
            url: ダウンロードするリソースのURL
            
        Returns:
            bytes: リソースの内容（バイナリ）
        """
        try:
            # CloudScraperでリソース取得
            response = self.cloudscraper.get(url, timeout=30)
            if response.status_code == 200:
                self.logger.debug(f"リソース取得成功: {url}")
                return response.content
            else:
                self.logger.warning(f"リソース取得失敗: {response.status_code} - {url}")
                return None
        except Exception as e:
            self.logger.debug(f"リソース取得エラー ({url}): {e}")
            return None
    
    def close(self):
        """リソースをクリーンアップ"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
        if self.session:
            self.session.close()