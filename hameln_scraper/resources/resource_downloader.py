"""
リソースダウンローダーモジュール
CSS、JavaScript、画像ファイルの取得と保存を担当
"""

import os
import re
import time
from pathlib import Path
from typing import Set, Dict, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup


class ResourceDownloader:
    """リソースダウンローダークラス"""
    
    def __init__(self, config, network_client):
        self.config = config
        self.network_client = network_client
        self.downloaded_resources = set()
    
    def download_all_resources(self, soup: BeautifulSoup, base_url: str, 
                             output_dir: str) -> BeautifulSoup:
        """全てのリソースをダウンロードしてHTMLを更新"""
        if not self.config.enable_resource_saving:
            return soup
        
        resources_dir = os.path.join(output_dir, "resources")
        os.makedirs(resources_dir, exist_ok=True)
        
        # CSS ファイル
        soup = self._download_css_files(soup, base_url, resources_dir)
        
        # JavaScript ファイル
        soup = self._download_js_files(soup, base_url, resources_dir)
        
        # 画像ファイル
        soup = self._download_image_files(soup, base_url, resources_dir)
        
        return soup
    
    def _download_css_files(self, soup: BeautifulSoup, base_url: str, 
                           resources_dir: str) -> BeautifulSoup:
        """CSSファイルをダウンロード"""
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href')
            if href:
                local_path = self._download_resource(href, base_url, resources_dir, '.css')
                if local_path:
                    link['href'] = f"./resources/{os.path.basename(local_path)}"
                    # ダウンロードしたCSSファイル内の画像参照も処理
                    self._process_css_file_images(local_path, base_url, resources_dir)
        
        return soup
    
    def _download_js_files(self, soup: BeautifulSoup, base_url: str, 
                          resources_dir: str) -> BeautifulSoup:
        """JavaScriptファイルをダウンロード"""
        for script in soup.find_all('script', src=True):
            src = script.get('src')
            if src:
                local_path = self._download_resource(src, base_url, resources_dir, '.js')
                if local_path:
                    script['src'] = f"resources/{os.path.basename(local_path)}"
        
        return soup
    
    def _download_image_files(self, soup: BeautifulSoup, base_url: str, 
                             resources_dir: str) -> BeautifulSoup:
        """画像ファイルをダウンロード"""
        # img タグ
        for img in soup.find_all('img', src=True):
            src = img.get('src')
            if src:
                local_path = self._download_resource(src, base_url, resources_dir)
                if local_path:
                    img['src'] = f"resources/{os.path.basename(local_path)}"
        
        # CSS内の背景画像も処理
        for style_tag in soup.find_all('style'):
            if style_tag.string:
                updated_css = self._process_css_urls(style_tag.string, base_url, resources_dir)
                style_tag.string = updated_css
        
        return soup
    
    def _download_resource(self, url: str, base_url: str, resources_dir: str, 
                          expected_ext: str = None) -> Optional[str]:
        """個別リソースをダウンロード"""
        try:
            # 絶対URLに変換
            full_url = urljoin(base_url, url)
            
            # 既にダウンロード済みかチェック
            if full_url in self.downloaded_resources:
                return None
            
            # ファイル名を決定
            parsed = urlparse(full_url)
            filename = os.path.basename(parsed.path)
            
            if not filename or '.' not in filename:
                if expected_ext:
                    filename = f"resource_{len(self.downloaded_resources)}{expected_ext}"
                else:
                    # URLから拡張子を推測
                    if 'css' in full_url:
                        filename = f"resource_{len(self.downloaded_resources)}.css"
                    elif 'js' in full_url:
                        filename = f"resource_{len(self.downloaded_resources)}.js"
                    elif any(ext in full_url for ext in ['.png', '.jpg', '.gif', '.ico']):
                        ext = '.png'  # デフォルト
                        for e in ['.png', '.jpg', '.jpeg', '.gif', '.ico', '.webp']:
                            if e in full_url:
                                ext = e
                                break
                        filename = f"resource_{len(self.downloaded_resources)}{ext}"
                    else:
                        filename = f"resource_{len(self.downloaded_resources)}.txt"
            
            # ファイルパス
            filepath = os.path.join(resources_dir, filename)
            
            # ダウンロード実行
            content = self.network_client.get_resource(full_url)
            if content:
                with open(filepath, 'wb') as f:
                    f.write(content)
                
                self.downloaded_resources.add(full_url)
                print(f"リソース保存: {filename}")
                return filepath
            
        except Exception as e:
            print(f"リソースダウンロードエラー ({url}): {e}")
        
        return None
    
    def _process_css_urls(self, css_content: str, base_url: str, resources_dir: str) -> str:
        """CSS内のURL参照を処理"""
        def replace_url(match):
            url = match.group(1).strip('\'"')
            local_path = self._download_resource(url, base_url, resources_dir)
            if local_path:
                return f'url("./resources/{os.path.basename(local_path)}")'
            return match.group(0)
        
        # CSS内のurl()を置換
        return re.sub(r'url\(["\']?([^"\']+)["\']?\)', replace_url, css_content)
    
    def _process_css_file_images(self, css_file_path: str, base_url: str, resources_dir: str):
        """ダウンロードしたCSSファイル内の画像参照を処理"""
        try:
            # CSSファイルを読み込み
            with open(css_file_path, 'r', encoding='utf-8') as f:
                css_content = f.read()
            
            # CSS内の画像URLを処理
            def replace_css_url(match):
                url = match.group(1).strip('\'"')
                
                # 相対パス（../image/など）を絶対URLに変換
                if url.startswith('../'):
                    # CSSの基本URLを取得（img.syosetu.org/css/）
                    css_base_url = base_url.replace('syosetu.org', 'img.syosetu.org') + '/'
                    if not css_base_url.endswith('/css/'):
                        css_base_url = css_base_url.rstrip('/') + '/css/'
                    
                    # ../image/ を /image/ に変換
                    image_url = url.replace('../', '/')
                    full_image_url = urljoin(css_base_url, image_url)
                else:
                    full_image_url = urljoin(base_url, url)
                
                # 画像をダウンロード
                local_path = self._download_resource(full_image_url, base_url, resources_dir)
                if local_path:
                    return f'url("./{os.path.basename(local_path)}")'
                
                return match.group(0)
            
            # CSS内のurl()を置換
            updated_css = re.sub(r'url\(["\']?([^"\']+)["\']?\)', replace_css_url, css_content)
            
            # 更新されたCSSファイルを保存
            with open(css_file_path, 'w', encoding='utf-8') as f:
                f.write(updated_css)
                
        except Exception as e:
            print(f"CSS画像処理エラー ({css_file_path}): {e}")