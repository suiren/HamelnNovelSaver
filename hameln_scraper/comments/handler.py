"""
感想ページ処理モジュール
複数ページの感想取得と統合処理
"""

import time
import copy
import logging
import os
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup


class CommentsHandler:
    """感想ページ処理クラス"""
    
    def __init__(self, config, network_client, file_manager):
        self.config = config
        self.network_client = network_client
        self.file_manager = file_manager
        self.logger = logging.getLogger(__name__)
    
    def get_all_comments_pages(self, base_comments_url):
        """複数ページの感想を全て取得して統合"""
        try:
            self.logger.info("感想ページのページネーション検出を開始")
            
            first_page_soup = self.network_client.get_page(base_comments_url)
            if not first_page_soup:
                return None
            
            first_page_soup = BeautifulSoup(first_page_soup, 'html.parser')
            
            page_links = self.detect_comments_pagination(first_page_soup, base_comments_url)
            
            if len(page_links) <= 1:
                self.logger.info("感想は1ページのみです")
                return first_page_soup
            
            self.logger.info(f"感想ページ数: {len(page_links)}ページ")
            
            all_comments = []
            
            for page_num, page_url in enumerate(page_links, 1):
                self.logger.info(f"感想ページ {page_num}/{len(page_links)} を取得中: {page_url}")
                
                if page_num == 1:
                    page_soup = first_page_soup
                else:
                    time.sleep(2)
                    page_html = self.network_client.get_page(page_url)
                    if not page_html:
                        self.logger.warning(f"感想ページ {page_num} の取得に失敗")
                        continue
                    page_soup = BeautifulSoup(page_html, 'html.parser')
                
                comments_content = self.extract_comments_content(page_soup)
                if comments_content:
                    all_comments.extend(comments_content)
            
            if not all_comments:
                self.logger.warning("感想コンテンツが見つかりませんでした")
                return first_page_soup
            
            integrated_soup = self.create_integrated_comments_page(first_page_soup, all_comments, len(page_links))
            self.logger.info(f"感想ページ統合完了: {len(all_comments)}件の感想を統合")
            
            return integrated_soup
            
        except Exception as e:
            self.logger.error(f"感想ページ統合エラー: {e}")
            return None
    
    def detect_comments_pagination(self, soup, base_url):
        """感想ページのページネーションを検出"""
        try:
            page_links = []
            base_page_num = self.extract_page_number(base_url)
            
            pagination_selectors = [
                'div.pagination a',
                'div.pager a', 
                'div.page-nav a',
                'a[href*="mode=review"][href*="page="]',
                'a[href*="&page="]'
            ]
            
            for selector in pagination_selectors:
                pagination_links = soup.select(selector)
                if pagination_links:
                    self.logger.debug(f"ページネーション発見: {selector} ({len(pagination_links)}個のリンク)")
                    
                    for link in pagination_links:
                        href = link.get('href')
                        if href and 'page=' in href:
                            if href.startswith('?'):
                                full_url = base_url.split('?')[0] + href
                            elif href.startswith('./'):
                                full_url = base_url.split('?')[0] + href[2:]
                            elif href.startswith('//'):
                                full_url = f"https:{href}"
                            elif href.startswith('/'):
                                full_url = 'https://syosetu.org' + href
                            elif href.startswith('http'):
                                full_url = href
                            else:
                                continue
                            
                            page_num = self.extract_page_number(full_url)
                            if not any(self.extract_page_number(existing_url) == page_num for existing_url in page_links):
                                page_links.append(full_url)
                    break
            
            if not any(self.extract_page_number(url) == base_page_num for url in page_links):
                page_links.append(base_url)
            
            page_links.sort(key=lambda url: self.extract_page_number(url))
            
            self.logger.debug(f"検出されたページ: {len(page_links)}ページ")
            for i, url in enumerate(page_links, 1):
                self.logger.debug(f"  ページ{i}: {url}")
            
            return page_links
            
        except Exception as e:
            self.logger.error(f"ページネーション検出エラー: {e}")
            return [base_url]
    
    def extract_comments_content(self, soup):
        """感想コンテンツを抽出"""
        try:
            comments = []
            
            comment_selectors = [
                'div[id*="review"]',
                'div.review-item',
                'div.comment-item', 
                'div.impression',
                'tr[id*="review"]',
                'div[class*="review_"]',
                'div[class*="review"]',
                'div[class*="comment"]'
            ]
            
            for selector in comment_selectors:
                comment_elements = soup.select(selector)
                if comment_elements:
                    self.logger.debug(f"感想要素発見: {selector} ({len(comment_elements)}件)")
                    comments.extend(comment_elements)
                    break
            
            if not comments:
                table_rows = soup.find_all('tr')
                for row in table_rows:
                    text = row.get_text().strip()
                    if len(text) > 20 and any(keyword in text for keyword in ['面白', '良い', '素晴らしい', '感動', '続き']):
                        comments.append(row)
            
            self.logger.debug(f"抽出された感想: {len(comments)}件")
            return comments
            
        except Exception as e:
            self.logger.error(f"感想コンテンツ抽出エラー: {e}")
            return []
    
    def create_integrated_comments_page(self, base_soup, all_comments, total_pages):
        """統合された感想ページを作成"""
        try:
            integrated_soup = copy.deepcopy(base_soup)
            
            for selector in ['div[id*="review"]', 'div.review-item', 'div.comment-item', 'tr[id*="review"]']:
                existing_comments = integrated_soup.select(selector)
                for comment in existing_comments:
                    comment.decompose()
            
            content_area = integrated_soup.find('div', class_='content') or integrated_soup.find('div', class_='main') or integrated_soup.find('body')
            
            if content_area and all_comments:
                for comment in all_comments:
                    if comment:
                        content_area.append(copy.deepcopy(comment))
            
            self.logger.debug("感想ページ統合完了")
            return integrated_soup
            
        except Exception as e:
            self.logger.error(f"感想ページ統合作成エラー: {e}")
            import traceback
            self.logger.error(f"統合エラー詳細: {traceback.format_exc()}")
            return base_soup
    
    def extract_page_number(self, url):
        """URLからページ番号を抽出"""
        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            
            if 'page' in params:
                return int(params['page'][0])
            else:
                return 1
                
        except Exception as e:
            self.logger.debug(f"ページ番号抽出エラー: {e}")
            return 1
    
    def save_comments_page(self, comments_url, output_dir, novel_title, index_file_name=None):
        """感想ページを保存"""
        try:
            self.logger.info(f"感想ページを取得中: {comments_url}")
            
            page_links = []
            first_page_html = self.network_client.get_page(comments_url)
            if not first_page_html:
                self.logger.error("感想ページの取得に失敗しました")
                return None
            
            first_page_soup = BeautifulSoup(first_page_html, 'html.parser')
            page_links = self.detect_comments_pagination(first_page_soup, comments_url)
            
            if len(page_links) <= 1:
                self.logger.info("感想は1ページのみです")
                integrated_soup = first_page_soup
                safe_title = self.file_manager._sanitize_filename(novel_title)
                comments_filename = f"{safe_title} - 感想"
                
                comments_file_path = self.file_manager.save_complete_page(
                    integrated_soup,
                    comments_url,
                    comments_filename,
                    output_dir,
                    comments_url
                )
                
                if comments_file_path:
                    self.logger.info(f"感想ページ保存完了: {comments_file_path}")
                    return comments_file_path
                else:
                    self.logger.error("感想ページの保存に失敗しました")
                    return None
            
            self.logger.info(f"複数ページの感想を保存中: {len(page_links)}ページ")
            
            comments_dir = os.path.join(output_dir, "感想")
            os.makedirs(comments_dir, exist_ok=True)
            
            saved_files = []
            
            for page_num, page_url in enumerate(page_links, 1):
                self.logger.info(f"感想ページ {page_num}/{len(page_links)} を保存中")
                
                if page_num == 1:
                    page_soup = first_page_soup
                else:
                    time.sleep(2)
                    page_html = self.network_client.get_page(page_url)
                    if not page_html:
                        self.logger.warning(f"感想ページ {page_num} の取得に失敗")
                        continue
                    page_soup = BeautifulSoup(page_html, 'html.parser')
                
                page_filename = f"感想 - ページ{page_num}"
                page_file_path = self.file_manager.save_complete_page(
                    page_soup,
                    page_url,
                    page_filename,
                    comments_dir,
                    page_url
                )
                
                if page_file_path:
                    saved_files.append(page_file_path)
                    self.logger.info(f"感想ページ{page_num}保存完了: {os.path.basename(page_file_path)}")
            
            if saved_files:
                self.fix_comments_page_links(saved_files, page_links, index_file_name)
                self.logger.info(f"感想ページ保存完了: {len(saved_files)}ページ保存")
                return saved_files[0]
            else:
                self.logger.error("感想ページの保存に失敗しました")
                return None
                
        except Exception as e:
            self.logger.error(f"感想ページ保存エラー: {e}")
            return None
    
    def fix_comments_page_links(self, saved_files, page_urls, index_file_name=None):
        """感想ページ間のリンクを修正"""
        try:
            page_mapping = {}
            for i, (file_path, url) in enumerate(zip(saved_files, page_urls), 1):
                page_mapping[url] = os.path.basename(file_path)
            
            for i, file_path in enumerate(saved_files):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                soup = BeautifulSoup(content, 'html.parser')
                
                for link in soup.find_all('a', href=True):
                    href = link.get('href')
                    if not href:
                        continue
                    
                    if 'mode=review' in href:
                        matched_file = self.find_matching_comments_page(href, page_mapping)
                        if matched_file:
                            link['href'] = matched_file
                            self.logger.debug(f"感想ページリンク修正: {href} -> {matched_file}")
                    
                    elif ('/novel/' in href and href.endswith('/')) or '目次' in link.get_text():
                        if index_file_name:
                            link['href'] = f'../{index_file_name}'
                            self.logger.debug(f"目次リンク修正: {href} -> ../{index_file_name}")
                        else:
                            link['href'] = '../目次.html'
                            self.logger.debug(f"目次リンク修正: {href} -> ../目次.html")
                    
                    elif 'mode=ss_detail' in href or '小説情報' in link.get_text():
                        link['href'] = '../小説情報.html'
                        self.logger.debug(f"小説情報リンク修正: {href} -> ../小説情報.html")
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(str(soup))
                
        except Exception as e:
            self.logger.error(f"感想ページリンク修正エラー: {e}")
    
    def find_matching_comments_page(self, href, page_mapping):
        """感想ページのURLから正確なローカルファイルを探す"""
        try:
            target_page_num = self.extract_page_number(href)
            target_base_url = self.extract_base_comments_url(href)
            
            for original_url, local_file in page_mapping.items():
                original_page_num = self.extract_page_number(original_url)
                original_base_url = self.extract_base_comments_url(original_url)
                
                if (target_base_url == original_base_url and 
                    target_page_num == original_page_num):
                    return local_file
            
            return None
            
        except Exception as e:
            self.logger.error(f"感想ページマッチングエラー: {e}")
            return None
    
    def extract_base_comments_url(self, url):
        """URLから基本URL（nid部分）を抽出"""
        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            
            base_params = {}
            if 'mode' in params:
                base_params['mode'] = params['mode'][0]
            if 'nid' in params:
                base_params['nid'] = params['nid'][0]
            
            base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if base_params:
                param_str = '&'.join([f"{k}={v}" for k, v in base_params.items()])
                base_url += f"?{param_str}"
            
            return base_url
            
        except Exception as e:
            self.logger.error(f"基本URL抽出エラー: {e}")
            return url
