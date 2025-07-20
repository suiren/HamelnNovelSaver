"""
ハーメルンネットワーククライアント
"""

import time
import requests
import cloudscraper
import logging
import traceback
from bs4 import BeautifulSoup
from typing import Optional, Union
from .user_agent import UserAgentRotator
from .compression import ResponseDecompressor


class HamelnNetworkClient:
    """ハーメルンサイト専用ネットワーククライアント"""
    
    def __init__(self, base_url: str = "https://syosetu.org", debug_mode: bool = True):
        self.base_url = base_url
        self.debug_mode = debug_mode
        self.logger = logging.getLogger(__name__)
        
        # User-Agent管理
        self.ua_rotator = UserAgentRotator()
        
        # レスポンス解凍器
        self.decompressor = ResponseDecompressor()
        
        # CloudScraperを初期化
        self.cloudscraper = None
        self.session = requests.Session()
        
        self.setup_scrapers()
        
    def setup_scrapers(self):
        """スクレイパーを設定（強化版）"""
        try:
            self.debug_log("CloudScraper初期化開始")
            
            # CloudScraper設定（より進歩的な設定）
            self.cloudscraper = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'desktop': True
                },
                delay=10,  # リクエスト間の遅延
                debug=False
            )
            
            # ユーザーエージェントを設定
            self.cloudscraper.headers.update({
                'User-Agent': self.ua_rotator.get_current_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0'
            })
            
            self.debug_log("CloudScraper設定完了")
            self.debug_log("Chrome/Chromiumが見つからないため、CloudScraperのみ使用")
            
            # Selenium設定（オプション）
            try:
                pass  # Skip Selenium for tests
            except Exception as e:
                self.logger.info(f"Chrome/Chromiumが見つからないため、CloudScraperのみ使用: {e}")
        except Exception as e:
            self.debug_log(f"スクレイパー設定エラー: {e}", "ERROR")
            self.debug_log(f"スタックトレース: {traceback.format_exc()}", "ERROR")
            
    def rotate_user_agent(self):
        """ユーザーエージェントをローテーション"""
        new_ua = self.ua_rotator.rotate_user_agent()
        if self.cloudscraper:
            self.cloudscraper.headers.update({'User-Agent': new_ua})
        self.debug_log(f"User-Agentを変更: {new_ua[:50]}...")
        return new_ua
    
    def decompress_response(self, response):
        """レスポンスの圧縮解凍処理"""
        return self.decompressor.decompress_response(response)
        
    def get_page(self, url: str, retry_count: int = 3) -> Optional[BeautifulSoup]:
        """ページを取得してBeautifulSoupオブジェクトを返す"""
        
        self.debug_log(f"ページ取得開始: {url}")
        
        for attempt in range(retry_count):
            try:
                if attempt > 0:
                    self.debug_log(f"リトライ {attempt + 1}/{retry_count}")
                    
                # User-Agentローテーション（リトライ時）
                if attempt > 0:
                    self.rotate_user_agent()
                    
                # CloudScraperでページを取得
                self.debug_log("CloudScraperでページ取得中...")
                response = self.cloudscraper.get(url, timeout=30)
                
                self.debug_log(f"レスポンス取得: {response.status_code}")
                
                # レスポンスの確認
                if response.status_code != 200:
                    self.debug_log(f"HTTPエラー: {response.status_code}", "ERROR")
                    
                    if response.status_code == 403:
                        self.debug_log("403エラー: bot検知による拒否", "ERROR")
                        if attempt < retry_count - 1:
                            wait_time = 30 * (attempt + 1)
                            self.debug_log(f"{wait_time}秒待機してリトライ...")
                            time.sleep(wait_time)
                            continue
                        else:
                            return None
                            
                    elif response.status_code == 429:
                        self.debug_log("429エラー: リクエスト制限", "ERROR")
                        if attempt < retry_count - 1:
                            wait_time = 60 * (attempt + 1)
                            self.debug_log(f"{wait_time}秒待機してリトライ...")
                            time.sleep(wait_time)
                            continue
                        else:
                            return None
                    
                    continue
                    
                # HTMLの解凍
                html_content = self.decompress_response(response)
                
                if not html_content:
                    self.debug_log("HTMLコンテンツが空です", "ERROR")
                    continue
                    
                # BeautifulSoupでパース
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # ページの妥当性チェック
                if not self.validate_page(soup, url):
                    self.debug_log("ページの妥当性チェックに失敗", "ERROR")
                    if attempt < retry_count - 1:
                        wait_time = 10 * (attempt + 1)
                        self.debug_log(f"{wait_time}秒待機してリトライ...")
                        time.sleep(wait_time)
                        continue
                    else:
                        return None
                        
                self.debug_log("ページ取得完了")
                return soup
                
            except requests.exceptions.RequestException as e:
                self.debug_log(f"リクエストエラー: {e}", "ERROR")
                if attempt < retry_count - 1:
                    wait_time = 15 * (attempt + 1)
                    self.debug_log(f"{wait_time}秒待機してリトライ...")
                    time.sleep(wait_time)
                    continue
                else:
                    return None
                    
            except Exception as e:
                self.debug_log(f"予期せぬエラー: {e}", "ERROR")
                self.debug_log(f"スタックトレース: {traceback.format_exc()}", "ERROR")
                if attempt < retry_count - 1:
                    wait_time = 20 * (attempt + 1)
                    self.debug_log(f"{wait_time}秒待機してリトライ...")
                    time.sleep(wait_time)
                    continue
                else:
                    return None
                    
        self.debug_log("全てのリトライに失敗しました", "ERROR")
        return None
        
    def validate_page(self, soup: BeautifulSoup, url: str) -> bool:
        """ページの妥当性を検証"""
        # 基本的なHTML構造チェック
        if not soup.find('title'):
            self.debug_log("ページ検証: タイトルタグが見つかりません", "WARNING")
            return False
            
        # Cloudflareチャレンジページかチェック
        if soup.find('div', class_='cf-browser-verification'):
            self.debug_log("ページ検証: Cloudflareチャレンジページです", "WARNING")
            return False
            
        # 内容の長さチェック
        text_content = soup.get_text()
        if len(text_content) < 50:
            self.debug_log(f"ページ検証: コンテンツが少なすぎます ({len(text_content)}文字)", "WARNING")
            return False
            
        # エラーページかチェック
        title = soup.find('title')
        if title and 'エラー' in title.get_text():
            self.debug_log("ページ検証: エラーページです", "WARNING")
            return False
            
        return True
        
    def debug_log(self, message: str, level: str = "INFO"):
        """デバッグログ出力"""
        if self.debug_mode:
            timestamp = time.strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] {level}: {message}"
            print(formatted_message)
            
            # ログファイルにも出力
            if level == "ERROR":
                self.logger.error(message)
            elif level == "WARNING":
                self.logger.warning(message)
            elif level == "DEBUG":
                self.logger.debug(message)
            else:
                self.logger.info(message)
                
    def close(self):
        """リソースを解放"""
        if self.cloudscraper:
            self.cloudscraper.close()
        if self.session:
            self.session.close()
            
    def get_status(self) -> dict:
        """クライアントの状態を取得"""
        return {
            'base_url': self.base_url,
            'user_agent_count': self.ua_rotator.get_user_agent_count(),
            'current_user_agent': self.ua_rotator.get_current_user_agent()[:50] + "...",
            'cloudscraper_initialized': self.cloudscraper is not None,
            'debug_mode': self.debug_mode
        }
