#!/usr/bin/env python3
"""
ハーメルン小説保存アプリケーション - 最終版
完全なページ保存機能（CSS、JavaScript、画像等を含む）
リファクタリング版 - モジュール化された構造
"""

import os
import sys
from hameln_scraper.core.scraper import HamelnScraper
from hameln_scraper.core.config import ScraperConfig

class HamelnFinalScraper(HamelnScraper):
    """後方互換性のためのラッパークラス"""
    
    def __init__(self):
        config = ScraperConfig()
        config.enable_novel_info_saving = False
        config.enable_comments_saving = False
        super().__init__(config)


import time
import re
import base64
import requests
import cloudscraper
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from urllib.parse import urljoin, urlparse
from PIL import Image
import io
import logging
import traceback
from datetime import datetime
import gzip
import zlib
import brotli
import copy

class HamelnFinalScraperLegacy:
    def __init__(self, base_url="https://syosetu.org"):
        self.base_url = base_url
        self.driver = None
        self.cloudscraper = None
        self.session = requests.Session()
        self.debug_mode = True
        
        # 🎛️ 機能制御フラグ（Norton検出問題解決により、新機能を有効化）
        self.enable_novel_info_saving = True   # 小説情報保存機能
        self.enable_comments_saving = True     # 感想保存機能
        
        self.resource_cache = {}  # URL -> local_filename mapping
        
        self.setup_logging()
        self.setup_scrapers()
        
    def setup_logging(self):
        """ログ設定を初期化"""
        logging.basicConfig(
            level=logging.DEBUG if self.debug_mode else logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('hameln_scraper.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("ハーメルンスクレイパー初期化開始")
        
    def debug_log(self, message, level="INFO"):
        """デバッグログ出力（アプリ内表示＋外部ファイル出力）"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {level}: {message}"
        print(formatted_message)
        
        # 外部ファイルにも出力
        try:
            log_file = "hameln_debug.log"
            with open(log_file, 'a', encoding='utf-8') as f:
                full_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{full_timestamp}] {level}: {message}\n")
        except Exception as e:
            print(f"ログファイル書き込みエラー: {e}")
        
        if level == "ERROR":
            self.logger.error(message)
        elif level == "WARNING":
            self.logger.warning(message)
        elif level == "DEBUG":
            self.logger.debug(message)
        else:
            self.logger.info(message)
        
    def setup_scrapers(self):
        """スクレイパーを設定（強化版）"""
        try:
            self.debug_log("CloudScraper初期化開始")
            
            # ユーザーエージェントローテーション用のリスト
            self.user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]
            self.current_ua_index = 0
            
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
                'User-Agent': self.user_agents[0],
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
            
            # Selenium/Chrome初期化をスキップ（CloudScraperのみ使用）
            self.debug_log("Chrome/Chromiumが見つからないため、CloudScraperのみ使用")
            self.driver = None
            
        except Exception as e:
            self.debug_log(f"スクレイパー設定エラー: {e}", "ERROR")
            self.debug_log(f"スタックトレース: {traceback.format_exc()}", "ERROR")
            self.driver = None
            
    def rotate_user_agent(self):
        """ユーザーエージェントをローテーション"""
        self.current_ua_index = (self.current_ua_index + 1) % len(self.user_agents)
        new_ua = self.user_agents[self.current_ua_index]
        self.cloudscraper.headers.update({'User-Agent': new_ua})
        self.debug_log(f"User-Agentを変更: {new_ua[:50]}...")
        return new_ua
    
    def decompress_response(self, response):
        """レスポンスの圧縮解凍処理（CloudScraperの自動処理を活用）"""
        # CloudScraperは自動的に圧縮を解凍するため、response.textを直接使用
        try:
            html_content = response.text
            self.debug_log(f"CloudScraperで取得されたHTMLテキスト長: {len(html_content)}")
            return html_content
        except Exception as e:
            self.debug_log(f"HTMLテキスト取得エラー: {e}", "ERROR")
            # フォールバック: 手動解凍を試す
            content = response.content
            encoding = response.headers.get('content-encoding', '').lower()
            
            self.debug_log(f"フォールバック解凍開始 - Content-Encoding: {encoding}")
            
            try:
                if encoding == 'gzip':
                    content = gzip.decompress(content)
                elif encoding == 'deflate':
                    content = zlib.decompress(content)
                elif encoding == 'br':
                    content = brotli.decompress(content)
                
                return content.decode('utf-8')
            except Exception as decode_error:
                self.debug_log(f"手動解凍も失敗: {decode_error}", "ERROR")
                return ""
    
    def get_page(self, url, retry_count = 3):
        """ページ取得: CloudScraper → Selenium フォールバック（強化版）"""
        self.debug_log(f"ページ取得開始: {url}")
        
        # URL形式の検証
        if not url.startswith('http'):
            self.debug_log(f"無効なURL形式: {url}", "ERROR")
            return None
        
        # アクセス間隔を設けてサーバー負荷を軽減
        time.sleep(2)  # ベーシックな待機時間
        
        # まずCloudScraperを試す（高速）
        for attempt in range(retry_count):
            try:
                if attempt > 0:
                    self.debug_log(f"CloudScraper再試行 {attempt + 1}/{retry_count}")
                    # User-Agentをローテーション
                    self.rotate_user_agent()
                    # 待機時間を漸進的に増やす
                    wait_time = 5 + (attempt * 3)
                    self.debug_log(f"アクセス間隔を取ります: {wait_time}秒")
                    time.sleep(wait_time)
                else:
                    self.debug_log("CloudScraperで初回試行中...")
                    
                response = self.cloudscraper.get(url, timeout=30)
                
                self.debug_log(f"CloudScraperレスポンス: ステータス={response.status_code}, サイズ={len(response.content)}bytes")
                
                if response.status_code == 403:
                    self.debug_log("CloudScraper: 403 Forbidden - bot検知により拒否", "WARNING")
                    if attempt < retry_count - 1:
                        continue  # 再試行
                elif response.status_code == 404:
                    self.debug_log("CloudScraper: 404 Not Found - ページが存在しません", "WARNING")
                    return None  # 404は再試行しない
                elif response.status_code == 503:
                    self.debug_log("CloudScraper: 503 Service Unavailable - サーバーメンテナンス中", "WARNING")
                    if attempt < retry_count - 1:
                        continue  # 再試行
                elif response.status_code == 429:
                    self.debug_log("CloudScraper: 429 Too Many Requests - レート制限", "WARNING")
                    if attempt < retry_count - 1:
                        wait_time = 30 + (attempt * 15)  # より長い待機
                        self.debug_log(f"レート制限のため {wait_time}秒待機...")
                        time.sleep(wait_time)
                        continue
                else:
                    response.raise_for_status()
                
                # 圧縮解凍処理
                html_content = self.decompress_response(response)
                
                if not html_content:
                    self.debug_log("HTMLコンテンツが空です", "ERROR")
                    if attempt < retry_count - 1:
                        continue
                    return None
                
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # ページ内容の詳細分析
                self.analyze_page_content(soup, "CloudScraper")
                
                # ページが正常に取得できたかチェック
                if self.validate_page(soup, url):
                    self.debug_log(f"CloudScraperで取得成功: {url}")
                    return soup
                else:
                    self.debug_log("CloudScraperで取得したページが無効", "WARNING")
                    if attempt < retry_count - 1:
                        continue  # 再試行
                    else:
                        self.debug_log("CloudScraperでの全試行が失敗、Seleniumで再試行...", "WARNING")
                        break
                        
            except requests.exceptions.Timeout:
                self.debug_log("CloudScraperタイムアウト", "ERROR")
                if attempt < retry_count - 1:
                    continue
            except requests.exceptions.ConnectionError:
                self.debug_log("CloudScraper接続エラー", "ERROR")
                if attempt < retry_count - 1:
                    continue
            except Exception as e:
                self.debug_log(f"CloudScraperエラー: {e}", "ERROR")
                self.debug_log(f"CloudScraperスタックトレース: {traceback.format_exc()}", "DEBUG")
                if attempt < retry_count - 1:
                    continue
        
        # Seleniumで再試行
        if self.driver:
            for attempt in range(retry_count):
                try:
                    self.debug_log(f"Selenium試行 {attempt + 1}/{retry_count}")
                    
                    self.driver.get(url)
                    
                    # Cloudflareの認証チェック待機（タイムアウト延長）
                    try:
                        WebDriverWait(self.driver, 15).until(
                            lambda driver: "Cloudflare" not in driver.title and "Just a moment" not in driver.title
                        )
                        self.debug_log("Cloudflare認証クリア")
                    except:
                        self.debug_log("Cloudflare認証待機タイムアウト、続行...", "WARNING")
                    
                    # ページの読み込み完了を待機
                    WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    
                    # 動的コンテンツの読み込み完了を待機
                    time.sleep(8)
                    
                    # 画像の遅延読み込みを強制実行（スクロールで発火）
                    try:
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(2)
                        self.driver.execute_script("window.scrollTo(0, 0);")
                        time.sleep(2)
                    except Exception as e:
                        print(f"スクロール処理エラー: {e}")
                    
                    soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                    
                    # ページ内容の詳細分析
                    self.analyze_page_content(soup, "Selenium")
                    
                    if self.validate_page(soup, url):
                        self.debug_log(f"Seleniumで取得成功: {url}")
                        return soup
                    else:
                        self.debug_log(f"無効なページ、再試行 {attempt + 1}/{retry_count}", "WARNING")
                        time.sleep(3)
                        
                except Exception as e:
                    self.debug_log(f"Selenium試行エラー {attempt + 1}/{retry_count}: {e}", "ERROR")
                    self.debug_log(f"Seleniumスタックトレース: {traceback.format_exc()}", "DEBUG")
                    if attempt < retry_count - 1:
                        time.sleep(5)
        else:
            self.debug_log("Seleniumドライバーが利用できません", "ERROR")
        
        self.debug_log(f"全ての方法で失敗: {url}", "ERROR")
        return None
        
    def analyze_page_content(self, soup, method):
        """ページ内容を詳細分析"""
        if not soup:
            self.debug_log(f"{method}: soupがNone", "ERROR")
            return
            
        title = soup.title.string if soup.title else "タイトルなし"
        body_length = len(soup.get_text()) if soup else 0
        
        self.debug_log(f"{method}取得ページ分析:")
        self.debug_log(f"  - タイトル: {title}")
        self.debug_log(f"  - 本文長: {body_length}文字")
        
        # HTMLの最初の500文字を確認
        html_snippet = str(soup)[:500]
        self.debug_log(f"  - HTML先頭部分: {html_snippet}...")
        
        # 特定の要素の存在確認
        elements_check = {
            'h1': len(soup.find_all('h1')),
            'div': len(soup.find_all('div')),
            'a': len(soup.find_all('a')),
            'novel_body': len(soup.find_all('div', class_='novel_body')),
            'novel_view': len(soup.find_all('div', class_='novel_view'))
        }
        
        for element, count in elements_check.items():
            self.debug_log(f"  - {element}要素数: {count}")
        
        # エラーページかどうかチェック
        error_indicators = ['404', 'Error', 'Forbidden', 'Access Denied', 'メンテナンス']
        for indicator in error_indicators:
            if indicator in title:
                self.debug_log(f"  - エラーページ検出: {indicator}", "WARNING")
                
    def validate_page(self, soup, url):
        """ページが正常に取得できたかチェック"""
        if not soup:
            self.debug_log("ページ検証: soupがNone", "ERROR")
            return False
            
        title = soup.title.string if soup.title else ""
        
        # Cloudflareの認証ページチェック
        if 'Cloudflare' in title or 'Just a moment' in title:
            self.debug_log(f"ページ検証: Cloudflare認証ページ検出 - {title}", "ERROR")
            return False
            
        # エラーページチェック
        error_keywords = ['404', 'Error', 'Forbidden', 'Access Denied', 'Not Found', 'メンテナンス']
        for keyword in error_keywords:
            if keyword in title:
                self.debug_log(f"ページ検証: エラーページ検出 - {keyword} in {title}", "ERROR")
                return False
            
        # 最低限の内容があるかチェック
        text_content = soup.get_text(strip=True)
        
        # 基本的なHTML構造チェック（bodyタグがない場合も許可）
        if not soup.find('body'):
            self.debug_log("ページ検証: bodyタグが見つかりません（SPAの可能性）", "WARNING")
            # bodyタグがなくても、有効なコンテンツがあれば続行
            if len(text_content) > 500:  # 十分なコンテンツがある場合
                self.debug_log("ページ検証: bodyタグなしでも十分なコンテンツがあるため続行", "INFO")
            else:
                self.debug_log("ページ検証: bodyタグなしでコンテンツも不十分", "ERROR")
                return False
        elif len(text_content) < 100:
            self.debug_log(f"ページ検証: コンテンツが少なすぎます ({len(text_content)}文字)", "WARNING")
            return False
        
        # ハーメルン特有のチェック
        if 'syosetu.org' in url:
            # ハーメルンのページかどうか確認
            if not any(indicator in text_content for indicator in ['ハーメルン', 'syosetu', '小説']):
                self.debug_log("ページ検証: ハーメルンページではない可能性", "WARNING")
                return False
        
        self.debug_log("ページ検証: 正常なページ")
        return True
            
    def download_resource(self, url, base_path):
        """リソース（画像、CSS、JS等）をダウンロード（キャッシュ機能付き）"""
        try:
            # 絶対URLに変換（ハーメルン特化）
            if not url.startswith('http'):
                if url.startswith('./resources/'):
                    # ./resources/style.css -> https://img.syosetu.org/css/style.css
                    resource_file = url.replace('./resources/', '')
                    if resource_file.endswith('.css'):
                        url = f"https://img.syosetu.org/css/{resource_file}"
                    elif resource_file.endswith('.js'):
                        url = f"https://img.syosetu.org/js/{resource_file}"
                    else:
                        url = f"https://img.syosetu.org/image/{resource_file}"
                elif url.startswith('./'):
                    # ./banner.png -> https://img.syosetu.org/image/banner.png
                    url = f"https://img.syosetu.org/image/{url[2:]}"
                else:
                    url = urljoin(self.base_url, url)
            
            if url in self.resource_cache:
                cached_filename = self.resource_cache[url]
                cached_path = os.path.join(base_path, cached_filename)
                if os.path.exists(cached_path):
                    print(f"キャッシュから取得: {cached_filename}")
                    return cached_filename
                else:
                    del self.resource_cache[url]
            
            # ファイル名を生成
            parsed = urlparse(url)
            filename = os.path.basename(parsed.path)
            if not filename or '.' not in filename:
                # 拡張子がない場合は推測
                if 'css' in url:
                    filename = f"style_{hash(url) % 10000}.css"
                elif 'js' in url:
                    filename = f"script_{hash(url) % 10000}.js"
                elif any(ext in url for ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg']):
                    ext = url.split('.')[-1].split('?')[0]
                    filename = f"image_{hash(url) % 10000}.{ext}"
                else:
                    filename = f"resource_{hash(url) % 10000}.txt"
            
            # ローカルパスを作成
            local_path = os.path.join(base_path, filename)
            
            # 既存ファイルの保護（エンコーディング破損防止）
            if os.path.exists(local_path):
                print(f"既存ファイルを使用（上書き防止）: {filename}")
                self.resource_cache[url] = filename
                return filename
            
            # リソースをダウンロード
            response = self.cloudscraper.get(url, timeout=10)
            response.raise_for_status()
            
            # CSSファイルの場合は文字エンコーディングを考慮
            if filename.endswith('.css'):
                response.encoding = 'utf-8'
                with open(local_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)
            else:
                with open(local_path, 'wb') as f:
                    f.write(response.content)
            
            print(f"リソース保存: {filename}")
            
            self.resource_cache[url] = filename
            
            return filename
            
        except Exception as e:
            print(f"リソースダウンロードエラー ({url}): {e}")
            return url  # 失敗した場合は元のURLを返す
            
    def adjust_resource_paths_only(self, soup, output_dir):
        """リソースファイルをダウンロードせず、パス調整のみ実行（重複処理防止）"""
        resources_dir_name = "resources"
        
        # CSSファイルのhref属性を調整
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href')
            if href and href.startswith(('http', '//')):
                filename = os.path.basename(urlparse(href).path)
                if filename:
                    link['href'] = f"./{resources_dir_name}/{filename}"
        
        # JavaScriptファイルのsrc属性を調整
        for script in soup.find_all('script', src=True):
            src = script.get('src')
            if src and src.startswith(('http', '//')):
                filename = os.path.basename(urlparse(src).path)
                if filename:
                    script['src'] = f"./{resources_dir_name}/{filename}"
        
        # 画像のsrc属性を調整
        for img in soup.find_all('img', src=True):
            src = img.get('src')
            if src and src.startswith(('http', '//')):
                filename = os.path.basename(urlparse(src).path)
                if filename:
                    img['src'] = f"./{resources_dir_name}/{filename}"
        
        print(f"📂 パス調整のみ完了（ダウンロードスキップ）")
        return soup
    
    def process_html_resources(self, soup, base_path):
        """HTMLのリソースを処理してローカル化（ブラウザレベル完全保存）"""
        # ブラウザ互換のリソースディレクトリ名を使用
        resources_dir_name = getattr(self, 'browser_compatible_name', 'resources')
        resources_dir = os.path.join(base_path, resources_dir_name)
        os.makedirs(resources_dir, exist_ok=True)
        
        print("=== ブラウザレベル完全リソース保存開始 ===")
        
        # 1. CSS リンクを処理（スタイルシート）
        css_links = soup.find_all('link', {'rel': 'stylesheet'})
        print(f"CSS リンク数: {len(css_links)}")
        for link in css_links:
            href = link.get('href')
            if href:
                print(f"CSS処理中: {href}")
                local_file = self.download_and_process_css(href, resources_dir)
                link['href'] = f"./{resources_dir_name}/{local_file}"
        
        # 2. すべての外部リンクリソース（ファビコン、アイコン等）
        icon_rels = ['icon', 'shortcut icon', 'apple-touch-icon', 'apple-touch-icon-precomposed', 
                     'mask-icon', 'fluid-icon']
        icon_links = soup.find_all('link', {'rel': icon_rels})
        print(f"アイコンリンク数: {len(icon_links)}")
        for link in icon_links:
            href = link.get('href')
            if href:
                print(f"アイコン処理中: {href}")
                local_file = self.download_resource(href, resources_dir)
                if local_file != href:
                    link['href'] = f"./{resources_dir_name}/{local_file}"
        
        # 3. JavaScript ファイル
        scripts = soup.find_all('script', {'src': True})
        print(f"JavaScript ファイル数: {len(scripts)}")
        for script in scripts:
            src = script.get('src')
            if src:
                print(f"JS処理中: {src}")
                local_file = self.download_resource(src, resources_dir)
                if local_file != src:
                    script['src'] = f"./{resources_dir_name}/{local_file}"
        
        # 4. 全ての画像（img タグ）
        images = soup.find_all('img', {'src': True})
        print(f"画像数: {len(images)}")
        for img in images:
            src = img.get('src')
            if src:
                print(f"画像処理中: {src}")
                local_file = self.download_resource(src, resources_dir)
                if local_file != src:
                    img['src'] = f"./{resources_dir_name}/{local_file}"
        
        # 5. インラインスタイルの背景画像
        styled_elements = soup.find_all(style=True)
        print(f"インラインスタイル要素数: {len(styled_elements)}")
        for element in styled_elements:
            style = element.get('style')
            if 'url(' in style:
                import re
                urls = re.findall(r'url\([\'"]?([^\'"]+)[\'"]?\)', style)
                for url in urls:
                    print(f"インラインスタイル画像処理中: {url}")
                    local_file = self.download_resource(url, resources_dir)
                    if local_file != url:
                        style = style.replace(url, f"./{resources_dir_name}/{local_file}")
                element['style'] = style
        
        # 6. その他のメディアリソース（video, audio, embed, object）
        media_tags = ['video', 'audio', 'embed', 'object', 'source']
        for tag_name in media_tags:
            elements = soup.find_all(tag_name)
            for element in elements:
                # src, data, href 属性をチェック
                for attr in ['src', 'data', 'href', 'poster']:
                    url = element.get(attr)
                    if url and url.startswith(('http', '//')):
                        print(f"{tag_name}のリソース処理中: {url}")
                        local_file = self.download_resource(url, resources_dir)
                        if local_file != url:
                            element[attr] = f"./{resources_dir_name}/{local_file}"
        
        # 7. CSS内の@import文やfont-face等の処理を強化
        for style_tag in soup.find_all('style'):
            if style_tag.string:
                css_content = style_tag.string
                # @import文を処理
                import re
                imports = re.findall(r'@import\s+[\'"]([^\'"]+)[\'"]', css_content)
                for import_url in imports:
                    print(f"CSS @import処理中: {import_url}")
                    local_file = self.download_and_process_css(import_url, resources_dir)
                    css_content = css_content.replace(import_url, f"./{resources_dir_name}/{local_file}")
                
                # url()参照を処理（相対パス・絶対パス両方に対応）
                urls = re.findall(r'url\([\'"]?([^\'"]+)[\'"]?\)', css_content)
                for url in urls:
                    # 絶対URL・相対URL・ローカルファイル名すべてを処理
                    if url.startswith(('http', '//', '/')):
                        # 絶対URLの場合
                        print(f"CSS内画像ダウンロード: {self.base_url if url.startswith('/') and not url.startswith('//') else 'https:' if url.startswith('//') else ''}{url}")
                        local_file = self.download_resource(url, resources_dir)
                        if local_file != url:
                            # CSS内の相対パス・絶対パス両方に対応
                            css_content = css_content.replace(f"url({url})", f"url({local_file})")
                            css_content = css_content.replace(f"url('{url}')", f"url('{local_file}')")
                            css_content = css_content.replace(f'url("{url}")', f'url("{local_file}")')
                    elif url and not url.startswith(('data:', '#', './')):
                        # 相対ファイル名の場合（banner.png等）- 既にローカル化されていない場合のみ
                        full_url = f"https://img.syosetu.org/image/{url}"
                        print(f"CSS内相対画像ダウンロード: {full_url}")
                        local_file = self.download_resource(full_url, resources_dir)
                        if local_file and local_file != url:
                            # 相対ファイル名を置換
                            css_content = css_content.replace(f"url({url})", f"url({local_file})")
                            css_content = css_content.replace(f"url('{url}')", f"url('{local_file}')")
                            css_content = css_content.replace(f'url("{url}")', f'url("{local_file}")')
                            print(f"CSS内画像パス更新: {url} -> {local_file}")
                
                style_tag.string = css_content
        
        # 8. data-src属性（遅延読み込み画像）も処理
        lazy_images = soup.find_all(attrs={'data-src': True})
        print(f"遅延読み込み画像数: {len(lazy_images)}")
        for img in lazy_images:
            data_src = img.get('data-src')
            if data_src:
                print(f"遅延読み込み画像処理中: {data_src}")
                local_file = self.download_resource(data_src, resources_dir)
                if local_file != data_src:
                    img['data-src'] = f"./{resources_dir_name}/{local_file}"
                    # srcsetやdata-srcset属性も存在する場合は処理
                    if img.get('data-srcset'):
                        img['data-srcset'] = f"./{resources_dir_name}/{local_file}"
                    # 遅延読み込み画像をsrcにも設定
                    if not img.get('src'):
                        img['src'] = f"./{resources_dir_name}/{local_file}"
        
        # 9. その他の画像属性も処理（ハーメルン特有の属性）
        for attr in ['data-original', 'data-lazy-src', 'data-echo']:
            attr_images = soup.find_all(attrs={attr: True})
            print(f"{attr}属性画像数: {len(attr_images)}")
            for img in attr_images:
                img_src = img.get(attr)
                if img_src:
                    print(f"{attr}属性画像処理中: {img_src}")
                    local_file = self.download_resource(img_src, resources_dir)
                    if local_file != img_src:
                        img[attr] = f"./{resources_dir_name}/{local_file}"
        
        print("=== ブラウザレベル完全リソース保存完了 ===")
        return soup
    
    def fix_local_navigation_links(self, soup, chapter_mapping, current_chapter_url, index_file = None, novel_info_file = None, comments_file = None):
        """ナビゲーションリンクをローカルファイルへのリンクに修正（強化版 + 小説情報・感想対応）"""
        print("ナビゲーションリンクをローカル用に修正中...")
        
        # 1. 目次リンクの修正（複数のパターンに対応）
        index_patterns = [
            # 基本的な目次URLパターン
            lambda tag: tag.name == 'a' and tag.get('href') and '/novel/' in tag.get('href') and tag.get('href').endswith('/'),
            # 完全URL形式
            lambda tag: tag.name == 'a' and tag.get('href') == 'https://syosetu.org/novel/378070/',
            # 目次テキストを含むリンク
            lambda tag: tag.name == 'a' and '目次' in tag.get_text() and 'syosetu.org' in str(tag.get('href', ''))
        ]
        
        if index_file:
            for pattern in index_patterns:
                links = soup.find_all(pattern)
                for link in links:
                    old_href = link.get('href')
                    if old_href and old_href != index_file:
                        link['href'] = index_file
                        print(f"目次リンク修正: {old_href} -> {index_file}")
        
        # 2. 章間ナビゲーションリンクの修正
        # 全てのaタグを調査して、章URLパターンを検出
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link.get('href')
            if not href:
                continue
            
            # 絶対URLに正規化
            normalized_href = href
            if href.startswith('/'):
                normalized_href = self.base_url + href
            elif href.startswith('./') and href.endswith('.html'):
                # 相対パス形式を絶対URLに変換
                relative_part = href[2:]
                try:
                    novel_id = current_chapter_url.split('/')[-2]
                    normalized_href = f"{self.base_url}/novel/{novel_id}/{relative_part}"
                except:
                    continue
            elif not href.startswith('http') and not (href.endswith('.html') and any(char in href for char in ['第', '話'])):
                continue
            
            # チャプターマッピングに存在するかチェック
            if normalized_href in chapter_mapping:
                local_file = chapter_mapping[normalized_href]
                if href != local_file:
                    link['href'] = local_file
                    print(f"章リンク修正: {href} -> {local_file}")
            
            # 短縮形式のリンクも処理（第1話.html等）
            elif href.endswith('.html') and any(char in href for char in ['第', '話']):
                print(f"短縮形式リンク候補検出: {href}")
                # 短縮形式から章番号を抽出してマッチング
                import re
                chapter_match = re.search(r'第(\d+)話', href)
                if chapter_match:
                    chapter_num = chapter_match.group(1)
                    print(f"短縮リンク検出: {href}, 章番号: {chapter_num}")
                    
                    # chapter_mappingからマッチするファイル名を探す
                    found_mapping = False
                    for url, filename in chapter_mapping.items():
                        # URLから章番号を抽出
                        url_match = re.search(r'/(\d+)\.html', url)
                        if url_match and url_match.group(1) == chapter_num:
                            print(f"マッピング発見: URL={url}, 章番号={url_match.group(1)}, ファイル名={filename}")
                            link['href'] = filename
                            print(f"短縮リンク修正: {href} -> {filename}")
                            found_mapping = True
                            break
                    
                    if not found_mapping:
                        # 存在しないファイルへのリンクは無効化
                        print(f"存在しないファイルへのリンク: {href} -> 無効化")
                        link['href'] = 'javascript:void(0);'
                        link['class'] = link.get('class', []) + ['disabled']
                        link['style'] = 'color: #999; cursor: not-allowed; text-decoration: none;'
        
        # 3. 空リンクや無効なリンクの処理
        empty_links = soup.find_all('a', href='#')
        for link in empty_links:
            link_text = link.get_text().strip()
            if link_text == '×':
                # 「×」リンクはそのまま保持（元の状態を維持）
                print(f"×リンク保持: {link_text}")
            elif '次の話' in link_text:
                # 無効な「次の話」リンクを無効化（テキストは変更しない）
                link['href'] = 'javascript:void(0);'
                link['class'] = link.get('class', []) + ['disabled']
                link['style'] = 'color: #999; cursor: not-allowed; text-decoration: none;'
                print(f"無効な次の話リンク修正: {link_text} -> 無効化")
        
        # 4. 🆕 小説情報・感想ページへのリンク修正
        if novel_info_file or comments_file:
            info_and_comment_links = soup.find_all('a', href=True)
            for link in info_and_comment_links:
                href = link.get('href')
                if not href:
                    continue
                
                # 小説情報ページのリンク修正
                if novel_info_file and ('mode=ss_detail' in href or '小説情報' in link.get_text()):
                    link['href'] = novel_info_file
                    print(f"小説情報リンク修正: {href} -> {novel_info_file}")
                
                # 感想ページのリンク修正
                elif comments_file and ('mode=review' in href or '感想' in link.get_text()):
                    # 感想フォルダ内の最初のページへのリンクに修正
                    link['href'] = '感想/感想 - ページ1.html'
                    print(f"感想リンク修正: {href} -> 感想/感想 - ページ1.html")
        
        return soup
    
    def download_and_process_css(self, url, resources_dir):
        """CSSファイルをダウンロードして内部の画像参照も処理（強化版）"""
        try:
            # 絶対URLに変換
            if not url.startswith('http'):
                url = urljoin(self.base_url, url)
            
            # ファイル名を生成
            parsed = urlparse(url)
            filename = os.path.basename(parsed.path)
            if not filename or '.' not in filename:
                filename = f"style_{hash(url) % 10000}.css"
            
            print(f"CSS詳細処理中: {url}")
            
            # CSSファイルをダウンロード
            response = self.cloudscraper.get(url, timeout=10)
            response.raise_for_status()
            
            # 文字エンコーディングを明示的に設定
            response.encoding = 'utf-8'
            css_content = response.text
            
            # CSS内のすべてのリソース参照を処理
            import re
            
            # 1. url()参照を処理（背景画像、フォント等）- 完全なマッチングで処理
            import re
            
            def replace_url_func(match):
                full_match = match.group(0)  # url(...) 全体
                img_url = match.group(1)     # URL部分のみ
                
                if img_url.startswith('data:'):
                    return full_match  # データURLはそのまま
                
                original_img_url = img_url
                
                # 相対URLを絶対URLに変換
                if not img_url.startswith('http'):
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    elif img_url.startswith('/'):
                        base_domain = '/'.join(url.split('/')[:3])
                        img_url = base_domain + img_url
                    else:
                        # 相対パス
                        base_css_url = '/'.join(url.split('/')[:-1])
                        img_url = urljoin(base_css_url + '/', img_url)
                
                # URL正規化
                cleaned_url = img_url.split(')')[0]
                if '?' in cleaned_url:
                    cleaned_url = cleaned_url.split('?')[0]
                
                # 画像をダウンロード
                print(f"CSS内画像ダウンロード: {cleaned_url}")
                local_img = self.download_resource(cleaned_url, resources_dir)
                if local_img != cleaned_url:
                    browser_compatible_path = f"./{local_img}"
                    print(f"CSS内パス置換: {original_img_url} -> {browser_compatible_path}")
                    return full_match.replace(original_img_url, browser_compatible_path)
                else:
                    return full_match
            
            # 正規表現で url() を検出し、コールバック関数で置換
            css_content = re.sub(r'url\([\'"]?([^\'"]+?)[\'"]?\)', replace_url_func, css_content)
            
            # 2. @import文を処理
            imports = re.findall(r'@import\s+[\'"]([^\'"]+)[\'"]', css_content)
            for import_url in imports:
                if not import_url.startswith('http'):
                    if import_url.startswith('//'):
                        import_url = 'https:' + import_url
                    elif import_url.startswith('/'):
                        base_domain = '/'.join(url.split('/')[:3])
                        import_url = base_domain + import_url
                    else:
                        base_css_url = '/'.join(url.split('/')[:-1])
                        import_url = urljoin(base_css_url + '/', import_url)
                
                print(f"CSS @import処理: {import_url}")
                local_css = self.download_and_process_css(import_url, resources_dir)
                if local_css != import_url:
                    # @import文で正確に置換
                    browser_compatible_css = f"./{local_css}"
                    css_content = css_content.replace(f'@import "{import_url}"', f'@import "{browser_compatible_css}"')
                    css_content = css_content.replace(f"@import '{import_url}'", f"@import '{browser_compatible_css}'")
            
            # 3. @font-face内のsrc参照も処理（上記のurl()処理で既に処理済みなのでスキップ）
            # フォントは既に上記のurl()処理で処理されているため、重複処理を避ける
            
            # ローカルパスを作成
            local_path = os.path.join(resources_dir, filename)
            with open(local_path, 'w', encoding='utf-8') as f:
                f.write(css_content)
            
            print(f"CSS処理完了: {filename}")
            return filename
            
        except Exception as e:
            print(f"CSS処理エラー ({url}): {e}")
            return self.download_resource(url, resources_dir)  # フォールバック
        
    def extract_novel_info(self, soup):
        """小説の基本情報を抽出（2024年版ハーメルン対応）"""
        info = {}
        
        self.debug_log("小説情報抽出開始")
        
        # タイトル抽出（Gemini分析によるハーメルン特化セレクター）
        title_selectors = [
            # ★ Gemini発見：ハーメルンの数字クラス構造
            ('div', {'class': 'section1'}),  # タイトルセクション候補
            ('div', {'class': 'section2'}),  # タイトルセクション候補
            ('h1', {'class': lambda x: x and any(cls.startswith('section') for cls in x if isinstance(cls, str))}),
            # 2024年ハーメルン用
            ('h1', {'class': 'p-novel-title'}),
            ('h1', {'class': 'novel-title'}),
            ('div', {'class': 'p-novel-title'}),
            ('span', {'class': 'novel-title'}),
            # 従来のセレクター
            ('h1', {'class': 'title'}),
            ('h1', {'class': 'novel_title'}),
            ('div', {'class': 'novel_title'}),
            ('h1', {}),
            ('title', {})
        ]
        
        self.debug_log("タイトル抽出試行中...")
        for tag, attrs in title_selectors:
            self.debug_log(f"タイトルセレクター試行: {tag} {attrs}")
            title_elem = soup.find(tag, attrs) if attrs else soup.find(tag)
            if title_elem:
                title_text = title_elem.get_text(strip=True)
                # ハーメルンの場合、タイトルから余分な文字を除去
                if ' - ハーメルン' in title_text:
                    title_text = title_text.replace(' - ハーメルン', '')
                if title_text and title_text not in ['Unknown Title', '']:
                    info['title'] = title_text
                    self.debug_log(f"タイトル取得成功: {title_text}")
                    break
            else:
                self.debug_log(f"セレクター {tag} {attrs} で要素が見つかりませんでした")
        
        # 作者抽出（幅広いセレクター）
        author_selectors = [
            # 2024年ハーメルン用
            ('a', {'class': 'p-novel-author'}),
            ('span', {'class': 'p-novel-author'}),
            ('div', {'class': 'novel-author'}),
            ('a', {'class': 'author-link'}),
            # 従来のセレクター
            ('a', {'href': lambda x: x and '/user/' in x}),
            ('div', {'class': 'author'}),
            ('span', {'class': 'author'}),
            ('a', {'class': 'author'})
        ]
        
        self.debug_log("作者抽出試行中...")
        for tag, attrs in author_selectors:
            self.debug_log(f"作者セレクター試行: {tag} {attrs}")
            if callable(attrs.get('href')):
                author_elem = soup.find(tag, href=attrs['href'])
            else:
                author_elem = soup.find(tag, attrs)
            
            if author_elem:
                author_text = author_elem.get_text(strip=True)
                if author_text and author_text not in ['Unknown Author', '']:
                    info['author'] = author_text
                    self.debug_log(f"作者取得成功: {author_text}")
                    break
            else:
                self.debug_log(f"セレクター {tag} {attrs} で要素が見つかりませんでした")
        
        # 情報が取得できない場合の詳細調査
        if not info.get('title') or not info.get('author'):
            self.debug_log("基本情報取得失敗、詳細調査を実行", "WARNING")
            self.investigate_page_structure(soup)
        
        return info
        
    def investigate_page_structure(self, soup):
        """ページ構造を詳細調査"""
        self.debug_log("=== ページ構造詳細調査 ===")
        
        # 利用可能なh1タグ
        h1_tags = soup.find_all('h1')
        self.debug_log(f"h1タグ数: {len(h1_tags)}")
        for i, h1 in enumerate(h1_tags[:5]):
            classes = h1.get('class', [])
            text = h1.get_text(strip=True)[:50]
            self.debug_log(f"  h1[{i}]: class={classes}, text={text}...")
        
        # 利用可能なリンク
        links = soup.find_all('a', href=True)
        self.debug_log(f"リンク数: {len(links)}")
        user_links = [link for link in links if '/user/' in link.get('href', '')]
        self.debug_log(f"ユーザーリンク数: {len(user_links)}")
        for i, link in enumerate(user_links[:3]):
            classes = link.get('class', [])
            text = link.get_text(strip=True)[:30]
            href = link.get('href')
            self.debug_log(f"  userlink[{i}]: class={classes}, text={text}..., href={href}")
        
        # 特殊なクラス名を検索
        divs_with_class = soup.find_all('div', class_=True)
        unique_classes = set()
        for div in divs_with_class:
            for cls in div.get('class', []):
                if any(keyword in cls.lower() for keyword in ['title', 'author', 'novel', 'name']):
                    unique_classes.add(cls)
        
        self.debug_log(f"関連クラス名: {sorted(unique_classes)}")
        
        # spanタグもチェック
        spans_with_class = soup.find_all('span', class_=True)
        span_classes = set()
        for span in spans_with_class:
            for cls in span.get('class', []):
                if any(keyword in cls.lower() for keyword in ['title', 'author', 'novel', 'name']):
                    span_classes.add(cls)
        
        self.debug_log(f"関連spanクラス名: {sorted(span_classes)}")
        
    def extract_novel_info_url(self, soup):
        """目次ページから小説情報ページのURLを抽出"""
        try:
            # topicPathから小説情報リンクを検索
            topic_path = soup.find('ol', class_='topicPath')
            if topic_path:
                info_link = topic_path.find('a', href=lambda x: x and 'mode=ss_detail' in x)
                if info_link:
                    href = info_link.get('href')
                    if href.startswith('?'):
                        # 相対URLを絶対URLに変換
                        return f"https://syosetu.org/{href}"
                    elif href.startswith('//'):
                        # プロトコル相対URLをHTTPS絶対URLに変換
                        return f"https:{href}"
                    elif href.startswith('/'):
                        # ルート相対URLを絶対URLに変換
                        return f"https://syosetu.org{href}"
                    return href
            
            self.debug_log("小説情報URLが見つかりませんでした", "WARNING")
            return None
        except Exception as e:
            self.debug_log(f"小説情報URL抽出エラー: {e}", "ERROR")
            return None

    def extract_comments_url(self, soup):
        """目次ページから感想ページのURLを抽出"""
        try:
            # topicPathから感想リンクを検索（複数のパターンに対応）
            topic_path_selectors = [
                'ol.topicPath',
                'div.topicPath',
                '.topicPath'
            ]
            
            topic_path = None
            for selector in topic_path_selectors:
                topic_path = soup.select_one(selector)
                if topic_path:
                    break
            
            if topic_path:
                comments_link = topic_path.find('a', href=lambda x: x and 'mode=review' in x)
                if comments_link:
                    href = comments_link.get('href')
                    if href.startswith('?'):
                        # 相対URLを絶対URLに変換
                        return f"https://syosetu.org/{href}"
                    elif href.startswith('//'):
                        # プロトコル相対URLを絶対URLに変換
                        return f"https:{href}"
                    elif href.startswith('/'):
                        # パス相対URLを絶対URLに変換
                        return f"https://syosetu.org{href}"
                    return href
            
            self.debug_log("感想URLが見つかりませんでした", "WARNING")
            return None
        except Exception as e:
            self.debug_log(f"感想URL抽出エラー: {e}", "ERROR")
            return None

    def save_novel_info_page(self, info_url, output_dir, novel_title, index_file_name=None, comments_file_name=None, vertical_file_name=None):
        """小説情報ページを取得・保存"""
        try:
            self.debug_log(f"小説情報ページを取得中: {info_url}")
            
            # 小説情報ページを取得
            info_soup = self.get_page(info_url)
            if not info_soup:
                self.debug_log("小説情報ページの取得に失敗しました", "ERROR")
                return None
            
            # 保存前に小説情報ページのリンク修正
            info_soup = self.fix_novel_info_page_links(info_soup, index_file_name, comments_file_name, vertical_file_name)
            
            # 保存処理
            safe_title = re.sub(r'[<>:"/\\|?*]', '_', novel_title)
            info_filename = f"{safe_title} - 小説情報"
            
            info_file_path = self.save_complete_page(
                info_soup,
                info_url,
                info_filename,
                output_dir,
                info_url
            )
            
            if info_file_path:
                self.debug_log(f"小説情報ページ保存完了: {os.path.basename(info_file_path)}")
                return info_file_path
            else:
                self.debug_log("小説情報ページの保存に失敗しました", "ERROR")
                return None
                
        except Exception as e:
            self.debug_log(f"小説情報ページ保存エラー: {e}", "ERROR")
            return None
    
    def fix_novel_info_page_links(self, soup, index_file_name=None, comments_file_name=None, vertical_file_name=None):
        """小説情報ページのリンクを修正"""
        try:
            # 小説情報ページから感想ページへのリンクを修正
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                if not href:
                    continue
                
                # 感想ページへのリンクを修正
                if 'mode=review' in href:
                    # 感想フォルダ内の最初のページへのリンクに修正
                    link['href'] = '感想/感想 - ページ1.html'
                    self.debug_log(f"小説情報ページ感想リンク修正: {href} -> 感想/感想 - ページ1.html")
                
                # 目次ページへのリンクを修正
                elif '/novel/' in href and href.endswith('/'):
                    if index_file_name:
                        link['href'] = index_file_name
                        self.debug_log(f"小説情報ページ目次リンク修正: {href} -> {index_file_name}")
                    else:
                        link['href'] = '目次.html'
                        self.debug_log(f"小説情報ページ目次リンク修正: {href} -> 目次.html")
                
                # 小説本文ページへのリンクを修正（章ページ）
                elif '/novel/' in href and re.search(r'/\d+\.html', href):
                    # 章ページへのリンクは相対パスで修正
                    chapter_num = re.search(r'/(\d+)\.html', href)
                    if chapter_num:
                        chapter_title = f"第{chapter_num.group(1)}話"
                        link['href'] = f"{chapter_title}.html"
                        self.debug_log(f"小説情報ページ章リンク修正: {href} -> {chapter_title}.html")
                
                # 縦書きページへのリンクを修正
                elif 'mode=ss_detail3' in href and vertical_file_name:
                    link['href'] = vertical_file_name
                    self.debug_log(f"小説情報ページ縦書きリンク修正: {href} -> {vertical_file_name}")
            
            return soup
            
        except Exception as e:
            self.debug_log(f"小説情報ページリンク修正エラー: {e}", "ERROR")
            return soup

    def save_comments_page(self, comments_url, output_dir, novel_title, index_file_name=None, info_file_name=None):
        """🆕 感想ページを各ページ個別に保存（ハーメルン元構造保持）"""
        try:
            self.debug_log(f"感想ページを取得中: {comments_url}")
            
            # 感想保存フォルダを作成
            safe_title = re.sub(r'[<>:"/\\|?*]', '_', novel_title)
            comments_dir = os.path.join(output_dir, "感想")
            os.makedirs(comments_dir, exist_ok=True)
            self.debug_log(f"感想保存フォルダ作成: {comments_dir}")
            
            # 最初のページを取得してページネーション検出
            first_page_soup = self.get_page(comments_url)
            if not first_page_soup:
                self.debug_log("感想ページの取得に失敗しました", "ERROR")
                return None
            
            # ページネーションを検出
            page_links = self.detect_comments_pagination(first_page_soup, comments_url)
            self.debug_log(f"感想ページ数: {len(page_links)}ページ")
            
            saved_files = []
            
            # 各ページを個別に保存
            for page_num, page_url in enumerate(page_links, 1):
                self.debug_log(f"感想ページ {page_num}/{len(page_links)} を保存中: {page_url}")
                
                # ページを取得
                if page_num == 1:
                    page_soup = first_page_soup
                else:
                    time.sleep(2)  # サーバー負荷軽減
                    page_soup = self.get_page(page_url)
                    if not page_soup:
                        self.debug_log(f"感想ページ {page_num} の取得に失敗", "WARNING")
                        continue
                
                # ファイル名生成
                comments_filename = f"感想 - ページ{page_num}"
                
                # 個別ページを保存
                page_file_path = self.save_complete_page(
                    page_soup,
                    page_url,
                    comments_filename,
                    comments_dir,
                    page_url
                )
                
                if page_file_path:
                    saved_files.append(page_file_path)
                    self.debug_log(f"感想ページ{page_num}保存完了: {os.path.basename(page_file_path)}")
            
            if saved_files:
                # 感想ページ間のリンクを修正
                self.debug_log("感想ページ間のリンクを修正中...")
                self.fix_comments_page_links(saved_files, page_links, index_file_name, info_file_name)
                self.debug_log(f"感想ページ保存完了: {len(saved_files)}ページ保存")
                return saved_files[0]  # 最初のページのパスを返す（互換性のため）
            else:
                self.debug_log("感想ページの保存に失敗しました", "ERROR")
                return None
                
        except Exception as e:
            self.debug_log(f"感想ページ保存エラー: {e}", "ERROR")
            return None
    
    def fix_comments_page_links(self, saved_files, page_urls, index_file_name=None, info_file_name=None):
        """感想ページ間のリンクを修正"""
        try:
            # ページファイル名とURLのマッピングを作成
            page_mapping = {}
            for i, (file_path, url) in enumerate(zip(saved_files, page_urls), 1):
                page_mapping[url] = os.path.basename(file_path)
            
            # 各ページのリンクを修正
            for i, file_path in enumerate(saved_files):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                soup = BeautifulSoup(content, 'html.parser')
                
                # 感想ページのナビゲーションリンクを修正
                for link in soup.find_all('a', href=True):
                    href = link.get('href')
                    if not href:
                        continue
                    
                    # 感想ページのURL形式を検出（p=パラメータも含む、HTMLエスケープも考慮）
                    is_comments_page = (
                        'mode=review' in href or 
                        ('p=' in href and '/novel/' in href) or
                        ('&amp;p=' in href and '/novel/' in href)
                    )
                    
                    if is_comments_page:
                        # より精密なマッチングを実装
                        matched_file = self.find_matching_comments_page(href, page_mapping)
                        if matched_file:
                            link['href'] = matched_file
                            self.debug_log(f"感想ページリンク修正: {href} -> {matched_file}")
                    
                    # 目次ページへのリンクを修正
                    elif ('/novel/' in href and href.endswith('/')) or '目次' in link.get_text():
                        # 親ディレクトリの目次ページへのリンクに修正
                        if index_file_name:
                            link['href'] = f'../{index_file_name}'
                            self.debug_log(f"目次リンク修正: {href} -> ../{index_file_name}")
                        else:
                            link['href'] = '../目次.html'
                            self.debug_log(f"目次リンク修正: {href} -> ../目次.html")
                    
                    # 小説情報ページへのリンクを修正
                    elif 'mode=ss_detail' in href or '小説情報' in link.get_text():
                        # 親ディレクトリの小説情報ページへのリンクに修正
                        if info_file_name:
                            link['href'] = f'../{info_file_name}'
                            self.debug_log(f"小説情報リンク修正: {href} -> ../{info_file_name}")
                        else:
                            link['href'] = '../小説情報.html'
                            self.debug_log(f"小説情報リンク修正: {href} -> ../小説情報.html")
                
                # 修正されたコンテンツを保存
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(str(soup))
                
        except Exception as e:
            self.debug_log(f"感想ページリンク修正エラー: {e}", "ERROR")
    
    def find_matching_comments_page(self, href, page_mapping):
        """感想ページのURLから正確なローカルファイルを探す"""
        try:
            # HTMLエスケープを解除
            import html
            href = html.unescape(href)
            
            # クエリパラメータの修正
            if '?' not in href and ('&p=' in href or '&page=' in href):
                href = href.replace('&', '?', 1)
            
            # リンクからページ番号を抽出
            target_page_num = self.extract_page_number(href)
            
            # 基本URL（nid部分）を抽出
            target_base_url = self.extract_base_comments_url(href)
            
            # マッピングから対応するファイルを検索
            for original_url, local_file in page_mapping.items():
                original_page_num = self.extract_page_number(original_url)
                original_base_url = self.extract_base_comments_url(original_url)
                
                # 基本URLとページ番号が一致する場合
                if (target_base_url == original_base_url and 
                    target_page_num == original_page_num):
                    return local_file
            
            return None
            
        except Exception as e:
            self.debug_log(f"感想ページマッチングエラー: {e}", "ERROR")
            return None
    
    def extract_page_number(self, url):
        """URLからページ番号を抽出"""
        try:
            from urllib.parse import urlparse, parse_qs
            
            # URLをパース
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            
            # page または p パラメータからページ番号を取得
            if 'page' in params:
                return int(params['page'][0])
            elif 'p' in params:
                return int(params['p'][0])
            else:
                return 1  # デフォルトは1ページ目
                
        except Exception as e:
            self.debug_log(f"ページ番号抽出エラー: {e}", "DEBUG")
            return 1
    
    def extract_base_comments_url(self, url):
        """URLから基本URL（nid部分）を抽出"""
        try:
            from urllib.parse import urlparse, parse_qs
            
            # URLをパース
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            
            # 基本的なパラメータのみを保持
            base_params = {}
            if 'mode' in params:
                base_params['mode'] = params['mode'][0]
            if 'nid' in params:
                base_params['nid'] = params['nid'][0]
            
            # 基本URLを構築
            base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if base_params:
                param_str = '&'.join([f"{k}={v}" for k, v in base_params.items()])
                base_url += f"?{param_str}"
            
            return base_url
            
        except Exception as e:
            self.debug_log(f"基本URL抽出エラー: {e}", "ERROR")
            return url

    def get_all_comments_pages(self, base_comments_url):
        """🆕 複数ページの感想を全て取得して統合"""
        try:
            self.debug_log("感想ページのページネーション検出を開始")
            
            # 最初のページを取得
            first_page_soup = self.get_page(base_comments_url)
            if not first_page_soup:
                return None
            
            # ページネーションを検出
            page_links = self.detect_comments_pagination(first_page_soup, base_comments_url)
            
            if len(page_links) <= 1:
                # 単一ページの場合
                self.debug_log("感想は1ページのみです")
                return first_page_soup
            
            self.debug_log(f"感想ページ数: {len(page_links)}ページ")
            
            # 全ページを取得
            all_comments = []
            
            for page_num, page_url in enumerate(page_links, 1):
                self.debug_log(f"感想ページ {page_num}/{len(page_links)} を取得中: {page_url}")
                
                if page_num == 1:
                    # 最初のページは既に取得済み
                    page_soup = first_page_soup
                else:
                    # 2ページ目以降を取得
                    time.sleep(2)  # サーバー負荷軽減
                    page_soup = self.get_page(page_url)
                    if not page_soup:
                        self.debug_log(f"感想ページ {page_num} の取得に失敗", "WARNING")
                        continue
                
                # 感想コンテンツを抽出
                comments_content = self.extract_comments_content(page_soup)
                if comments_content:
                    all_comments.extend(comments_content)
            
            if not all_comments:
                self.debug_log("感想コンテンツが見つかりませんでした", "WARNING")
                return first_page_soup
            
            # 統合されたHTMLを作成
            integrated_soup = self.create_integrated_comments_page(first_page_soup, all_comments, len(page_links))
            self.debug_log(f"感想ページ統合完了: {len(all_comments)}件の感想を統合")
            
            return integrated_soup
            
        except Exception as e:
            self.debug_log(f"感想ページ統合エラー: {e}", "ERROR")
            return None

    def detect_comments_pagination(self, soup, base_url):
        """🆕 感想ページのページネーションを検出（改良版）"""
        try:
            page_links = []
            base_page_num = self.extract_page_number(base_url)
            max_page_num = 1
            
            # ページネーションの検出パターン
            pagination_selectors = [
                # 一般的なページネーション
                'div.pagination a',
                'div.pager a', 
                'div.page-nav a',
                # ハーメルン特有のパターン
                'a[href*="mode=review"]',
                'a[href*="&page="]',
                'a[href*="&p="]'
            ]
            
            all_pagination_links = []
            
            # すべてのselectorからページネーションリンクを収集
            for selector in pagination_selectors:
                pagination_links = soup.select(selector)
                if pagination_links:
                    self.debug_log(f"ページネーション発見: {selector} ({len(pagination_links)}個のリンク)")
                    all_pagination_links.extend(pagination_links)
            
            # 重複を除去
            unique_links = []
            seen_hrefs = set()
            for link in all_pagination_links:
                href = link.get('href')
                if href and href not in seen_hrefs:
                    seen_hrefs.add(href)
                    unique_links.append(link)
            
            # リンクからページURLを抽出
            for link in unique_links:
                href = link.get('href')
                link_text = link.get_text(strip=True)
                
                if href and ('page=' in href or 'p=' in href or 'mode=review' in href):
                    # 相対URLを絶対URLに変換
                    if href.startswith('?'):
                        # ?page=2 または ?p=2 形式
                        full_url = base_url.split('?')[0] + href
                    elif href.startswith('./'):
                        # ./?page=2 または ./?p=2 形式
                        full_url = base_url.split('?')[0] + href[2:]  # ./ を削除して処理
                    elif href.startswith('//'):
                        # プロトコル相対URLを絶対URLに変換
                        full_url = f"https:{href}"
                    elif href.startswith('/'):
                        # /path?page=2 または /path?p=2 形式
                        # クエリパラメータの修正が必要な場合
                        if '?' not in href and ('&p=' in href or '&page=' in href):
                            # &を最初の?に変換
                            href = href.replace('&', '?', 1)
                        full_url = 'https://syosetu.org' + href
                    elif href.startswith('http'):
                        # https://... 形式
                        full_url = href
                    else:
                        continue
                    
                    # ページ番号を抽出
                    page_num = self.extract_page_number(full_url)
                    max_page_num = max(max_page_num, page_num)
                    
                    # 重複チェック（ページ番号ベース）
                    if not any(self.extract_page_number(existing_url) == page_num for existing_url in page_links):
                        page_links.append(full_url)
                        self.debug_log(f"ページリンク追加: {link_text} -> {full_url} (ページ{page_num})")
                
                # 数字のリンクテキストからページ番号を推定
                elif link_text.isdigit():
                    page_num = int(link_text)
                    max_page_num = max(max_page_num, page_num)
                    
                    # ベースURLからページURLを構築
                    if 'p=' in base_url:
                        constructed_url = base_url.split('p=')[0] + f'p={page_num}'
                    elif 'page=' in base_url:
                        constructed_url = base_url.split('page=')[0] + f'page={page_num}'
                    else:
                        # デフォルトのパラメータ形式で構築
                        if '?' in base_url:
                            constructed_url = base_url + f'&p={page_num}'
                        else:
                            constructed_url = base_url + f'?p={page_num}'
                    
                    if not any(self.extract_page_number(existing_url) == page_num for existing_url in page_links):
                        page_links.append(constructed_url)
                        self.debug_log(f"数字リンクからページ構築: {link_text} -> {constructed_url} (ページ{page_num})")
            
            # 最大ページ番号を検出した場合、不足しているページを補完
            if max_page_num > len(page_links):
                self.debug_log(f"最大ページ番号 {max_page_num} を検出、不足ページを補完中...")
                
                # ベースURLのパラメータ形式を確認
                if 'p=' in base_url:
                    param_format = 'p='
                elif 'page=' in base_url:
                    param_format = 'page='
                else:
                    param_format = 'p='
                
                # 1からmax_page_numまでのすべてのページURLを生成
                for page_num in range(1, max_page_num + 1):
                    if not any(self.extract_page_number(existing_url) == page_num for existing_url in page_links):
                        if param_format in base_url:
                            constructed_url = base_url.split(param_format)[0] + f'{param_format}{page_num}'
                        else:
                            # デフォルトのパラメータ形式で構築
                            if '?' in base_url:
                                constructed_url = base_url + f'&{param_format}{page_num}'
                            else:
                                constructed_url = base_url + f'?{param_format}{page_num}'
                        
                        page_links.append(constructed_url)
                        self.debug_log(f"補完ページ追加: ページ{page_num} -> {constructed_url}")
            
            # ベースURLがリストに含まれていない場合は追加
            if not any(self.extract_page_number(url) == base_page_num for url in page_links):
                page_links.append(base_url)
            
            # ページ番号順にソート
            page_links.sort(key=lambda url: self.extract_page_number(url))
            
            self.debug_log(f"検出されたページ: {len(page_links)}ページ (最大ページ番号: {max_page_num})")
            for i, url in enumerate(page_links, 1):
                self.debug_log(f"  ページ{i}: {url}")
            
            return page_links
            
        except Exception as e:
            self.debug_log(f"ページネーション検出エラー: {e}", "ERROR")
            return [base_url]

    def extract_comments_content(self, soup):
        """🆕 感想コンテンツを抽出"""
        try:
            comments = []
            
            # 感想コンテンツの検出パターン（ハーメルンの実際の構造に対応）
            comment_selectors = [
                'div[id*="review"]',     # ハーメルンの実際の構造: div.review_7612892
                'div.review-item',       # 一般的な構造
                'div.comment-item', 
                'div.impression',
                'tr[id*="review"]',      # テーブル形式の感想
                'div[class*="review_"]', # review_で始まるクラス
                'div[class*="review"]',
                'div[class*="comment"]'
            ]
            
            for selector in comment_selectors:
                comment_elements = soup.select(selector)
                if comment_elements:
                    self.debug_log(f"感想要素発見: {selector} ({len(comment_elements)}件)")
                    comments.extend(comment_elements)
                    break
            
            # フォールバック: テーブル行から感想を抽出
            if not comments:
                table_rows = soup.find_all('tr')
                for row in table_rows:
                    # 感想らしいテキストを含む行を検出
                    text = row.get_text().strip()
                    if len(text) > 20 and any(keyword in text for keyword in ['面白', '良い', '素晴らしい', '感動', '続き']):
                        comments.append(row)
            
            self.debug_log(f"抽出された感想: {len(comments)}件")
            return comments
            
        except Exception as e:
            self.debug_log(f"感想コンテンツ抽出エラー: {e}", "ERROR")
            return []

    def create_integrated_comments_page(self, base_soup, all_comments, total_pages):
        """🆕 統合された感想ページを作成"""
        try:
            # ベースHTMLをコピー
            integrated_soup = copy.deepcopy(base_soup)
            
            # 既存の感想コンテンツを削除（ハーメルンの実際の構造に対応）
            for selector in ['div[id*="review"]', 'div.review-item', 'div.comment-item', 'tr[id*="review"]']:
                existing_comments = integrated_soup.select(selector)
                for comment in existing_comments:
                    comment.decompose()
            
            # 感想を挿入する場所を特定
            content_area = integrated_soup.find('div', class_='content') or integrated_soup.find('div', class_='main') or integrated_soup.find('body')
            
            if content_area and all_comments:
                # 全感想を挿入
                for comment in all_comments:
                    if comment:  # Noneチェック
                        content_area.append(copy.deepcopy(comment))
            
            self.debug_log("感想ページ統合完了")
            return integrated_soup
            
        except Exception as e:
            self.debug_log(f"感想ページ統合作成エラー: {e}", "ERROR")
            import traceback
            self.debug_log(f"統合エラー詳細: {traceback.format_exc()}", "ERROR")
            return base_soup
        
    def get_chapter_links(self, soup, base_novel_url):
        """章のリンクを抽出（ハーメルン特化版）"""
        chapter_links = []
        
        print("章リンクを検索中...")
        
        # 現在の作品IDを抽出
        novel_id_match = re.search(r'/novel/(\d+)', base_novel_url)
        if not novel_id_match:
            print("作品IDの抽出に失敗しました")
            return []
        
        novel_id = novel_id_match.group(1)
        print(f"対象作品ID: {novel_id}")
        
        # ハーメルン特有のセレクターで章リンクを検索（作品ID限定）
        chapter_selectors = [
            # ハーメルンの一般的な章リスト
            ('div', {'class': 'chapter_list'}),
            ('ul', {'class': 'episode_list'}),
            ('div', {'class': 'episode_list'}),
            # 特定作品の章のみ（作品ID限定）
            ('a', {'href': lambda x: x and f'/novel/{novel_id}/' in x and x.count('/') >= 4 and x.endswith('.html')}),
            # 相対パス形式の章リンク（./2.html, ./3.html等）
            ('a', {'href': lambda x: x and re.match(r'\./\d+\.html$', x)}),
            ('li', {'class': 'chapter'}),
            ('div', {'class': 'novel_sublist'})
        ]
        
        for tag, attrs in chapter_selectors:
            print(f"セレクター試行: {tag} {attrs}")
            
            if callable(attrs.get('href')):
                elements = soup.find_all(tag, href=attrs['href'])
            else:
                elements = soup.find_all(tag, attrs)
            
            print(f"見つかった要素数: {len(elements)}")
            
            for element in elements:
                if tag == 'a':
                    href = element.get('href')
                    title = element.get_text(strip=True)
                    if href:
                        full_url = urljoin(base_novel_url, href)
                        
                        # 相対パス形式の章リンクの場合、作品ID検証をスキップして直接追加
                        if re.match(r'\./\d+\.html$', href):
                            if full_url not in chapter_links:
                                chapter_links.append(full_url)
                                print(f"✓ 章リンク追加（相対パス）: {title[:30]}... -> {full_url}")
                            else:
                                print(f"重複スキップ: {full_url}")
                        # 絶対パス形式の場合は作品ID検証
                        elif f'/novel/{novel_id}/' in full_url:
                            if full_url not in chapter_links:
                                chapter_links.append(full_url)
                                print(f"✓ 章リンク追加（絶対パス）: {title[:30]}... -> {full_url}")
                            else:
                                print(f"重複スキップ: {full_url}")
                        else:
                            print(f"✗ 作品ID不一致でスキップ: {full_url} (期待ID: {novel_id})")
                else:
                    # div や ul の場合は内部のaタグを探す
                    links = element.find_all('a', href=True)
                    print(f"コンテナ内のリンク数: {len(links)}")
                    for link in links:
                        href = link.get('href')
                        if href and '/novel/' in href:
                            title = link.get_text(strip=True)
                            full_url = urljoin(self.base_url, href)
                            # 作品ID検証
                            if f'/novel/{novel_id}/' in full_url:
                                if full_url not in chapter_links:
                                    chapter_links.append(full_url)
                                    print(f"✓ 章リンク追加: {title[:30]}... -> {full_url}")
                                else:
                                    print(f"重複スキップ: {full_url}")
                            else:
                                print(f"✗ 作品ID不一致でスキップ: {full_url} (期待ID: {novel_id})")
        
        # 通常のリンク検索もフォールバック（作品ID検証付き）
        if not chapter_links:
            print("通常のリンク検索に切り替え...")
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                text = link.get_text(strip=True)
                
                # 相対パス形式の章リンクもチェック
                if re.match(r'\./\d+\.html$', href):
                    full_url = urljoin(base_novel_url, href)
                    if full_url not in chapter_links:
                        chapter_links.append(full_url)
                        print(f"フォールバック章リンク（相対パス）: {text[:30]}... -> {full_url}")
                    else:
                        print(f"重複スキップ: {full_url}")
                # より厳密な章リンクの条件（作品ID検証を含む）
                elif (href and '/novel/' in href and 
                    len(href.split('/')) >= 4 and 
                    href != base_novel_url and
                    not any(x in href for x in ['user', 'tag', 'search', 'ranking'])):
                    
                    full_url = urljoin(self.base_url, href)
                    
                    # 作品ID検証を追加
                    if f'/novel/{novel_id}/' in full_url:
                        if full_url not in chapter_links:
                            chapter_links.append(full_url)
                            print(f"フォールバック章リンク（絶対パス）: {text[:30]}... -> {full_url}")
                        else:
                            print(f"重複スキップ: {full_url}")
                    else:
                        print(f"✗ フォールバック作品ID不一致でスキップ: {full_url} (期待ID: {novel_id})")
        
        # 重複削除と並び順確認
        unique_links = []
        for link in chapter_links:
            if link not in unique_links:
                unique_links.append(link)
        
        print(f"最終的な章数: {len(unique_links)}")
        return unique_links
        
    def create_complete_html(self, title, author, chapters, output_dir):
        """完全なHTMLファイルを作成"""
        
        # メインHTMLテンプレート
        html_template = f"""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html lang="ja">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - ハーメルン（ローカル保存版）</title>
    <style>
        body {{
            font-family: 'Helvetica Neue', Arial, 'Hiragino Kaku Gothic ProN', 'Hiragino Sans', Meiryo, sans-serif;
            line-height: 1.8;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            background-color: #fafafa;
        }}
        .header {{
            border-bottom: 2px solid #ddd;
            padding-bottom: 20px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .title {{
            font-size: 2.5em;
            color: #333;
            margin-bottom: 10px;
        }}
        .author {{
            font-size: 1.3em;
            color: #666;
            margin-bottom: 20px;
        }}
        .navigation {{
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        .nav-title {{
            font-size: 1.5em;
            margin-bottom: 15px;
            color: #444;
        }}
        .chapter-nav {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}
        .chapter-link {{
            background-color: #007acc;
            color: white;
            padding: 8px 15px;
            text-decoration: none;
            border-radius: 3px;
            font-size: 0.9em;
        }}
        .chapter-link:hover {{
            background-color: #005a9e;
        }}
        .content {{
            background-color: white;
            padding: 30px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .chapter {{
            margin-bottom: 50px;
            padding-bottom: 30px;
            border-bottom: 1px solid #eee;
        }}
        .chapter:last-child {{
            border-bottom: none;
        }}
        .chapter-title {{
            font-size: 1.8em;
            color: #444;
            border-left: 4px solid #007acc;
            padding-left: 15px;
            margin-bottom: 20px;
            scroll-margin-top: 20px;
        }}
        .chapter-content {{
            font-size: 1.1em;
            line-height: 1.9;
        }}
        .chapter-content p {{
            margin-bottom: 15px;
            text-indent: 1em;
        }}
        .back-to-top {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            background-color: #007acc;
            color: white;
            padding: 10px 15px;
            border-radius: 50%;
            text-decoration: none;
            font-size: 1.2em;
        }}
        .back-to-top:hover {{
            background-color: #005a9e;
        }}
        @media (max-width: 768px) {{
            .chapter-nav {{
                flex-direction: column;
            }}
            .chapter-link {{
                text-align: center;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1 class="title">{title}</h1>
        <div class="author">作者: {author}</div>
    </div>
    
    <div class="navigation">
        <div class="nav-title">目次</div>
        <div class="chapter-nav">
            {self.create_chapter_navigation(chapters)}
        </div>
    </div>
    
    <div class="content">
        {self.create_chapters_html(chapters)}
    </div>
    
    <a href="#" class="back-to-top">↑</a>
    
    <script>
        // スムーススクロール
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function (e) {{
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {{
                    target.scrollIntoView({{
                        behavior: 'smooth'
                    }});
                }}
            }});
        }});
        
        // トップに戻るボタン
        document.querySelector('.back-to-top').addEventListener('click', function(e) {{
            e.preventDefault();
            window.scrollTo({{
                top: 0,
                behavior: 'smooth'
            }});
        }});
    </script>
</body>
</html>"""
        
        return html_template
        
    def create_chapter_navigation(self, chapters):
        """章のナビゲーションを作成"""
        nav_html = []
        for i, chapter in enumerate(chapters, 1):
            title = chapter.get('title', f'第{i}章')
            nav_html.append(f'<a href="#chapter-{i}" class="chapter-link">{title}</a>')
        return '\n'.join(nav_html)
        
    def create_chapters_html(self, chapters):
        """章のHTMLを作成（ハーメルン風）"""
        chapters_html = []
        for i, chapter in enumerate(chapters, 1):
            title = chapter.get('title', f'第{i}章')
            content = chapter.get('content', '')
            
            # ハーメルン風の章構造
            chapter_html = f'''
            <div id="chapter-{i}" class="chapter-separator">
                <h2>{title}</h2>
                <br/>
                <div>
                    <div id="honbun">
                        {content}
                    </div>
                </div>
            </div>'''
            chapters_html.append(chapter_html)
        return '\n'.join(chapters_html)
        
    def extract_chapter_content(self, soup, chapter_url):
        """章の本文を抽出（2024年版ハーメルン対応）"""
        self.debug_log(f"本文抽出開始: {chapter_url}")
        
        # 2024年ハーメルン特有の本文セレクター（強化版）
        content_selectors = [
            # ★ 実際のハーメルン構造（2024年最新）
            ('div', {'id': 'honbun'}),  # ← これが実際の本文ID！
            ('div', {'id': 'entry_box'}),  # 本文を含む外側のコンテナ
            # フォールバック用の古い構造
            ('div', {'class': 'section3'}),
            ('div', {'class': 'section1'}),
            ('div', {'class': 'section2'}),
            ('div', {'class': 'section4'}),
            ('div', {'class': 'section5'}),
            ('div', {'class': 'section6'}),
            ('div', {'class': 'section7'}),
            ('div', {'class': 'section8'}),
            ('div', {'class': 'section9'}),
            # 数字付きsectionクラスのパターンマッチング
            ('div', {'class': lambda x: x and any(cls.startswith('section') and len(cls) > 7 and cls[7:].isdigit() for cls in x if isinstance(cls, str))}),
            # 2024年ハーメルン用の新しいセレクター
            ('div', {'class': 'p-novel-text'}),
            ('div', {'class': 'novel-text'}),
            ('section', {'class': 'p-novel-text'}),
            ('div', {'class': 'p-chapter-text'}),
            ('div', {'class': 'chapter-text'}),
            ('div', {'class': 'p-story-text'}),
            ('div', {'class': 'story-text'}),
            ('div', {'class': 'episode-text'}),
            ('div', {'class': 'p-episode-text'}),
            ('div', {'class': 'p-content-text'}),
            ('div', {'class': 'content-text'}),
            # IDベースのセレクター
            ('div', {'id': 'novel_body'}),
            ('div', {'id': 'main_text'}),
            ('div', {'id': 'chapter_body'}),
            ('div', {'id': 'story_body'}),
            ('div', {'id': 'content_body'}),
            ('div', {'id': 'episode_body'}),
            # 従来のハーメルン本文クラス
            ('div', {'class': 'novel_body'}),
            ('div', {'class': 'novel_view'}),
            ('div', {'class': 'novel_content'}),
            ('div', {'class': 'chapter_body'}),
            ('div', {'class': 'ss_body'}),
            ('div', {'class': 'contents'}),
            ('div', {'class': 'main_content'}),
            ('div', {'class': 'story_content'}),
            # より一般的なセレクター
            ('article', {'class': None}),
            ('main', {'class': None}),
            ('section', {'class': None}),
            # フォールバック（パターンマッチング）
            ('div', {'class': lambda x: x and any(keyword in ' '.join(x).lower() for keyword in ['body', 'content', 'text', 'story', 'chapter', 'episode', 'novel'])}),
            # 最後の手段：大きなdivタグ（テキストが多い）
            ('div', {'data-content': 'main'}),
            ('div', {'role': 'main'}),
        ]
        
        for tag, attrs in content_selectors:
            self.debug_log(f"本文セレクター試行: {tag} {attrs}")
            
            try:
                if callable(attrs.get('class')):
                    elements = soup.find_all(tag, class_=attrs['class'])
                elif callable(attrs.get('id')):
                    elements = soup.find_all(tag, id=attrs['id'])
                elif attrs:
                    elements = soup.find_all(tag, attrs)
                else:
                    elements = soup.find_all(tag)
                
                self.debug_log(f"見つかった要素数: {len(elements)}")
                
                for element in elements:
                    content_text = element.get_text(strip=True)
                    content_length = len(content_text)
                    
                    # より詳細な条件チェック
                    if content_length > 50:  # 基準を緩和（短い章にも対応）
                        # 本文らしい内容かチェック
                        if self.is_likely_novel_content(content_text):
                            self.debug_log(f"本文取得成功: {content_length}文字")
                            # 完全な見た目を保持するため、元のHTML構造を保持
                            return self.preserve_original_formatting(element)
                        else:
                            self.debug_log(f"本文候補だが内容が適切でない: {content_length}文字")
                    else:
                        self.debug_log(f"要素が短すぎます: {content_length}文字")
                        
            except Exception as e:
                self.debug_log(f"セレクター試行エラー: {e}", "ERROR")
        
        self.debug_log("本文取得失敗: 適切な要素が見つかりませんでした", "WARNING")
        
        # 詳細調査を実行
        self.investigate_content_structure(soup)
        
        # 最後の手段：最も長いテキストを含む要素を選択
        self.debug_log("最後の手段：最も長いテキスト要素を検索")
        longest_element = None
        longest_length = 0
        
        for div in soup.find_all('div'):
            content_text = div.get_text(strip=True)
            if len(content_text) > longest_length and len(content_text) > 100:
                # 明らかにナビゲーション要素でないかチェック
                if not any(keyword in content_text for keyword in ['ナビゲーション', 'メニュー', 'ヘッダー', 'フッター']):
                    longest_element = div
                    longest_length = len(content_text)
        
        if longest_element:
            self.debug_log(f"最長テキスト要素を使用: {longest_length}文字")
            return self.preserve_original_formatting(longest_element)
        
        return ""
        
    def preserve_original_formatting(self, element):
        """元のHTML構造を保持して見た目を完全再現"""
        # 元のHTMLタグを保持
        html_content = str(element)
        
        # 不要な属性を削除（プライバシー保護のため）
        import re
        # onclick, onload等のイベントハンドラーを削除
        html_content = re.sub(r'\s*on\w+\s*=\s*["\'][^"\'>]*["\']', '', html_content)
        # data-track等のトラッキング属性を削除
        html_content = re.sub(r'\s*data-track\w*\s*=\s*["\'][^"\'>]*["\']', '', html_content)
        
        self.debug_log(f"元のフォーマットを保持: {len(html_content)}バイト")
        return html_content
        
    def is_likely_novel_content(self, text):
        """テキストが小説の本文らしいかチェック（強化版）"""
        # 基本的な長さチェック（より柔軟に）
        if len(text) < 30:  # さらに緩和
            return False
        
        # ナビゲーション要素や不要な要素を除外
        exclusion_keywords = [
            'ナビゲーション', 'メニュー', 'ヘッダー', 'フッター',
            'サイドバー', '広告', 'アドバタイズ', 'コメント',
            'ランキング', 'お知らせ', '利用規約', '検索',
            'ログイン', 'マイページ', 'ブックマーク',
            'タグ一覧', 'カテゴリ', 'プロフィール',
            'フォロー', 'いいね', 'シェア', 'ツイート',
            'コピー', 'URL', 'リンク', 'ソーシャル'
        ]
        
        for keyword in exclusion_keywords:
            if keyword in text:
                self.debug_log(f"除外キーワード検出: {keyword}")
                return False
        
        # 小説らしい要素をチェック（より柔軟に）
        novel_indicators = [
            '。', '「', '」', 'だ', 'である', 'です', 'ます',
            'した', 'する', 'その', 'この', 'あの', 'が', 'を', 'に', 'は', 'で'
        ]
        
        indicator_count = sum(1 for indicator in novel_indicators if indicator in text)
        if indicator_count < 2:  # 3→2に緩和
            self.debug_log(f"小説らしい要素が少ない: {indicator_count}/{len(novel_indicators)}")
            return False
        
        # ★ ハーメルンの作品説明文は本文ではない（除外）
        if ('総合評価：' in text or '評価：' in text or '連載：' in text or 
            '更新日時：' in text or '小説情報' in text or 'href="//syosetu.org/' in str(text)):
            self.debug_log("ハーメルン特有の作品説明文として除外")
            return False
        
        self.debug_log(f"小説コンテンツとして認識: {indicator_count}個の指標を確認")
        return True
        
    def investigate_content_structure(self, soup):
        """本文構造を詳細調査"""
        self.debug_log("=== 本文構造詳細調査 ===")
        
        # テキスト量の多い要素を検索
        text_elements = []
        for element in soup.find_all(['div', 'section', 'article', 'main', 'p']):
            text = element.get_text(strip=True)
            if len(text) > 50:
                text_elements.append({
                    'tag': element.name,
                    'class': element.get('class', []),
                    'id': element.get('id', ''),
                    'length': len(text),
                    'preview': text[:100] + '...' if len(text) > 100 else text
                })
        
        # 長さ順でソート
        text_elements.sort(key=lambda x: x['length'], reverse=True)
        
        self.debug_log(f"テキスト要素上位5件:")
        for i, elem in enumerate(text_elements[:5]):
            self.debug_log(f"  [{i+1}] {elem['tag']} class={elem['class']} id={elem['id']} length={elem['length']}")
            self.debug_log(f"      preview: {elem['preview']}")
        
        # クラス名パターン分析
        all_classes = set()
        for div in soup.find_all('div', class_=True):
            all_classes.update(div.get('class', []))
        
        content_related_classes = [cls for cls in all_classes 
                                 if any(keyword in cls.lower() 
                                       for keyword in ['text', 'content', 'body', 'story', 'novel', 'chapter', 'section'])]
        
        self.debug_log(f"本文関連クラス名候補: {sorted(content_related_classes)}")
    
    def process_single_chapter(self, chapter_url):
        """単一の章ページを完全保存"""
        print(f"=== 単話処理モード ===")
        print(f"URL: {chapter_url}")
        soup = self.get_page(chapter_url)
        
        if not soup:
            print("章ページの取得に失敗しました")
            return None
        
        # タイトルを簡単に抽出（titleタグから）
        title = soup.title.string if soup.title else "章ページ"
        print(f"ページタイトル: {title}")
        
        # #honbun要素の存在を確認
        honbun_element = soup.find('div', {'id': 'honbun'})
        if honbun_element:
            print(f"#honbun要素を発見: {len(honbun_element.get_text(strip=True))}文字")
            self.debug_log(f"#honbun要素内容プレビュー: {honbun_element.get_text(strip=True)[:200]}...")
        else:
            print("警告: #honbun要素が見つかりません")
            self.debug_log("警告: #honbun要素が見つかりません - 構造調査を実行")
            # ページ構造を調査
            all_divs = soup.find_all('div', id=True)
            print(f"ID付きdiv要素数: {len(all_divs)}")
            for div in all_divs[:10]:  # 最初の10個を表示
                div_id = div.get('id')
                text_preview = div.get_text(strip=True)[:50]
                print(f"  ID: {div_id}, テキスト: {text_preview}...")
        
        # 保存ディレクトリを作成（ブラウザ互換形式）
        safe_title = re.sub(r'[<>:"/\\|?*]', '_', title)
        output_dir = os.path.join("saved_novels", safe_title)
        os.makedirs(output_dir, exist_ok=True)
        
        # ブラウザ互換のリソースディレクトリ名を設定
        self.browser_compatible_name = safe_title + "_files"
        
        # 完全なページとして保存（構造をそのまま保持）
        base_url = "https://syosetu.org"
        safe_title = re.sub(r'[<>:"/\\|?*]', '_', title)
        output_file = self.save_complete_page(soup, base_url, safe_title, output_dir, chapter_url)
        print(f"完全なページとして保存: 1ページ")
        
        return output_file
    
    def save_complete_page(self, soup, base_url, 
                          title, save_dir, page_url):
        """ページを完全な形で保存（ブラウザ保存と同等）"""
        print("=== ブラウザレベル完全保存開始 ===")
        
        # ブラウザ互換リソースディレクトリ名を取得
        resources_dir_name = getattr(self, 'browser_compatible_name', 'resources')
        
        # リソースを処理してローカル保存
        soup = self.process_html_resources(soup, save_dir)
        
        # ブラウザ保存のように、元URLをコメントとして追加
        html_tag = soup.find('html')
        if html_tag:
            from bs4 import Comment
            comment = Comment(f' saved from url=({len(page_url):04d}){page_url} ')
            html_tag.insert(0, comment)
        
        # ベースURLを設定
        base_url = '/'.join(page_url.split('/')[:3])  # https://syosetu.org
        
        # 相対リンクを絶対パスに変換（ブラウザ保存と同様）
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href:
                if href.startswith('//'):
                    link['href'] = 'https:' + href
                elif href.startswith('/') and not href.startswith('//'):
                    link['href'] = base_url + href
                elif href.startswith('./'):
                    # 相対パスを絶対パスに変換
                    current_dir = '/'.join(page_url.split('/')[:-1])
                    link['href'] = current_dir + '/' + href[2:]
        
        # すべての画像のsrcを絶対パスに変換
        for img in soup.find_all('img', src=True):
            src = img.get('src')
            if src and not src.startswith('./' + resources_dir_name + '/'):  # 既にローカル化されていない場合
                if src.startswith('//'):
                    img['src'] = 'https:' + src
                elif src.startswith('/') and not src.startswith('//'):
                    img['src'] = base_url + src
        
        # CSS や JS の参照も同様に処理
        for link in soup.find_all('link', href=True):
            href = link.get('href')
            if href and not href.startswith('./' + resources_dir_name + '/'):
                if href.startswith('//'):
                    link['href'] = 'https:' + href
                elif href.startswith('/') and not href.startswith('//'):
                    link['href'] = base_url + href
        
        for script in soup.find_all('script', src=True):
            src = script.get('src')
            if src and not src.startswith('./' + resources_dir_name + '/'):
                if src.startswith('//'):
                    script['src'] = 'https:' + src
                elif src.startswith('/') and not src.startswith('//'):
                    script['src'] = base_url + src
        
        # メタ情報を保持（ブラウザ保存のように）
        head = soup.find('head')
        if head:
            # 保存日時を追加
            from datetime import datetime
            save_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            meta_save = soup.new_tag('meta')
            meta_save['name'] = 'save-date'
            meta_save['content'] = save_time
            head.append(meta_save)
            
            # 保存元URLを追加
            meta_source = soup.new_tag('meta')
            meta_source['name'] = 'source-url'
            meta_source['content'] = page_url
            head.append(meta_source)
        
        # 完全なHTMLとして保存
        safe_filename = re.sub(r'[<>:"/\\|?*]', '_', title)
        output_file = os.path.join(save_dir, f"{safe_filename}.html")
        
        # UTF-8 BOMを含めてブラウザ互換性を向上
        html_content = str(soup)
        
        with open(output_file, 'w', encoding='utf-8-sig') as f:
            f.write(html_content)
        
        print(f"=== ブラウザレベル完全保存完了: {output_file} ===")
        return output_file
        
    def scrape_novel(self, novel_url):
        """小説全体をスクレイピングして保存（完全モード一本化）"""
        print(f"=== 小説スクレイピング開始 ===")
        print(f"URL: {novel_url}")
        
        # サーバー負荷軽減のための初期待機
        time.sleep(2)
        
        # 章ページかどうかをチェック（例: /novel/378070/2.html）
        is_chapter_page = bool(re.search(r'/novel/\d+/\d+\.html$', novel_url))
        print(f"章ページ判定: {is_chapter_page}")
        
        if is_chapter_page:
            print("章ページを検出しました。目次ページから全話取得を開始します。")
            # 章ページのURLから目次ページのURLを構築
            # 例: https://syosetu.org/novel/378070/2.html → https://syosetu.org/novel/378070/
            match = re.search(r'(https?://[^/]+/novel/\d+)/', novel_url)
            print(f"URL正規表現マッチ結果: {match}")
            if match:
                index_url = match.group(1) + '/'
                print(f"目次ページURL: {index_url}")
                print(f"元のURL: {novel_url}")
                print(f"URL比較: {index_url} != {novel_url} = {index_url != novel_url}")
                
                # 無限ループ防止：現在のURLが既に目次ページでないことを確認
                if index_url != novel_url:
                    print("目次ページから全話取得を実行します...")
                    # 目次ページから全話取得を実行
                    return self.scrape_novel(index_url)
                else:
                    print("既に目次ページです。通常処理を続行します。")
            else:
                print("目次ページURLの構築に失敗しました。単話処理に切り替えます。")
                return self.process_single_chapter(novel_url)
        
        # メインページを取得
        soup = self.get_page(novel_url)
            
        if not soup:
            print("メインページの取得に失敗しました")
            return None
            
        # 小説情報を抽出
        novel_info = self.extract_novel_info(soup)
        title = novel_info.get('title', 'Unknown Title')
        author = novel_info.get('author', 'Unknown Author')
        
        print(f"タイトル: {title}")
        print(f"作者: {author}")
        
        # 保存ディレクトリを作成
        safe_title = re.sub(r'[<>:"/\\|?*]', '_', title)
        output_dir = os.path.join("saved_novels", safe_title)
        os.makedirs(output_dir, exist_ok=True)
        
        # 目次ページを保存（複数章がある場合）
        index_file_path = None
        
        # 章リンクを取得
        chapter_links = self.get_chapter_links(soup, novel_url)
        print(f"章数: {len(chapter_links)}")
        
        # 小説情報・感想ファイル名の初期化（章処理で使用するため事前に定義）
        info_file_name = None
        comments_file_name = None
        
        # 目次ページの保存とリソースファイルのダウンロード
        if len(chapter_links) > 1:
            print("目次ページを保存中...")
            # 目次ページを保存
            index_file_path = self.save_complete_page(
                soup, 
                novel_url,
                f"{safe_title} - 目次",
                output_dir, 
                novel_url
            )
            if index_file_path:
                print(f"📖 目次ページ保存完了: {os.path.basename(index_file_path)}")
            
            print("リソースファイル（CSS、JS、画像等）をダウンロード中...")
            # リソースダウンロードのみ実行（各章ではリソース再処理をスキップ）
            self.process_html_resources(soup, output_dir)
            print("📁 リソースファイルのダウンロードが完了しました。各章ではリソース再処理をスキップします。")
            
            # 🆕 新機能: 小説情報・感想保存（フラグで制御）
            
            # 感想ページを先に保存（小説情報ページから参照するため）
            if self.enable_comments_saving:
                print("感想ページを保存中...")
                comments_url = self.extract_comments_url(soup)
                if comments_url:
                    # index_file_pathが定義されていない場合は単一ページなので None を渡す
                    index_file_name = os.path.basename(index_file_path) if index_file_path else None
                    comments_file_path = self.save_comments_page(comments_url, output_dir, title, index_file_name, info_file_name)
                    if comments_file_path:
                        comments_file_name = os.path.basename(comments_file_path)
                        print(f"💬 感想ページ保存完了: {comments_file_name}")
                    else:
                        print("⚠️ 感想ページの保存に失敗しました")
                        comments_file_name = None
                else:
                    print("⚠️ 感想ページのURLが見つかりませんでした")
                    comments_file_name = None
            else:
                comments_file_name = None
            
            if self.enable_novel_info_saving:
                print("小説情報ページを保存中...")
                info_url = self.extract_novel_info_url(soup)
                if info_url:
                    # index_file_pathが定義されていない場合は単一ページなので None を渡す
                    index_file_name = os.path.basename(index_file_path) if index_file_path else None
                    info_file_path = self.save_novel_info_page(info_url, output_dir, title, index_file_name, comments_file_name)
                    if info_file_path:
                        info_file_name = os.path.basename(info_file_path)
                        print(f"📝 小説情報ページ保存完了: {info_file_name}")
                        
                        # 感想ページのリンクを再修正（小説情報ページへのリンクを追加）
                        if comments_file_path and os.path.exists(comments_file_path):
                            print("感想ページの小説情報リンクを再修正中...")
                            comments_dir = os.path.dirname(comments_file_path)
                            if os.path.exists(comments_dir):
                                # 感想フォルダ内のすべてのHTMLファイルを処理
                                for comments_file in os.listdir(comments_dir):
                                    if comments_file.endswith('.html'):
                                        comments_file_full_path = os.path.join(comments_dir, comments_file)
                                        with open(comments_file_full_path, 'r', encoding='utf-8') as f:
                                            content = f.read()
                                        
                                        soup_comments = BeautifulSoup(content, 'html.parser')
                                        
                                        # 小説情報ページへのリンクを修正
                                        for link in soup_comments.find_all('a', href=True):
                                            href = link.get('href')
                                            if href and ('mode=ss_detail' in href or '小説情報' in link.get_text()):
                                                link['href'] = f'../{info_file_name}'
                                                self.debug_log(f"感想ページ小説情報リンク再修正: {href} -> ../{info_file_name}")
                                        
                                        with open(comments_file_full_path, 'w', encoding='utf-8') as f:
                                            f.write(str(soup_comments))
                    else:
                        print("⚠️ 小説情報ページの保存に失敗しました")
                        info_file_name = None
                else:
                    print("⚠️ 小説情報ページのURLが見つかりませんでした")
                    info_file_name = None
            else:
                info_file_name = None
            
            # 🆕 縦書きページ処理機能
            print("縦書きページと関連リンクを処理中...")
            # 縦書きページ内のナビゲーションリンク修正のため、適切なファイル名を渡す
            index_file_for_vertical = os.path.basename(index_file_path) if index_file_path else None
            comments_file_for_vertical = f"感想/感想 - ページ1.html" if comments_file_name else None
            
            vertical_result = self.process_vertical_reading_links(
                soup, 
                output_dir, 
                title,
                index_file=index_file_for_vertical,
                info_file=info_file_name,
                comments_file=comments_file_for_vertical
            )
            if vertical_result:
                if 'vertical_page' in vertical_result:
                    print(f"📖 縦書きページ保存完了: {os.path.basename(vertical_result['vertical_page']['file_path'])}")
                    additional_links = vertical_result['vertical_page'].get('additional_links', [])
                    if additional_links:
                        print(f"🔗 縦書きページ内関連リンク: {len(additional_links)}個発見")
                
                if 'info_page' in vertical_result:
                    print(f"📝 小説情報ページ（縦書き用）保存完了: {os.path.basename(vertical_result['info_page'])}")
            else:
                print("⚠️ 縦書きページまたは小説情報ページが見つかりませんでした")
                vertical_result = None
            
            # 縦書きページ処理完了後、既存の小説情報ページと感想ページの縦書きリンクを修正
            if vertical_result and 'vertical_page' in vertical_result:
                vertical_file_name = os.path.basename(vertical_result['vertical_page']['file_path'])
                print("既存ページの縦書きリンクを修正中...")
                
                # 小説情報ページの縦書きリンク修正
                if info_file_name and info_file_path and os.path.exists(info_file_path):
                    print(f"小説情報ページの縦書きリンクを修正中: {info_file_name}")
                    with open(info_file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    soup_info = BeautifulSoup(content, 'html.parser')
                    soup_info = self.fix_vertical_links_in_all_pages(
                        soup_info,
                        index_file_name,
                        None,  # 小説情報ページ自身なのでinfo_file=None
                        vertical_file_name
                    )
                    
                    with open(info_file_path, 'w', encoding='utf-8') as f:
                        f.write(str(soup_info))
                    print(f"✓ 小説情報ページの縦書きリンク修正完了")
                
                # 感想ページの縦書きリンク修正（複数ページある場合）
                if comments_file_name:
                    comments_dir = os.path.join(output_dir, "感想")
                    if os.path.exists(comments_dir):
                        print("感想ページの縦書きリンクを修正中...")
                        for filename in os.listdir(comments_dir):
                            if filename.endswith('.html'):
                                file_path = os.path.join(comments_dir, filename)
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                
                                soup_comment = BeautifulSoup(content, 'html.parser')
                                soup_comment = self.fix_vertical_links_in_all_pages(
                                    soup_comment,
                                    f"../{index_file_name}" if index_file_name else "../目次.html",
                                    f"../{info_file_name}" if info_file_name else None,
                                    f"../{vertical_file_name}"
                                )
                                
                                with open(file_path, 'w', encoding='utf-8') as f:
                                    f.write(str(soup_comment))
                        print(f"✓ 感想ページの縦書きリンク修正完了")
        
        if not chapter_links:
            print("章リンクが見つかりませんでした。単一ページとして処理します。")
            
            # 単一ページの場合でも縦書きページ処理を実行
            print("縦書きページと関連リンクを処理中...")
            # 単一ページの場合、index_file_pathは未定義なので目次ファイル名は推定
            index_file_for_vertical = f"{safe_title} - 目次.html" if index_file_path else None
            comments_file_for_vertical = f"感想/感想 - ページ1.html" if comments_file_name else None
            
            vertical_result = self.process_vertical_reading_links(
                soup, 
                output_dir, 
                title,
                index_file=index_file_for_vertical,
                info_file=info_file_name,
                comments_file=comments_file_for_vertical
            )
            if vertical_result:
                if 'vertical_page' in vertical_result:
                    print(f"📖 縦書きページ保存完了: {os.path.basename(vertical_result['vertical_page']['file_path'])}")
                    additional_links = vertical_result['vertical_page'].get('additional_links', [])
                    if additional_links:
                        print(f"🔗 縦書きページ内関連リンク: {len(additional_links)}個発見")
                
                if 'info_page' in vertical_result:
                    print(f"📝 小説情報ページ（縦書き用）保存完了: {os.path.basename(vertical_result['info_page'])}")
            else:
                print("⚠️ 縦書きページまたは小説情報ページが見つかりませんでした")
                vertical_result = None
            
            # 単一ページの場合
            chapter_content = self.extract_chapter_content(soup, novel_url)
            if chapter_content:
                chapters = [{
                    'title': title,
                    'content': chapter_content
                }]
            else:
                print("本文の取得に失敗しました")
                return None
        else:
            # 各章を個別ファイルとして保存
            chapters = []
            chapter_mapping = {}  # URL -> ローカルファイルパスのマッピング
            saved_chapters = []
            
            # まず目次ページのローカルファイル名を決定
            if index_file_path:
                index_filename = os.path.basename(index_file_path)
            else:
                index_filename = None
            
            # 章のマッピングを事前に作成（前の話・次の話リンク用）
            print("章のファイル名マッピングを作成中...")
            # 初期マッピングは空で開始（短縮形式ファイル名の生成を回避）
            chapter_mapping = {}
            print(f"事前マッピング準備完了: {len(chapter_links)}章")
            
            for i, chapter_url in enumerate(chapter_links, 1):
                print(f"章 {i}/{len(chapter_links)} を取得中: {chapter_url}")
                
                # サーバー負荷軽減のための適応的待機
                if i > 1:
                    wait_time = min(3 + (i // 10), 8)  # 章数が増えるほど待機時間を増加
                    print(f"サーバー負荷軽減のため {wait_time} 秒待機...")
                    time.sleep(wait_time)
                
                chapter_soup = self.get_page(chapter_url)
                
                if chapter_soup:
                    # リソース処理は目次ページで完了済みのため、ローカルパス調整のみ
                    chapter_soup = self.adjust_resource_paths_only(chapter_soup, output_dir)
                    
                    # 章のタイトルを抽出
                    chapter_title = chapter_soup.find('title')
                    if chapter_title:
                        chapter_title_text = chapter_title.get_text(strip=True)
                    else:
                        chapter_title_text = f"第{i}話"
                    
                    # ローカルリンク修正（第1回目：仮のマッピング + 小説情報・感想対応）
                    chapter_soup = self.fix_local_navigation_links(
                        chapter_soup, 
                        chapter_mapping, 
                        chapter_url, 
                        os.path.basename(index_file_path) if index_file_path else None,
                        info_file_name,
                        comments_file_name
                    )
                    
                    # 縦書きページ対応のナビゲーションリンク修正
                    vertical_file_name = None
                    if vertical_result and 'vertical_page' in vertical_result:
                        vertical_file_name = os.path.basename(vertical_result['vertical_page']['file_path'])
                    
                    info_file_name_for_vertical = None
                    if vertical_result and 'info_page' in vertical_result:
                        info_file_name_for_vertical = os.path.basename(vertical_result['info_page'])
                    
                    if vertical_file_name or info_file_name_for_vertical:
                        chapter_soup = self.update_navigation_links_with_vertical_pages(
                            chapter_soup,
                            os.path.basename(index_file_path) if index_file_path else None,
                            info_file_name_for_vertical or info_file_name,
                            vertical_file_name
                        )
                    
                    # 章を個別ファイルとして保存
                    safe_chapter_title = re.sub(r'[<>:"/\\|?*]', '_', chapter_title_text)
                    chapter_file_path = self.save_complete_page(
                        chapter_soup, 
                        chapter_url,
                        safe_chapter_title,
                        output_dir, 
                        chapter_url
                    )
                    
                    if chapter_file_path:
                        chapter_filename = os.path.basename(chapter_file_path)
                        # 実際のファイル名でマッピングを更新
                        chapter_mapping[chapter_url] = chapter_filename
                        print(f"マッピング更新: {chapter_url} -> {chapter_filename}")
                        saved_chapters.append({
                            'url': chapter_url,
                            'title': chapter_title_text,
                            'file_path': chapter_file_path,
                            'filename': chapter_filename
                        })
                        print(f"章 {i} 保存完了: {chapter_title_text} -> {chapter_filename}")
                    else:
                        print(f"章 {i} の保存に失敗しました")
                else:
                    print(f"章 {i} のページ取得に失敗しました")
            
            # 第2回目：全章の相互リンクを修正
            print("章間のナビゲーションリンクを修正中...")
            for chapter_info in saved_chapters:
                if os.path.exists(chapter_info['file_path']):
                    with open(chapter_info['file_path'], 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    soup = BeautifulSoup(content, 'html.parser')
                    soup = self.fix_local_navigation_links(
                        soup, 
                        chapter_mapping, 
                        chapter_info['url'], 
                        os.path.basename(index_file_path) if index_file_path else None,
                        info_file_name,
                        comments_file_name
                    )
                    
                    with open(chapter_info['file_path'], 'w', encoding='utf-8') as f:
                        f.write(str(soup))
            
            # 目次ページのリンクも修正
            if index_file_path and os.path.exists(index_file_path):
                print("目次ページのリンクを修正中...")
                with open(index_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                soup = BeautifulSoup(content, 'html.parser')
                soup = self.fix_local_navigation_links(
                    soup, 
                    chapter_mapping, 
                    novel_url, 
                    None,
                    info_file_name,
                    comments_file_name
                )
                
                # 縦書きページのリンクも修正
                vertical_file_name = None
                if vertical_result and 'vertical_page' in vertical_result:
                    vertical_file_name = os.path.basename(vertical_result['vertical_page']['file_path'])
                
                if vertical_file_name:
                    soup = self.fix_vertical_links_in_all_pages(
                        soup,
                        None,  # 目次ページ自身なのでindex_file=None
                        info_file_name,
                        vertical_file_name
                    )
                
                with open(index_file_path, 'w', encoding='utf-8') as f:
                    f.write(str(soup))
            
            # 旧形式の章データも作成（既存コードとの互換性のため）
            chapters = [{'title': ch['title'], 'content': ''} for ch in saved_chapters]
        
        if not chapters:
            print("取得できた章がありませんでした")
            return None
        
        print(f"小説の保存が完了しました: {output_dir}")
        print(f"取得した章数: {len(chapters)}")
        
        # 保存ディレクトリのパスを返す（GUI互換性のため）
        return output_dir
        
    def get_cache_stats(self):
        """リソースキャッシュの統計情報を取得"""
        return {
            'cached_resources': len(self.resource_cache),
            'cache_entries': list(self.resource_cache.keys())[:10]  # 最初の10個のみ表示
        }

    def close(self):
        """リソースを解放"""
        if self.driver:
            self.driver.quit()
            print("ブラウザを閉じました")
        
        stats = self.get_cache_stats()
        self.debug_log(f"リソースキャッシュ統計: {stats['cached_resources']}個のリソースをキャッシュしました")

    def extract_vertical_reading_link(self, soup):
        """縦書きリンクをHTML構造から抽出"""
        try:
            # topicPath内の縦書きリンクを探す
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                if href and 'mode=ss_detail3' in href:
                    self.debug_log(f"縦書きリンク発見: {href}")
                    return href
            return None
        except Exception as e:
            self.debug_log(f"縦書きリンク抽出エラー: {e}", "ERROR")
            return None
    
    def extract_novel_info_link(self, soup):
        """小説情報リンクをHTML構造から抽出"""
        try:
            # topicPath内の小説情報リンクを探す
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                if href and 'mode=ss_detail' in href and 'mode=ss_detail3' not in href:
                    self.debug_log(f"小説情報リンク発見: {href}")
                    return href
            return None
        except Exception as e:
            self.debug_log(f"小説情報リンク抽出エラー: {e}", "ERROR")
            return None
    
    def extract_additional_links_from_vertical_page(self, soup):
        """縦書きページから追加リンクを抽出"""
        try:
            additional_links = []
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                if href and any(mode in href for mode in ['mode=review', 'mode=rating_input', 'mode=correct_view']):
                    additional_links.append(href)
                    self.debug_log(f"追加リンク発見: {href}")
            return additional_links
        except Exception as e:
            self.debug_log(f"追加リンク抽出エラー: {e}", "ERROR")
            return []
    
    def save_vertical_reading_page(self, vertical_url, output_dir, novel_title, index_file=None, info_file=None, comments_file=None):
        """縦書きページを保存（ナビゲーションリンク修正とPDFダウンロード機能付き）"""
        try:
            self.debug_log(f"縦書きページ保存開始: {vertical_url}")
            
            # URLが相対パスの場合は絶対パスに変換
            if vertical_url.startswith('//'):
                vertical_url = 'https:' + vertical_url
            elif vertical_url.startswith('/'):
                vertical_url = 'https://syosetu.org' + vertical_url
            
            # 縦書きページを取得
            soup = self.get_page(vertical_url)
            if not soup:
                self.debug_log("縦書きページの取得に失敗", "ERROR")
                return None
            
            # 1. 縦書きページ内のナビゲーションリンクを修正
            if index_file or info_file or comments_file:
                self.debug_log("縦書きページ内のナビゲーションリンクを修正中...")
                soup = self.fix_navigation_links_in_vertical_page(
                    soup, 
                    index_file=index_file,
                    info_file=info_file,
                    comments_file=comments_file
                )
            
            # 2. 縦書きページ内の追加リンクを抽出
            additional_links = self.extract_additional_links_from_vertical_page(soup)
            
            # 3. PDFリンクをダウンロード・ローカル化
            self.debug_log("PDFリンクのダウンロード・ローカル化を実行中...")
            soup = self.download_and_localize_pdf_links(soup, output_dir, novel_title)
            
            # 4. 縦書きページを保存
            safe_title = re.sub(r'[<>:"/\\|?*]', '_', novel_title)
            filename = f"{safe_title} - 縦書き"
            
            file_path = self.save_complete_page(soup, vertical_url, filename, output_dir, vertical_url)
            
            if file_path:
                self.debug_log(f"縦書きページ保存完了: {file_path}")
                return {
                    'file_path': file_path,
                    'additional_links': additional_links
                }
            return None
            
        except Exception as e:
            self.debug_log(f"縦書きページ保存エラー: {e}", "ERROR")
            return None
    
    def save_novel_info_page_with_vertical_link(self, info_url, output_dir, novel_title):
        """小説情報ページを保存（縦書きリンク対応）"""
        try:
            self.debug_log(f"小説情報ページ保存開始: {info_url}")
            
            # URLが相対パスの場合は絶対パスに変換
            if info_url.startswith('//'):
                info_url = 'https:' + info_url
            elif info_url.startswith('/'):
                info_url = 'https://syosetu.org' + info_url
            
            # 小説情報ページを取得
            soup = self.get_page(info_url)
            if not soup:
                self.debug_log("小説情報ページの取得に失敗", "ERROR")
                return None
            
            # 小説情報ページを保存
            safe_title = re.sub(r'[<>:"/\\|?*]', '_', novel_title)
            filename = f"{safe_title} - 小説情報"
            
            file_path = self.save_complete_page(soup, info_url, filename, output_dir, info_url)
            
            if file_path:
                self.debug_log(f"小説情報ページ保存完了: {file_path}")
                return file_path
            return None
            
        except Exception as e:
            self.debug_log(f"小説情報ページ保存エラー: {e}", "ERROR")
            return None
    
    def process_vertical_reading_links(self, soup, output_dir, novel_title, index_file=None, info_file=None, comments_file=None):
        """縦書きリンクの処理（統合機能：ナビゲーションリンク修正対応）"""
        try:
            result = {}
            
            # 縦書きリンクを抽出
            vertical_link = self.extract_vertical_reading_link(soup)
            if vertical_link:
                self.debug_log(f"縦書きリンクを処理中: {vertical_link}")
                vertical_result = self.save_vertical_reading_page(
                    vertical_link, 
                    output_dir, 
                    novel_title,
                    index_file=index_file,
                    info_file=info_file,
                    comments_file=comments_file
                )
                if vertical_result:
                    result['vertical_page'] = vertical_result
                    self.debug_log("縦書きページ保存完了（ナビゲーションリンク修正済み）")
            
            # 小説情報リンクを抽出
            info_link = self.extract_novel_info_link(soup)
            if info_link:
                info_result = self.save_novel_info_page_with_vertical_link(info_link, output_dir, novel_title)
                if info_result:
                    result['info_page'] = info_result
            
            return result if result else None
            
        except Exception as e:
            self.debug_log(f"縦書きリンク処理エラー: {e}", "ERROR")
            return None
    
    def update_navigation_links_with_vertical_pages(self, soup, index_file, info_file, vertical_file):
        """ナビゲーションリンクを更新（縦書きページ対応）"""
        try:
            # 目次リンクの更新
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                text = link.get_text(strip=True)
                
                if text == "目次" or ('/novel/' in href and href.endswith('/')):
                    link['href'] = index_file
                    self.debug_log(f"目次リンク更新: {href} -> {index_file}")
                elif text == "縦書き" or 'mode=ss_detail3' in href:
                    link['href'] = vertical_file
                    self.debug_log(f"縦書きリンク更新: {href} -> {vertical_file}")
                elif text == "小説情報" or ('mode=ss_detail' in href and 'mode=ss_detail3' not in href):
                    link['href'] = info_file
                    self.debug_log(f"小説情報リンク更新: {href} -> {info_file}")
            
            return soup
            
        except Exception as e:
            self.debug_log(f"ナビゲーションリンク更新エラー: {e}", "ERROR")
            return soup

    def fix_vertical_links_in_all_pages(self, soup, index_file, info_file, vertical_file):
        """全ページの縦書きリンク修正（目次・感想・小説情報ページ対応）"""
        try:
            # 全てのナビゲーションリンクを更新
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                text = link.get_text(strip=True)
                
                # 目次リンクの更新
                if text == "目次" or ('/novel/' in href and href.endswith('/')):
                    if index_file:
                        link['href'] = index_file
                        self.debug_log(f"目次リンク更新: {href} -> {index_file}")
                
                # 縦書きリンクの更新
                elif text == "縦書き" or 'mode=ss_detail3' in href:
                    if vertical_file:
                        link['href'] = vertical_file
                        self.debug_log(f"縦書きリンク更新: {href} -> {vertical_file}")
                
                # 小説情報リンクの更新
                elif text == "小説情報" or ('mode=ss_detail' in href and 'mode=ss_detail3' not in href):
                    if info_file:
                        link['href'] = info_file
                        self.debug_log(f"小説情報リンク更新: {href} -> {info_file}")
            
            return soup
            
        except Exception as e:
            self.debug_log(f"全ページナビゲーションリンク更新エラー: {e}", "ERROR")
            return soup

    def extract_pdf_links_from_vertical_page(self, soup):
        """縦書きページからPDF・テキストダウンロードリンクを抽出"""
        try:
            pdf_links = []
            
            # ダウンロード関連のリンクを検索
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                # 大文字小文字を区別しないでチェック（より精密な条件）
                href_lower = href.lower()
                if href and (
                    'txtdownload' in href_lower or 
                    'pdfdownload' in href_lower or 
                    'epubdownload' in href_lower or
                    ('/conv/pdf/' in href_lower and href_lower.startswith('/conv/')) or
                    ('/conv/txt/' in href_lower and href_lower.startswith('/conv/')) or 
                    ('/conv/epub/' in href_lower and href_lower.startswith('/conv/')) or
                    ('api/download' in href_lower and 'format=' in href_lower)
                ):
                    # 相対URLを絶対URLに変換
                    if href.startswith('//'):
                        full_url = 'https:' + href
                    elif href.startswith('/'):
                        full_url = self.base_url + href
                    elif not href.startswith('http'):
                        full_url = urljoin(self.base_url, href)
                    else:
                        full_url = href
                    
                    pdf_links.append(href)  # 元のhrefを返す（テスト用）
                    self.debug_log(f"ダウンロードリンク発見: {href}")
            
            return pdf_links
            
        except Exception as e:
            self.debug_log(f"PDFリンク抽出エラー: {e}", "ERROR")
            return []

    def download_file(self, url, output_dir, filename=None):
        """ファイルをダウンロードしてローカルに保存（デバッグ強化版）"""
        try:
            self.debug_log(f"ダウンロード開始: 元URL={url}")
            
            # 絶対URLに変換
            if url.startswith('//'):
                url = 'https:' + url
            elif url.startswith('/'):
                url = self.base_url + url
            elif not url.startswith('http'):
                url = urljoin(self.base_url, url)
            
            self.debug_log(f"正規化後URL: {url}")
            
            # ファイル名を決定
            if not filename:
                parsed = urlparse(url)
                filename = os.path.basename(parsed.path)
                if not filename or '.' not in filename:
                    # URLパラメータからファイル名を推測
                    if 'txtdownload' in url:
                        if 'code=sjis' in url:
                            filename = "小説_SJIS版.txt"
                        elif 'code=utf8' in url:
                            filename = "小説_UTF8版.txt"
                        else:
                            filename = "小説.txt"
                    elif 'pdfdownload' in url:
                        filename = "小説.pdf"
                    else:
                        filename = "download_file"
            
            self.debug_log(f"ファイル名決定: {filename}")
            
            # 出力パスを作成
            output_path = os.path.join(output_dir, filename)
            self.debug_log(f"保存先パス: {output_path}")
            
            # ダウンロード実行
            self.debug_log("HTTPリクエスト開始...")
            response = self.cloudscraper.get(url, timeout=30)
            self.debug_log(f"HTTPレスポンス: status={response.status_code}, content-length={len(response.content)}")
            response.raise_for_status()
            
            # ファイルを保存
            self.debug_log("ファイル書き込み開始...")
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            # ファイルサイズを確認
            file_size = os.path.getsize(output_path)
            self.debug_log(f"✓ ファイル保存完了: {output_path} (サイズ: {file_size}バイト)")
            return output_path
            
        except Exception as e:
            self.debug_log(f"✗ ファイルダウンロードエラー: {e}", "ERROR")
            import traceback
            self.debug_log(f"詳細エラー: {traceback.format_exc()}", "ERROR")
            return None

    def download_and_localize_pdf_links(self, soup, output_dir, novel_title):
        """PDFリンクをダウンロードしてローカルリンクに変換（デバッグ強化版）"""
        try:
            self.debug_log("PDFリンクのダウンロード・ローカル化を開始...")
            
            # PDFリンクを抽出
            pdf_links = self.extract_pdf_links_from_vertical_page(soup)
            self.debug_log(f"抽出されたPDFリンク数: {len(pdf_links)}")
            
            if not pdf_links:
                self.debug_log("ダウンロード対象のリンクが見つかりません")
                return soup
            
            # 抽出されたリンクを詳細表示
            for i, link in enumerate(pdf_links):
                self.debug_log(f"PDFリンク{i+1}: {link}")
            
            download_count = 0
            # 各リンクをダウンロードしてローカル化
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                link_text = link.get_text(strip=True)
                self.debug_log(f"検査中のリンク: href='{href}', text='{link_text}'")
                
                if href in pdf_links:
                    self.debug_log(f"PDFダウンロード対象リンク発見: {href}")
                    
                    # ファイル名を決定
                    if 'SJIS' in link_text or 'sjis' in href:
                        filename = f"{novel_title}_SJIS版.txt"
                    elif 'UTF' in link_text or 'utf8' in href:
                        filename = f"{novel_title}_UTF8版.txt"
                    elif 'PDF' in link_text or 'pdf' in href:
                        filename = f"{novel_title}.pdf"
                    else:
                        filename = f"{novel_title}_ダウンロード.txt"
                    
                    self.debug_log(f"ダウンロード実行: {href} -> {filename}")
                    
                    # ファイルをダウンロード
                    local_path = self.download_file(href, output_dir, filename)
                    
                    if local_path:
                        # リンクをローカルファイルに更新
                        relative_path = os.path.basename(local_path)
                        link['href'] = relative_path
                        download_count += 1
                        self.debug_log(f"✓ リンクローカル化成功: {href} -> {relative_path}")
                    else:
                        self.debug_log(f"✗ ダウンロード失敗: {href}")
            
            self.debug_log(f"PDFダウンロード完了: {download_count}個のファイルを処理")
            return soup
            
        except Exception as e:
            self.debug_log(f"PDFリンクローカル化エラー: {e}", "ERROR")
            import traceback
            self.debug_log(f"詳細エラー: {traceback.format_exc()}", "ERROR")
            return soup

    def fix_navigation_links_in_vertical_page(self, soup, index_file=None, info_file=None, comments_file=None):
        """縦書きページ内のナビゲーションリンクをローカルファイルに修正"""
        try:
            # 縦書きページ内の全てのリンクを調査
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                text = link.get_text(strip=True)
                
                if not href:
                    continue
                
                # 目次リンクの修正
                if text == "目次" or ('/novel/' in href and href.endswith('/')):
                    if index_file:
                        link['href'] = index_file
                        self.debug_log(f"縦書きページ内目次リンク修正: {href} -> {index_file}")
                
                # 小説情報リンクの修正
                elif text == "小説情報" or ('mode=ss_detail' in href and 'mode=ss_detail3' not in href):
                    if info_file:
                        link['href'] = info_file
                        self.debug_log(f"縦書きページ内小説情報リンク修正: {href} -> {info_file}")
                
                # 感想リンクの修正
                elif text == "感想" or 'mode=review' in href:
                    if comments_file:
                        link['href'] = comments_file
                        self.debug_log(f"縦書きページ内感想リンク修正: {href} -> {comments_file}")
                
                # 評価、ここすき、誤字報告などのリンクは無効化
                elif any(mode in href for mode in ['mode=rating_input', 'mode=ss_detail_like_line', 'mode=correct_view']):
                    link['href'] = 'javascript:void(0);'
                    link['style'] = 'color: #999; cursor: not-allowed; text-decoration: none;'
                    self.debug_log(f"縦書きページ内リンク無効化: {href} ({text})")
            
            return soup
            
        except Exception as e:
            self.debug_log(f"縦書きページナビゲーションリンク修正エラー: {e}", "ERROR")
            return soup

    def save_vertical_reading_page_with_full_fixes(self, vertical_url, output_dir, novel_title, index_file=None, info_file=None, comments_file=None):
        """縦書きページを保存（完全修正版：ナビゲーションリンク修正とPDFダウンロード含む）"""
        try:
            self.debug_log(f"縦書きページ保存開始（完全修正版）: {vertical_url}")
            
            # URLが相対パスの場合は絶対パスに変換
            if vertical_url.startswith('//'):
                vertical_url = 'https:' + vertical_url
            elif vertical_url.startswith('/'):
                vertical_url = 'https://syosetu.org' + vertical_url
            
            # 縦書きページを取得
            soup = self.get_page(vertical_url)
            if not soup:
                self.debug_log("縦書きページの取得に失敗", "ERROR")
                return None
            
            # 1. 縦書きページ内のナビゲーションリンクを修正
            soup = self.fix_navigation_links_in_vertical_page(
                soup, 
                index_file=index_file,
                info_file=info_file,
                comments_file=comments_file
            )
            
            # 2. PDFリンクをダウンロード・ローカル化
            soup = self.download_and_localize_pdf_links(soup, output_dir, novel_title)
            
            # 3. 縦書きページ内の追加リンクを抽出
            additional_links = self.extract_additional_links_from_vertical_page(soup)
            
            # 4. 縦書きページを保存
            safe_title = re.sub(r'[<>:"/\\|?*]', '_', novel_title)
            filename = f"{safe_title} - 縦書き"
            
            file_path = self.save_complete_page(soup, vertical_url, filename, output_dir, vertical_url)
            
            if file_path:
                self.debug_log(f"縦書きページ保存完了（完全修正版）: {file_path}")
                return {
                    'file_path': file_path,
                    'additional_links': additional_links
                }
            return None
            
        except Exception as e:
            self.debug_log(f"縦書きページ保存エラー（完全修正版）: {e}", "ERROR")
            return None

def main():
    """メイン関数"""
    scraper = None
    
    try:
        scraper = HamelnFinalScraper()
        
        print("ハーメルン小説保存ツール（最終版）")
        print("完全モード（CSS・画像・JavaScript含む完全保存）")
        print("=" * 50)
        
        import sys
        if len(sys.argv) > 1:
            novel_url = sys.argv[1]
            print(f"指定されたURL: {novel_url}")
        else:
            novel_url = input("小説のURLを入力してください: ").strip()
        
        if not novel_url:
            print("URLが入力されていません。")
            return
        
        result = scraper.scrape_novel(novel_url)
        if result:
            print(f"\n✓ 保存完了: {result}")
        else:
            print("\n✗ 保存に失敗しました。")
            
    except KeyboardInterrupt:
        print("\n\n処理が中断されました。")
    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if scraper:
            scraper.close()

# 縦書きリンク処理をHamelnFinalScraperクラスに追加
def add_vertical_reading_methods():
    """縦書きリンク処理メソッドをHamelnFinalScraperクラスに追加"""
    
if __name__ == "__main__":
    main()
