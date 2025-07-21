"""
リソースダウンローダーモジュール
hameln_scraper_final.pyのdownload_resource, download_and_process_css機能を分離
"""

import os
import re
import logging
from typing import Dict, Optional, Any, List
from urllib.parse import urlparse, urljoin
import cloudscraper
import requests
from .file_manager import FileManager


class ResourceDownloader:
    """リソースダウンロードクラス（ハーメルン特化）"""
    
    def __init__(self, network_client=None):
        self.logger = logging.getLogger(__name__)
        self.file_manager = FileManager()
        self.resource_cache: Dict[str, str] = {}
        
        # CloudScraperまたはネットワーククライアント使用
        if network_client:
            self.http_client = network_client
        else:
            self.http_client = self._create_cloudscraper()
    
    def _create_cloudscraper(self):
        """CloudScraper作成（元ファイル行101-114と同じ設定）"""
        try:
            return cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'desktop': True
                },
                delay=3,  # リクエスト間の遅延
                debug=False
            )
        except Exception as e:
            self.logger.warning(f"CloudScraper作成失敗、requestsを使用: {e}")
            return requests.Session()
    
    def convert_hameln_url(self, url: str, base_url: str = "") -> str:
        """
        ハーメルン特化URL変換（元ファイル行408-421から抽出）
        
        Args:
            url: 変換するURL
            base_url: ベースURL
            
        Returns:
            str: 変換されたURL
        """
        if url.startswith('http'):
            return url
            
        # 元ファイルと同じハーメルン特化変換
        if url.startswith('./resources/'):
            # ./resources/style.css -> https://img.syosetu.org/css/style.css
            resource_file = url.replace('./resources/', '')
            if resource_file.endswith('.css'):
                converted_url = f"https://img.syosetu.org/css/{resource_file}"
            elif resource_file.endswith('.js'):
                converted_url = f"https://img.syosetu.org/js/{resource_file}"
            else:
                converted_url = f"https://img.syosetu.org/image/{resource_file}"
            
            self.logger.debug(f"ハーメルンURL変換: {url} → {converted_url}")
            return converted_url
            
        elif url.startswith('./'):
            # ./banner.png -> https://img.syosetu.org/image/banner.png
            converted_url = f"https://img.syosetu.org/image/{url[2:]}"
            self.logger.debug(f"ハーメルン相対URL変換: {url} → {converted_url}")
            return converted_url
        else:
            # 通常の相対URL処理
            if base_url:
                return urljoin(base_url, url)
            return url
    
    def download_resource(self, url: str, output_dir: str, base_url: str = "") -> Dict[str, Any]:
        """
        個別リソースダウンロード（元ファイル行403-477から抽出・改良）
        
        Args:
            url: ダウンロードするURL
            output_dir: 出力ディレクトリ
            base_url: ベースURL
            
        Returns:
            Dict[str, Any]: ダウンロード結果
        """
        try:
            # URL変換
            absolute_url = self.convert_hameln_url(url, base_url)
            
            # キャッシュチェック（元ファイル行423-430と同じ）
            if self.is_cached(absolute_url):
                cached_filename = self.get_cached_path(absolute_url)
                cached_path = os.path.join(output_dir, cached_filename)
                if os.path.exists(cached_path):
                    self.logger.debug(f"キャッシュから取得: {cached_filename}")
                    return {
                        'success': True,
                        'local_path': cached_path,
                        'filename': cached_filename,
                        'from_cache': True
                    }
                else:
                    # キャッシュに記録されているが実ファイルが存在しない
                    del self.resource_cache[absolute_url]
            
            # ファイル名生成（元ファイル行432-445と同じロジック）
            filename = self.file_manager.generate_resource_filename(absolute_url)
            local_path = os.path.join(output_dir, filename)
            
            # 既存ファイル保護（元ファイル行451-454と同じ）
            if os.path.exists(local_path):
                self.logger.debug(f"既存ファイルを使用（上書き防止）: {filename}")
                self.add_to_cache(absolute_url, filename)
                return {
                    'success': True,
                    'local_path': local_path,
                    'filename': filename,
                    'from_cache': True
                }
            
            # リソースダウンロード実行
            self.logger.debug(f"リソースダウンロード開始: {absolute_url}")
            response = self.http_client.get(absolute_url, timeout=10)
            response.raise_for_status()
            
            # ファイル保存（元ファイル行459-470と同じエンコーディング考慮）
            if filename.endswith('.css'):
                # CSSファイルはUTF-8テキストとして保存
                response.encoding = 'utf-8'
                with open(local_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)
            else:
                # その他はバイナリとして保存
                with open(local_path, 'wb') as f:
                    f.write(response.content)
            
            self.logger.debug(f"リソース保存完了: {filename}")
            
            # キャッシュに追加
            self.add_to_cache(absolute_url, filename)
            
            return {
                'success': True,
                'local_path': local_path,
                'filename': filename,
                'from_cache': False
            }
            
        except Exception as e:
            self.logger.error(f"リソースダウンロードエラー ({url}): {e}")
            return {
                'success': False,
                'error': str(e),
                'original_url': url
            }
    
    def download_css(self, url: str, output_dir: str, base_url: str = "") -> Dict[str, Any]:
        """
        CSS詳細処理（元ファイル行781-875から抽出・改良）
        
        Args:
            url: CSSファイルURL
            output_dir: 出力ディレクトリ  
            base_url: ベースURL
            
        Returns:
            Dict[str, Any]: 処理結果
        """
        try:
            # URL変換
            absolute_url = self.convert_hameln_url(url, base_url)
            
            # ファイル名生成
            filename = self.file_manager.generate_resource_filename(absolute_url)
            if not filename.endswith('.css'):
                filename = f"style_{abs(hash(absolute_url)) % 10000}.css"
            
            self.logger.debug(f"CSS詳細処理開始: {absolute_url}")
            
            # CSSファイルダウンロード
            response = self.http_client.get(absolute_url, timeout=10)
            response.raise_for_status()
            response.encoding = 'utf-8'
            css_content = response.text
            
            # CSS内リソース処理結果
            processed_images = []
            processed_imports = []
            
            # 1. url()参照処理（元ファイル行810-850と同じロジック）
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
                        base_domain = '/'.join(absolute_url.split('/')[:3])
                        img_url = base_domain + img_url
                    else:
                        # 相対パス
                        base_css_url = '/'.join(absolute_url.split('/')[:-1])
                        img_url = urljoin(base_css_url + '/', img_url)
                
                # URL正規化
                cleaned_url = img_url.split(')')[0]
                if '?' in cleaned_url:
                    cleaned_url = cleaned_url.split('?')[0]
                
                # 画像ダウンロード
                self.logger.debug(f"CSS内画像ダウンロード: {cleaned_url}")
                result = self.download_resource(cleaned_url, output_dir, base_url)
                
                if result['success']:
                    local_filename = result['filename']
                    browser_compatible_path = f"./{local_filename}"
                    processed_images.append({
                        'original_url': original_img_url,
                        'processed_url': cleaned_url,
                        'local_file': local_filename
                    })
                    self.logger.debug(f"CSS内パス置換: {original_img_url} -> {browser_compatible_path}")
                    return full_match.replace(original_img_url, browser_compatible_path)
                else:
                    return full_match
            
            # 正規表現でurl()を検出・置換（元ファイルと同じパターン）
            css_content = re.sub(r'url\([\'"]?([^\'"]+?)[\'"]?\)', replace_url_func, css_content)
            
            # 2. @import文処理（元ファイル行851-872と同じ）
            imports = re.findall(r'@import\s+[\'"]([^\'"]+)[\'"]', css_content)
            for import_url in imports:
                if not import_url.startswith('http'):
                    if import_url.startswith('//'):
                        import_url = 'https:' + import_url
                    elif import_url.startswith('/'):
                        base_domain = '/'.join(absolute_url.split('/')[:3])
                        import_url = base_domain + import_url
                    else:
                        base_css_url = '/'.join(absolute_url.split('/')[:-1])
                        import_url = urljoin(base_css_url + '/', import_url)
                
                self.logger.debug(f"CSS @import処理: {import_url}")
                import_result = self.download_css(import_url, output_dir, base_url)
                
                if import_result['success']:
                    import_filename = import_result['filename']
                    browser_compatible_css = f"./{import_filename}"
                    css_content = css_content.replace(f'@import "{import_url}"', f'@import "{browser_compatible_css}"')
                    css_content = css_content.replace(f"@import '{import_url}'", f"@import '{browser_compatible_css}'")
                    processed_imports.append({
                        'original_url': import_url,
                        'local_file': import_filename
                    })
            
            # CSS保存
            local_path = os.path.join(output_dir, filename)
            with open(local_path, 'w', encoding='utf-8') as f:
                f.write(css_content)
            
            self.logger.debug(f"CSS処理完了: {filename}")
            
            return {
                'success': True,
                'local_path': local_path,
                'filename': filename,
                'processed_images': processed_images,
                'processed_imports': processed_imports
            }
            
        except Exception as e:
            self.logger.error(f"CSS処理エラー ({url}): {e}")
            return {
                'success': False,
                'error': str(e),
                'original_url': url
            }
    
    def is_cached(self, url: str) -> bool:
        """キャッシュ確認"""
        return url in self.resource_cache
    
    def add_to_cache(self, url: str, filename: str) -> None:
        """キャッシュ追加"""
        self.resource_cache[url] = filename
        self.logger.debug(f"キャッシュ追加: {url} → {filename}")
    
    def get_cached_path(self, url: str) -> Optional[str]:
        """キャッシュからファイル名取得"""
        return self.resource_cache.get(url)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        キャッシュ統計情報取得（元ファイル行2448-2453と同じ）
        
        Returns:
            Dict[str, Any]: キャッシュ統計
        """
        return {
            'cached_resources': len(self.resource_cache),
            'cache_entries': list(self.resource_cache.keys())[:10]  # 最初の10個のみ
        }
    
    def clear_cache(self) -> None:
        """キャッシュクリア"""
        self.resource_cache.clear()
        self.logger.debug("リソースキャッシュをクリア")