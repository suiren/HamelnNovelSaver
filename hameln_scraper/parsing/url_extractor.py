"""
URL抽出モジュール - ハーメルン2024年対応完全版
"""

import logging
import re
from bs4 import BeautifulSoup
from typing import Optional, List, Dict, Any
from urllib.parse import urljoin


class UrlExtractor:
    """URL抽出クラス - ハーメルン2024年対応完全版"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_chapter_links(self, soup: BeautifulSoup, base_novel_url: str) -> Dict[str, Any]:
        """
        章のリンクを抽出（ハーメルン特化版 - 目次ページ対応）
        
        Args:
            soup: BeautifulSoupオブジェクト
            base_novel_url: 小説のベースURL
            
        Returns:
            Dict[str, Any]: 章リンクのリストと目次ページ情報を含む
                - chapter_links: List[Dict[str, str]] 章リンクのリスト
                - index_page: Dict[str, str] 目次ページ情報（URLとタイトル）
        """
        chapter_links = []
        index_page = None  # 目次ページ情報を保存
        
        self.logger.debug("章リンクを検索中...")
        
        # 現在の作品IDを抽出
        novel_id_match = re.search(r'/novel/(\d+)', base_novel_url)
        if not novel_id_match:
            self.logger.error("作品IDの抽出に失敗しました")
            return {
                'chapter_links': [],
                'index_page': None,
                'error': '作品IDの抽出に失敗しました'
            }
        
        novel_id = novel_id_match.group(1)
        self.logger.debug(f"対象作品ID: {novel_id}")
        
        # ハーメルン特有のセレクターで章リンクを検索（作品ID限定）
        chapter_selectors = [
            # ハーメルンの一般的な章リスト
            ('div', {'class': 'chapter_list'}),
            ('ul', {'class': 'episode_list'}),
            ('div', {'class': 'episode_list'}),
            # 特定作品の章のみ（作品ID限定）
            ('a', {'href': lambda x: x and f'/novel/{novel_id}/' in x and x.count('/') >= 4}),
            # 相対パス形式の章リンク（./2.html, ./3.html等）
            ('a', {'href': lambda x: x and re.match(r'\./\d+\.html$', x)}),
            ('li', {'class': 'chapter'}),
            ('div', {'class': 'novel_sublist'}),
            # 汎用的なリンクパターン
            ('a', {'href': lambda x: x and re.match(rf'/novel/{novel_id}/\d+/', x)})
        ]
        
        processed_urls = set()  # 重複チェック用
        
        for tag, attrs in chapter_selectors:
            self.logger.debug(f"セレクター試行: {tag} {attrs}")
            
            try:
                if callable(attrs.get('href')):
                    elements = soup.find_all(tag, href=attrs['href'])
                else:
                    elements = soup.find_all(tag, attrs)
                
                self.logger.debug(f"見つかった要素数: {len(elements)}")
                
                for element in elements:
                    if tag == 'a':
                        href = element.get('href')
                        title = element.get_text(strip=True)
                        if href:
                            # 相対パス形式の章リンクの場合は絶対URLに変換
                            if re.match(r'\./\d+\.html$', href):
                                # 相対パスを絶対URLに変換
                                full_url = urljoin(base_novel_url, href)
                                if full_url not in processed_urls:
                                    chapter_links.append({
                                        'title': title,
                                        'url': full_url  # 絶対URLに変換
                                    })
                                    processed_urls.add(full_url)
                                    self.logger.debug(f"✓ 章リンク追加（相対→絶対）: {title[:30]}... -> {full_url}")
                            else:
                                # その他の場合は絶対パスに変換
                                full_url = urljoin(base_novel_url, href)
                                
                                # 絶対パス形式の場合は作品ID検証
                                if f'/novel/{novel_id}/' in full_url:
                                    # 目次ページ（base_novel_urlと同一）を別途記録
                                    if full_url == base_novel_url:
                                        if not index_page:  # 最初の目次ページのみ記録
                                            index_page = {
                                                'title': title if title else '目次',
                                                'url': full_url
                                            }
                                            self.logger.debug(f"✓ 目次ページを記録: {title[:30] if title else '目次'}... -> {full_url}")
                                    elif full_url not in processed_urls:
                                        chapter_links.append({
                                            'title': title,
                                            'url': full_url
                                        })
                                        processed_urls.add(full_url)
                                        self.logger.debug(f"✓ 章リンク追加（絶対パス）: {title[:30]}... -> {full_url}")
                    else:
                        # div や ul の場合は内部のaタグを探す
                        links = element.find_all('a', href=True)
                        self.logger.debug(f"コンテナ内のリンク数: {len(links)}")
                        for link in links:
                            href = link.get('href')
                            if href and '/novel/' in href:
                                title = link.get_text(strip=True)
                                full_url = urljoin(base_novel_url, href)
                                # 作品ID検証
                                if f'/novel/{novel_id}/' in full_url:
                                    # 目次ページ（base_novel_urlと同一）を別途記録
                                    if full_url == base_novel_url:
                                        if not index_page:  # 最初の目次ページのみ記録
                                            index_page = {
                                                'title': title if title else '目次',
                                                'url': full_url
                                            }
                                            self.logger.debug(f"✓ 目次ページを記録: {title[:30] if title else '目次'}... -> {full_url}")
                                    elif full_url not in processed_urls:
                                        chapter_links.append({
                                            'title': title,
                                            'url': full_url
                                        })
                                        processed_urls.add(full_url)
                                        self.logger.debug(f"✓ 章リンク追加: {title[:30]}... -> {full_url}")
                                        
            except Exception as e:
                self.logger.error(f"セレクター試行エラー: {e}")
        
        # シンプルなテスト用のフォールバック
        if not chapter_links:
            # テスト用の基本的な章リンク抽出
            self.logger.debug("フォールバック: 基本的な章リンク検索")
            links = soup.find_all('a', href=True)
            for link in links:
                href = link.get('href')
                if href and f'/novel/{novel_id}/' in href:
                    title = link.get_text(strip=True)
                    full_url = urljoin(base_novel_url, href)
                    # フォールバック処理でも目次ページを考慮
                    if full_url == base_novel_url:
                        if not index_page:
                            index_page = {
                                'title': title if title else '目次',
                                'url': full_url
                            }
                    elif full_url not in processed_urls:
                        chapter_links.append({
                            'title': title,
                            'url': full_url
                        })
                        processed_urls.add(full_url)
        
        # 目次ページが見つからない場合はデフォルト設定
        if not index_page:
            index_page = {
                'title': '目次',
                'url': base_novel_url
            }
            self.logger.debug(f"デフォルト目次ページを設定: {base_novel_url}")
        
        self.logger.debug(f"章リンク抽出完了: {len(chapter_links)}個、目次ページ: {index_page['title']}")
        return {
            'chapter_links': chapter_links,
            'index_page': index_page
        }
    
    def extract_chapter_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """
        章リンクを抽出（HamelnModularScraper互換メソッド）
        
        Args:
            soup: BeautifulSoupオブジェクト
            base_url: ベースURL
            
        Returns:
            List[str]: 抽出された章リンクのリスト（URLのみ）
        """
        # get_chapter_linksを呼び出してURLのみを抽出（新しい辞書形式対応）
        result = self.get_chapter_links(soup, base_url)
        if isinstance(result, dict) and 'chapter_links' in result:
            chapter_data = result['chapter_links']
            return [item['url'] if isinstance(item, dict) else item for item in chapter_data]
        else:
            # 古い形式の場合のフォールバック
            return [item['url'] if isinstance(item, dict) else item for item in result] if isinstance(result, list) else []
    
    def extract_novel_info_url(self, soup: BeautifulSoup) -> Optional[str]:
        """
        小説情報URLを抽出
        
        Args:
            soup: BeautifulSoupオブジェクト
            
        Returns:
            Optional[str]: 小説情報URL
        """
        # ハーメルン特有のinfo URLパターン
        info_selectors = [
            ('a', {'href': lambda x: x and 'info' in x}),
            ('a', {'text': lambda x: x and '小説情報' in x}),
            ('a', {'href': lambda x: x and '/novel/' in x and '/info/' in x}),
            ('link', {'rel': 'canonical', 'href': lambda x: x and '/info/' in x})
        ]
        
        for tag, attrs in info_selectors:
            if 'href' in attrs and callable(attrs['href']):
                element = soup.find(tag, href=attrs['href'])
            elif 'text' in attrs and callable(attrs['text']):
                element = soup.find(tag, string=attrs['text'])
                if element:
                    element = element.parent if element.parent and element.parent.name == 'a' else element
            else:
                element = soup.find(tag, attrs)
            
            if element and element.get('href'):
                return element.get('href')
        
        return None
    
    def extract_comments_url(self, soup: BeautifulSoup) -> Optional[str]:
        """
        感想URLを抽出
        
        Args:
            soup: BeautifulSoupオブジェクト
            
        Returns:
            Optional[str]: 感想URL
        """
        # ハーメルン特有のcomments URLパターン
        comments_selectors = [
            ('a', {'href': lambda x: x and 'comments' in x}),
            ('a', {'text': lambda x: x and '感想' in x}),
            ('a', {'href': lambda x: x and '/novel/' in x and '/comments/' in x}),
            ('link', {'rel': 'alternate', 'href': lambda x: x and '/comments/' in x})
        ]
        
        for tag, attrs in comments_selectors:
            if 'href' in attrs and callable(attrs['href']):
                element = soup.find(tag, href=attrs['href'])
            elif 'text' in attrs and callable(attrs['text']):
                element = soup.find(tag, string=attrs['text'])
                if element:
                    element = element.parent if element.parent and element.parent.name == 'a' else element
            else:
                element = soup.find(tag, attrs)
            
            if element and element.get('href'):
                return element.get('href')
        
        return None
    
    def extract_all_novel_urls(self, soup: BeautifulSoup, base_novel_url: str) -> Dict[str, Optional[str]]:
        """
        小説関連のすべてのURLを一括抽出
        
        Args:
            soup: BeautifulSoupオブジェクト
            base_novel_url: 小説のベースURL
            
        Returns:
            Dict[str, Optional[str]]: 各種URLの辞書
        """
        return {
            'info_url': self.extract_novel_info_url(soup),
            'comments_url': self.extract_comments_url(soup),
            'chapter_links': self.get_chapter_links(soup, base_novel_url)
        }