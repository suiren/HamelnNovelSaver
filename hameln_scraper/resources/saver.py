"""
完全ページ保存モジュール
hameln_scraper_final.pyのsave_complete_page機能を分離
"""

import os
import re
import logging
from datetime import datetime
from typing import Dict, Optional, Any
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup, Comment
from .processor import ResourceProcessor
from .file_manager import FileManager


class PageSaver:
    """完全ページ保存クラス（ハーメルン特化）"""
    
    def __init__(self, processor: Optional[ResourceProcessor] = None):
        self.logger = logging.getLogger(__name__)
        self.processor = processor  # processorがNoneの場合は後で設定
        self.file_manager = FileManager()
        
        # デフォルト設定
        self.resources_dir_name = "resources"
        self.browser_compatible_name = "resources"
    
    def save_complete_page(self, html_content: str, output_dir: str, filename: str,
                          original_url: str, title: str = "", 
                          processor: Optional[ResourceProcessor] = None) -> Dict[str, Any]:
        """
        ページ完全保存（元ファイル行2092-2180から抽出・改良）
        ブラウザ保存と同等の品質を実現
        
        Args:
            html_content: HTMLコンテンツ
            output_dir: 出力ディレクトリ
            filename: ファイル名
            original_url: 元のURL
            title: ページタイトル（オプション）
            processor: リソースプロセッサー（オプション）
            
        Returns:
            Dict[str, Any]: 保存結果
        """
        try:
            self.logger.info("ブラウザレベル完全保存開始")
            
            # プロセッサー設定
            active_processor = processor or self.processor
            
            # HTMLパース
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # リソース処理（元ファイル行2097と同じ）
            soup = active_processor.process_html_resources(soup, output_dir)
            
            # 元URLコメント追加（元ファイル行2105-2108と同じ）
            soup = self._add_url_comment(soup, original_url)
            
            # 相対リンク→絶対パス変換（元ファイル行2114-2150と同じ）
            soup = self._convert_links_to_absolute(soup, original_url)
            
            # メタ情報追加（元ファイル行2154-2167と同じ）
            soup = self._add_meta_information(soup, original_url, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            # ファイル名安全化と保存（filename引数優先版）
            # filenameが明示的に指定されている場合は、それを必ず優先
            if filename:
                safe_filename = self.file_manager.sanitize_filename(filename)
                self.logger.debug(f"ファイル名指定優先: {filename}")
            elif title:
                safe_filename = self.file_manager.sanitize_filename(title + ".html")
                self.logger.debug(f"タイトルから生成: {title}.html")
            else:
                safe_filename = "untitled.html"
                self.logger.debug(f"デフォルトファイル名使用: untitled.html")
            
            output_file = os.path.join(output_dir, safe_filename)
            
            # UTF-8 BOM付き保存（元ファイル行2175-2180と同じ）
            html_output = str(soup)
            with open(output_file, 'w', encoding='utf-8-sig') as f:
                f.write(html_output)
            
            self.logger.info(f"ブラウザレベル完全保存完了: {safe_filename}")
            
            return {
                'success': True,
                'file_path': output_file,
                'saved_path': output_file,  # 後方互換性のため残す
                'filename': safe_filename,
                'original_url': original_url,
                'file_size': len(html_output),
                'save_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            self.logger.error(f"完全ページ保存エラー: {e}")
            return {
                'success': False,
                'error': str(e),
                'original_url': original_url
            }
    
    def _add_url_comment(self, soup: BeautifulSoup, original_url: str) -> BeautifulSoup:
        """
        元URLコメント追加（元ファイル行2105-2108と同じ）
        
        Args:
            soup: BeautifulSoupオブジェクト
            original_url: 元のURL
            
        Returns:
            BeautifulSoup: コメント追加済みsoup
        """
        html_tag = soup.find('html')
        if html_tag:
            # 元ファイルと同じ形式のコメント
            comment = Comment(f' saved from url=({len(original_url):04d}){original_url} ')
            html_tag.insert(0, comment)
            self.logger.debug(f"URLコメント追加: {original_url}")
        
        return soup
    
    def _convert_links_to_absolute(self, soup: BeautifulSoup, original_url: str) -> BeautifulSoup:
        """
        相対リンク→絶対パス変換（元ファイル行2114-2150と同じ）
        
        Args:
            soup: BeautifulSoupオブジェクト
            original_url: 元のURL
            
        Returns:
            BeautifulSoup: リンク変換済みsoup
        """
        # ベースURL設定（元ファイル行2113と同じ）
        base_url = '/'.join(original_url.split('/')[:3])  # https://syosetu.org
        current_dir = '/'.join(original_url.split('/')[:-1])
        
        # aタグのhref属性変換（元ファイル行2116-2125）
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href:
                if href.startswith('//'):
                    link['href'] = 'https:' + href
                elif href.startswith('/') and not href.startswith('//'):
                    link['href'] = base_url + href
                elif href.startswith('./'):
                    # 相対パスを絶対パスに変換
                    link['href'] = current_dir + '/' + href[2:]
                self.logger.debug(f"リンク変換: {href} → {link['href']}")
        
        # 画像のsrc属性変換（元ファイル行2127-2134）
        for img in soup.find_all('img', src=True):
            src = img.get('src')
            if src and not src.startswith('./' + self.resources_dir_name + '/'):
                original_src = src
                if src.startswith('//'):
                    img['src'] = 'https:' + src
                elif src.startswith('/') and not src.startswith('//'):
                    img['src'] = base_url + src
                if img['src'] != original_src:
                    self.logger.debug(f"画像リンク変換: {original_src} → {img['src']}")
        
        # CSSリンク変換（元ファイル行2136-2142）
        for link in soup.find_all('link', href=True):
            href = link.get('href')
            if href and not href.startswith('./' + self.resources_dir_name + '/'):
                original_href = href
                if href.startswith('//'):
                    link['href'] = 'https:' + href
                elif href.startswith('/') and not href.startswith('//'):
                    link['href'] = base_url + href
                if link['href'] != original_href:
                    self.logger.debug(f"CSSリンク変換: {original_href} → {link['href']}")
        
        # JSスクリプト変換（元ファイル行2144-2150）
        for script in soup.find_all('script', src=True):
            src = script.get('src')
            if src and not src.startswith('./' + self.resources_dir_name + '/'):
                original_src = src
                if src.startswith('//'):
                    script['src'] = 'https:' + src
                elif src.startswith('/') and not src.startswith('//'):
                    script['src'] = base_url + src
                if script['src'] != original_src:
                    self.logger.debug(f"JSリンク変換: {original_src} → {script['src']}")
        
        return soup
    
    def _add_meta_information(self, soup: BeautifulSoup, original_url: str, save_time: str) -> BeautifulSoup:
        """
        メタ情報追加（元ファイル行2154-2167と同じ）
        
        Args:
            soup: BeautifulSoupオブジェクト
            original_url: 元のURL
            save_time: 保存時刻
            
        Returns:
            BeautifulSoup: メタ情報追加済みsoup
        """
        head = soup.find('head')
        if head:
            # 保存日時メタタグ追加（元ファイル行2157-2161）
            meta_save = soup.new_tag('meta')
            meta_save['name'] = 'save-date'
            meta_save['content'] = save_time
            head.append(meta_save)
            
            # 保存元URLメタタグ追加（元ファイル行2163-2167）
            meta_source = soup.new_tag('meta')
            meta_source['name'] = 'source-url'
            meta_source['content'] = original_url
            head.append(meta_source)
            
            # 生成者情報追加（ハーメルンスクレイパー識別用）
            meta_generator = soup.new_tag('meta')
            meta_generator['name'] = 'generator'
            meta_generator['content'] = 'Hameln Scraper - Novel Preservation Tool'
            head.append(meta_generator)
            
            self.logger.debug(f"メタ情報追加完了: 保存時刻={save_time}, URL={original_url}")
        
        return soup
    
    def add_meta_information(self, soup: BeautifulSoup, original_url: str, save_time: str) -> BeautifulSoup:
        """
        メタ情報追加（テスト用パブリックメソッド）
        
        Args:
            soup: BeautifulSoupオブジェクト
            original_url: 元のURL
            save_time: 保存時刻
            
        Returns:
            BeautifulSoup: メタ情報追加済みsoup
        """
        return self._add_meta_information(soup, original_url, save_time)
    
    def save_with_resources(self, html_content: str, output_dir: str, filename: str,
                           original_url: str, download_resources: bool = True) -> Dict[str, Any]:
        """
        リソース処理制御付き保存
        
        Args:
            html_content: HTMLコンテンツ
            output_dir: 出力ディレクトリ
            filename: ファイル名
            original_url: 元のURL
            download_resources: リソースダウンロード実行フラグ
            
        Returns:
            Dict[str, Any]: 保存結果
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            if download_resources:
                # 完全リソース処理
                if self.processor:
                    soup = self.processor.process_html_resources(soup, output_dir)
            else:
                # パス調整のみ
                if self.processor:
                    soup = self.processor.adjust_resource_paths_only(soup, output_dir)
            
            # メタ情報・リンク変換は常に実行
            soup = self._add_url_comment(soup, original_url)
            soup = self._convert_links_to_absolute(soup, original_url)
            soup = self._add_meta_information(soup, original_url, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            # 保存
            safe_filename = self.file_manager.sanitize_filename(filename)
            output_file = os.path.join(output_dir, safe_filename)
            
            with open(output_file, 'w', encoding='utf-8-sig') as f:
                f.write(str(soup))
            
            return {
                'success': True,
                'saved_path': output_file,
                'filename': safe_filename,
                'resources_downloaded': download_resources
            }
            
        except Exception as e:
            self.logger.error(f"リソース制御付き保存エラー: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_save_stats(self) -> Dict[str, Any]:
        """
        保存統計情報取得
        
        Returns:
            Dict[str, Any]: 保存統計
        """
        return {
            'resources_dir_name': self.resources_dir_name,
            'encoding': 'utf-8-sig',
            'meta_tags_added': ['save-date', 'source-url', 'generator'],
            'link_conversion_types': ['a[href]', 'img[src]', 'link[href]', 'script[src]']
        }