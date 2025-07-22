"""
ファイル・ディレクトリ管理モジュール
hameln_scraper_final.pyからファイル管理機能を分離
"""

import os
import re
import hashlib
from urllib.parse import urlparse
from typing import Optional, Dict, Any
import logging


class FileManager:
    """ファイル・ディレクトリ管理クラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.resource_cache: Dict[str, str] = {}
        
        # デフォルト設定
        self.max_filename_length = 200  # ファイルシステム制限対応
        self.resources_dir_name = "resources"
        self.comments_dir_name = "感想"
    
    def sanitize_filename(self, filename: str) -> str:
        """
        ファイル名サニタイズ機能（元ファイル複数箇所から抽出）
        
        Args:
            filename: サニタイズするファイル名
            
        Returns:
            str: 安全なファイル名
        """
        if not filename:
            return "untitled"
        
        # 元ファイル行2077等と同じロジック: 危険文字を_に置換
        safe_filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # 長すぎるファイル名の切り詰め
        if len(safe_filename) > self.max_filename_length:
            name, ext = os.path.splitext(safe_filename)
            name = name[:self.max_filename_length - len(ext) - 10]  # 余裕を持って切り詰め
            safe_filename = f"{name}...{ext}"
        
        self.logger.debug(f"ファイル名サニタイズ: '{filename}' → '{safe_filename}'")
        return safe_filename
    
    def create_directory_structure(self, base_dir: str, novel_title: str) -> str:
        """
        小説用ディレクトリ構造作成（元ファイル行2078-2079, 514-515等から抽出）
        
        Args:
            base_dir: ベースディレクトリ
            novel_title: 小説タイトル
            
        Returns:
            str: 作成された小説ディレクトリのパス
        """
        # 元ファイルと同じロジック: タイトルを安全化
        safe_title = self.sanitize_filename(novel_title)
        
        # メインディレクトリ作成
        novel_dir = os.path.join(base_dir, safe_title)
        self._create_directory(novel_dir)
        
        # リソースディレクトリ作成（元ファイル行514-515）
        resources_dir = os.path.join(novel_dir, self.resources_dir_name)
        self._create_directory(resources_dir)
        
        # 感想ディレクトリ作成（元ファイル行1142-1144）
        comments_dir = os.path.join(novel_dir, self.comments_dir_name)
        self._create_directory(comments_dir)
        
        self.logger.debug(f"ディレクトリ構造作成完了: {novel_dir}")
        return novel_dir
    
    def _create_directory(self, path: str) -> None:
        """
        ディレクトリ作成内部メソッド（元ファイルのos.makedirs系から抽出）
        
        Args:
            path: 作成するディレクトリパス
        """
        try:
            # 元ファイルと同じ: exist_ok=Trueで既存時エラー回避
            os.makedirs(path, exist_ok=True)
            self.logger.debug(f"ディレクトリ作成: {path}")
        except OSError as e:
            self.logger.error(f"ディレクトリ作成失敗: {path} - {e}")
            raise
    
    def generate_resource_filename(self, url: str) -> str:
        """
        リソースファイル名生成（元ファイル行432-445から抽出・改良）
        
        Args:
            url: リソースURL
            
        Returns:
            str: 生成されたファイル名
        """
        try:
            parsed = urlparse(url)
            filename = os.path.basename(parsed.path)
            
            # 元ファイルと同じロジック: ファイル名がない場合の処理
            if not filename or '.' not in filename:
                filename = self._generate_fallback_filename(url)
            
            # クエリパラメータ除去
            if '?' in filename:
                filename = filename.split('?')[0]
                
            # ファイル名安全化
            safe_filename = self.sanitize_filename(filename)
            
            self.logger.debug(f"リソースファイル名生成: {url} → {safe_filename}")
            return safe_filename
            
        except Exception as e:
            self.logger.error(f"ファイル名生成エラー: {url} - {e}")
            return self._generate_fallback_filename(url)
    
    def _generate_fallback_filename(self, url: str) -> str:
        """
        フォールバックファイル名生成（元ファイル行432-445のロジック）
        
        Args:
            url: リソースURL
            
        Returns:
            str: フォールバック用ファイル名
        """
        # URLハッシュベースの一意ID生成（元ファイルと同じ手法）
        hash_id = abs(hash(url)) % 10000
        
        # 元ファイルと同じ拡張子推測ロジック
        if 'css' in url.lower():
            return f"style_{hash_id}.css"
        elif 'js' in url.lower() or 'javascript' in url.lower():
            return f"script_{hash_id}.js"
        elif any(ext in url.lower() for ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp']):
            # URL末尾から拡張子抽出
            for ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp']:
                if ext in url.lower():
                    ext_clean = ext.lstrip('.')
                    return f"image_{hash_id}.{ext_clean}"
            return f"image_{hash_id}.png"  # デフォルト
        else:
            return f"resource_{hash_id}.txt"
    
    def get_safe_path(self, base_dir: str, filename: str) -> str:
        """
        安全なファイルパス生成
        
        Args:
            base_dir: ベースディレクトリ
            filename: ファイル名
            
        Returns:
            str: 安全なファイルパス
        """
        safe_filename = self.sanitize_filename(filename)
        return os.path.join(base_dir, safe_filename)
    
    def file_exists(self, filepath: str) -> bool:
        """
        ファイル存在確認（元ファイル行451等から抽出）
        
        Args:
            filepath: 確認するファイルパス
            
        Returns:
            bool: ファイルが存在するかどうか
        """
        exists = os.path.exists(filepath)
        if exists:
            self.logger.debug(f"既存ファイル確認: {filepath}")
        return exists
    
    def get_basename(self, filepath: str) -> str:
        """
        ファイル名のみ抽出（元ファイル行1208, 2324等から抽出）
        
        Args:
            filepath: ファイルパス
            
        Returns:
            str: ファイル名部分のみ
        """
        return os.path.basename(filepath)
    
    def generate_chapter_filename(self, title: str, chapter_num: Optional[int] = None) -> str:
        """
        章ファイル名生成（元ファイル行2367等から抽出）
        
        Args:
            title: 章タイトル
            chapter_num: 章番号（オプション）
            
        Returns:
            str: 章ファイル名
        """
        safe_title = self.sanitize_filename(title)
        
        if chapter_num is not None:
            filename = f"第{chapter_num}章_{safe_title}.html"
        else:
            filename = f"{safe_title}.html"
            
        return filename
    
    def generate_info_filename(self, novel_title: str) -> str:
        """
        小説情報ファイル名生成（元ファイル行1075から抽出）
        
        Args:
            novel_title: 小説タイトル
            
        Returns:
            str: 小説情報ファイル名
        """
        safe_title = self.sanitize_filename(novel_title)
        return f"{safe_title} - 小説情報.html"
    
    def generate_comments_filename(self, page_num: int) -> str:
        """
        感想ページファイル名生成（元ファイル行1173から抽出）
        
        Args:
            page_num: ページ番号
            
        Returns:
            str: 感想ファイル名
        """
        return f"感想 - ページ{page_num}.html"
    
    def add_to_cache(self, url: str, filename: str) -> None:
        """
        ファイル名キャッシュに追加
        
        Args:
            url: リソースURL
            filename: ローカルファイル名
        """
        self.resource_cache[url] = filename
        self.logger.debug(f"キャッシュ追加: {url} → {filename}")
    
    def get_cached_filename(self, url: str) -> Optional[str]:
        """
        キャッシュからファイル名取得
        
        Args:
            url: リソースURL
            
        Returns:
            Optional[str]: キャッシュされたファイル名
        """
        return self.resource_cache.get(url)
    
    def is_cached(self, url: str) -> bool:
        """
        URLがキャッシュされているか確認
        
        Args:
            url: リソースURL
            
        Returns:
            bool: キャッシュされているかどうか
        """
        return url in self.resource_cache
    
    def fix_local_navigation_links(self, soup, chapter_mapping: Dict[str, str], current_url: Optional[str] = None, index_filename: Optional[str] = None):
        """
        ローカルナビゲーションリンクを修正
        
        章間のリンクを外部URL（https://syosetu.org/novel/...）から
        ローカルファイル（第001話.html等）に変換する
        
        Args:
            soup: BeautifulSoupオブジェクト
            chapter_mapping: URLとローカルファイル名のマッピング
            current_url: 現在のページURL（省略可）
            index_filename: インデックスファイル名（省略可）
            
        Returns:
            BeautifulSoup: 修正されたBeautifulSoupオブジェクト
        """
        self.logger.debug(f"ローカルナビゲーションリンク修正開始")
        
        try:
            # 全てのリンク要素（aタグ）を検索
            links = soup.find_all('a', href=True)
            modified_count = 0
            
            for link in links:
                href = link.get('href')
                
                # chapter_mappingに含まれるURLの場合、ローカルファイル名に置き換え
                if href in chapter_mapping:
                    local_filename = chapter_mapping[href]
                    
                    # ファイル名のみを抽出（パス部分を除去）
                    if isinstance(local_filename, str):
                        filename_only = os.path.basename(local_filename)
                        link['href'] = filename_only
                        modified_count += 1
                        self.logger.debug(f"リンク修正: {href} → {filename_only}")
            
            self.logger.debug(f"ローカルナビゲーションリンク修正完了: {modified_count}個のリンクを修正")
            return soup
            
        except Exception as e:
            self.logger.error(f"ローカルナビゲーションリンク修正エラー: {e}")
            return soup