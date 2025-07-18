"""
ファイル管理モジュール
HTMLファイルの保存とローカルナビゲーションリンクの修正
"""

import os
import re
import logging
from datetime import datetime
from urllib.parse import urljoin
from bs4 import BeautifulSoup, Comment


class FileManager:
    """ファイル管理クラス"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.base_url = config.base_url
    
    def _sanitize_filename(self, filename):
        """ファイル名を安全な形式に変換"""
        return re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    def save_complete_page(self, soup, base_url, title, save_dir, page_url):
        """ページを完全な形で保存（ブラウザ保存と同等）"""
        self.logger.info("=== ブラウザレベル完全保存開始 ===")
        
        resources_dir_name = getattr(self, 'browser_compatible_name', 'resources')
        
        html_tag = soup.find('html')
        if html_tag:
            comment = Comment(f' saved from url=({len(page_url):04d}){page_url} ')
            html_tag.insert(0, comment)
        
        base_url = '/'.join(page_url.split('/')[:3])
        
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href:
                if href.startswith('//'):
                    link['href'] = 'https:' + href
                elif href.startswith('/') and not href.startswith('//'):
                    link['href'] = base_url + href
                elif href.startswith('./'):
                    current_dir = '/'.join(page_url.split('/')[:-1])
                    link['href'] = current_dir + '/' + href[2:]
        
        for img in soup.find_all('img', src=True):
            src = img.get('src')
            if src and not src.startswith('./' + resources_dir_name + '/'):
                if src.startswith('//'):
                    img['src'] = 'https:' + src
                elif src.startswith('/') and not src.startswith('//'):
                    img['src'] = base_url + src
        
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
        
        head = soup.find('head')
        if head:
            save_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            meta_save = soup.new_tag('meta')
            meta_save['name'] = 'save-date'
            meta_save['content'] = save_time
            head.append(meta_save)
            
            meta_source = soup.new_tag('meta')
            meta_source['name'] = 'source-url'
            meta_source['content'] = page_url
            head.append(meta_source)
        
        safe_filename = self._sanitize_filename(title)
        output_file = os.path.join(save_dir, f"{safe_filename}.html")
        
        html_content = str(soup)
        
        with open(output_file, 'w', encoding='utf-8-sig') as f:
            f.write(html_content)
        
        self.logger.info(f"=== ブラウザレベル完全保存完了: {output_file} ===")
        return output_file
    
    def fix_local_navigation_links(self, soup, chapter_mapping, current_url, 
                                 index_filename=None, info_file_name=None, 
                                 comments_file_name=None):
        """ローカルナビゲーションリンクを修正"""
        try:
            self.logger.debug(f"ナビゲーションリンク修正開始: {current_url}")
            
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                link_text = link.get_text(strip=True)
                
                if not href:
                    continue
                
                original_href = href
                
                if href.startswith('http'):
                    if any(domain in href for domain in ['syosetu.org']):
                        if href in chapter_mapping:
                            link['href'] = chapter_mapping[href]
                            self.logger.debug(f"章リンク修正: {original_href} -> {chapter_mapping[href]}")
                        elif '/novel/' in href and href.endswith('/'):
                            if index_filename:
                                link['href'] = index_filename
                                self.logger.debug(f"目次リンク修正: {original_href} -> {index_filename}")
                        elif 'mode=ss_detail' in href:
                            if info_file_name:
                                link['href'] = info_file_name
                                self.logger.debug(f"小説情報リンク修正: {original_href} -> {info_file_name}")
                        elif 'mode=review' in href:
                            if comments_file_name:
                                link['href'] = comments_file_name
                                self.logger.debug(f"感想リンク修正: {original_href} -> {comments_file_name}")
                
                elif href.startswith('./'):
                    chapter_num_match = re.search(r'(\d+)\.html$', href)
                    if chapter_num_match:
                        for chapter_url, local_file in chapter_mapping.items():
                            if chapter_num_match.group(1) in chapter_url:
                                link['href'] = local_file
                                self.logger.debug(f"相対章リンク修正: {original_href} -> {local_file}")
                                break
                
                elif href.startswith('/'):
                    full_url = urljoin(self.base_url, href)
                    if full_url in chapter_mapping:
                        link['href'] = chapter_mapping[full_url]
                        self.logger.debug(f"絶対章リンク修正: {original_href} -> {chapter_mapping[full_url]}")
                    elif '/novel/' in href and href.endswith('/'):
                        if index_filename:
                            link['href'] = index_filename
                            self.logger.debug(f"絶対目次リンク修正: {original_href} -> {index_filename}")
                
                if any(keyword in link_text for keyword in ['目次', 'インデックス', 'もくじ']):
                    if index_filename:
                        link['href'] = index_filename
                        self.logger.debug(f"目次テキストリンク修正: {original_href} -> {index_filename}")
                elif any(keyword in link_text for keyword in ['小説情報', '作品情報']):
                    if info_file_name:
                        link['href'] = info_file_name
                        self.logger.debug(f"小説情報テキストリンク修正: {original_href} -> {info_file_name}")
                elif any(keyword in link_text for keyword in ['感想', 'レビュー']):
                    if comments_file_name:
                        link['href'] = comments_file_name
                        self.logger.debug(f"感想テキストリンク修正: {original_href} -> {comments_file_name}")
            
            self.logger.debug("ナビゲーションリンク修正完了")
            return soup
            
        except Exception as e:
            self.logger.error(f"ナビゲーションリンク修正エラー: {e}")
            return soup
