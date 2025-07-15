"""
小説処理モジュール
小説情報の抽出、章リンクの取得、本文の抽出
"""

import re
import logging
from urllib.parse import urljoin
from bs4 import BeautifulSoup


class NovelProcessor:
    """小説処理クラス"""
    
    def __init__(self, config, network_client):
        self.config = config
        self.network_client = network_client
        self.logger = logging.getLogger(__name__)
        self.base_url = config.base_url
    
    def extract_novel_info(self, soup):
        """小説の基本情報を抽出"""
        info = {}
        
        self.logger.debug("小説情報抽出開始")
        
        title_selectors = [
            ('div', {'class': 'section1'}),
            ('div', {'class': 'section2'}),
            ('h1', {'class': lambda x: x and any(cls.startswith('section') for cls in x if isinstance(cls, str))}),
            ('h1', {'class': 'p-novel-title'}),
            ('h1', {'class': 'novel-title'}),
            ('div', {'class': 'p-novel-title'}),
            ('span', {'class': 'novel-title'}),
            ('h1', {'class': 'title'}),
            ('h1', {'class': 'novel_title'}),
            ('div', {'class': 'novel_title'}),
            ('h1', {}),
            ('title', {})
        ]
        
        self.logger.debug("タイトル抽出試行中...")
        for tag, attrs in title_selectors:
            self.logger.debug(f"タイトルセレクター試行: {tag} {attrs}")
            title_elem = soup.find(tag, attrs) if attrs else soup.find(tag)
            if title_elem:
                title_text = title_elem.get_text(strip=True)
                if ' - ハーメルン' in title_text:
                    title_text = title_text.replace(' - ハーメルン', '')
                if title_text and title_text not in ['Unknown Title', '']:
                    info['title'] = title_text
                    self.logger.debug(f"タイトル取得成功: {title_text}")
                    break
            else:
                self.logger.debug(f"セレクター {tag} {attrs} で要素が見つかりませんでした")
        
        author_selectors = [
            ('a', {'class': 'p-novel-author'}),
            ('span', {'class': 'p-novel-author'}),
            ('div', {'class': 'novel-author'}),
            ('a', {'class': 'author-link'}),
            ('a', {'href': lambda x: x and '/user/' in x}),
            ('div', {'class': 'author'}),
            ('span', {'class': 'author'}),
            ('a', {'class': 'author'})
        ]
        
        self.logger.debug("作者抽出試行中...")
        for tag, attrs in author_selectors:
            self.logger.debug(f"作者セレクター試行: {tag} {attrs}")
            if callable(attrs.get('href')):
                author_elem = soup.find(tag, href=attrs['href'])
            else:
                author_elem = soup.find(tag, attrs)
            
            if author_elem:
                author_text = author_elem.get_text(strip=True)
                if author_text and author_text not in ['Unknown Author', '']:
                    info['author'] = author_text
                    self.logger.debug(f"作者取得成功: {author_text}")
                    break
            else:
                self.logger.debug(f"セレクター {tag} {attrs} で要素が見つかりませんでした")
        
        if not info.get('title') or not info.get('author'):
            self.logger.warning("基本情報取得失敗、詳細調査を実行")
            self.investigate_page_structure(soup)
        
        return info
    
    def investigate_page_structure(self, soup):
        """ページ構造を詳細調査"""
        self.logger.debug("=== ページ構造詳細調査 ===")
        
        h1_tags = soup.find_all('h1')
        self.logger.debug(f"h1タグ数: {len(h1_tags)}")
        for i, h1 in enumerate(h1_tags[:5]):
            classes = h1.get('class', [])
            text = h1.get_text(strip=True)[:50]
            self.logger.debug(f"  h1[{i}]: class={classes}, text={text}...")
        
        links = soup.find_all('a', href=True)
        self.logger.debug(f"リンク数: {len(links)}")
        user_links = [link for link in links if '/user/' in link.get('href', '')]
        self.logger.debug(f"ユーザーリンク数: {len(user_links)}")
        for i, link in enumerate(user_links[:3]):
            classes = link.get('class', [])
            text = link.get_text(strip=True)[:30]
            href = link.get('href')
            self.logger.debug(f"  userlink[{i}]: class={classes}, text={text}..., href={href}")
        
        divs_with_class = soup.find_all('div', class_=True)
        unique_classes = set()
        for div in divs_with_class:
            for cls in div.get('class', []):
                if any(keyword in cls.lower() for keyword in ['title', 'author', 'novel', 'name']):
                    unique_classes.add(cls)
        
        self.logger.debug(f"関連クラス名: {sorted(unique_classes)}")
        
        spans_with_class = soup.find_all('span', class_=True)
        span_classes = set()
        for span in spans_with_class:
            for cls in span.get('class', []):
                if any(keyword in cls.lower() for keyword in ['title', 'author', 'novel', 'name']):
                    span_classes.add(cls)
        
        self.logger.debug(f"関連spanクラス名: {sorted(span_classes)}")
    
    def get_chapter_links(self, soup, base_novel_url):
        """章のリンクを抽出"""
        chapter_links = []
        
        self.logger.info("章リンクを検索中...")
        
        novel_id_match = re.search(r'/novel/(\d+)', base_novel_url)
        if not novel_id_match:
            self.logger.error("作品IDの抽出に失敗しました")
            return []
        
        novel_id = novel_id_match.group(1)
        self.logger.info(f"対象作品ID: {novel_id}")
        
        chapter_selectors = [
            ('div', {'class': 'chapter_list'}),
            ('ul', {'class': 'episode_list'}),
            ('div', {'class': 'episode_list'}),
            ('a', {'href': lambda x: x and f'/novel/{novel_id}/' in x and x.count('/') >= 4 and x.endswith('.html')}),
            ('a', {'href': lambda x: x and re.match(r'\./\d+\.html$', x)}),
            ('li', {'class': 'chapter'}),
            ('div', {'class': 'novel_sublist'})
        ]
        
        for tag, attrs in chapter_selectors:
            self.logger.debug(f"セレクター試行: {tag} {attrs}")
            
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
                        full_url = urljoin(base_novel_url, href)
                        
                        if f'/novel/{novel_id}/' in full_url:
                            if full_url not in chapter_links:
                                chapter_links.append(full_url)
                                self.logger.debug(f"✓ 章リンク追加: {title[:30]}... -> {full_url}")
                            else:
                                self.logger.debug(f"重複スキップ: {full_url}")
                        else:
                            self.logger.debug(f"✗ 作品ID不一致でスキップ: {full_url} (期待ID: {novel_id})")
                else:
                    for link in element.find_all('a', href=True):
                        href = link.get('href')
                        if href and '/novel/' in href:
                            title = link.get_text(strip=True)
                            full_url = urljoin(self.base_url, href)
                            if f'/novel/{novel_id}/' in full_url:
                                if full_url not in chapter_links:
                                    chapter_links.append(full_url)
                                    self.logger.debug(f"✓ 章リンク追加: {title[:30]}... -> {full_url}")
                                else:
                                    self.logger.debug(f"重複スキップ: {full_url}")
                            else:
                                self.logger.debug(f"✗ 作品ID不一致でスキップ: {full_url} (期待ID: {novel_id})")
        
        if not chapter_links:
            self.logger.info("通常のリンク検索に切り替え...")
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                text = link.get_text(strip=True)
                
                if re.match(r'\./\d+\.html$', href):
                    full_url = urljoin(base_novel_url, href)
                    if full_url not in chapter_links:
                        chapter_links.append(full_url)
                        self.logger.debug(f"フォールバック章リンク（相対パス）: {text[:30]}... -> {full_url}")
                    else:
                        self.logger.debug(f"重複スキップ: {full_url}")
                elif (href and '/novel/' in href and 
                    len(href.split('/')) >= 4 and 
                    href != base_novel_url and
                    not any(x in href for x in ['user', 'tag', 'search', 'ranking'])):
                    
                    full_url = urljoin(self.base_url, href)
                    
                    if f'/novel/{novel_id}/' in full_url:
                        if full_url not in chapter_links:
                            chapter_links.append(full_url)
                            self.logger.debug(f"フォールバック章リンク（絶対パス）: {text[:30]}... -> {full_url}")
                        else:
                            self.logger.debug(f"重複スキップ: {full_url}")
                    else:
                        self.logger.debug(f"✗ フォールバック作品ID不一致でスキップ: {full_url} (期待ID: {novel_id})")
        
        unique_links = []
        for link in chapter_links:
            if link not in unique_links:
                unique_links.append(link)
        
        self.logger.info(f"最終的な章数: {len(unique_links)}")
        return unique_links
    
    def extract_chapter_content(self, soup, chapter_url):
        """章の本文を抽出"""
        self.logger.debug(f"本文抽出開始: {chapter_url}")
        
        content_selectors = [
            ('div', {'id': 'honbun'}),
            ('div', {'id': 'entry_box'}),
            ('div', {'class': 'section3'}),
            ('div', {'class': 'section1'}),
            ('div', {'class': 'section2'}),
            ('div', {'class': 'section4'}),
            ('div', {'class': 'section5'}),
            ('div', {'class': 'section6'}),
            ('div', {'class': 'section7'}),
            ('div', {'class': 'section8'}),
            ('div', {'class': 'section9'}),
            ('div', {'class': lambda x: x and any(cls.startswith('section') and len(cls) > 7 and cls[7:].isdigit() for cls in x if isinstance(cls, str))}),
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
            ('div', {'id': 'novel_body'}),
            ('div', {'id': 'main_text'}),
            ('div', {'id': 'chapter_body'}),
            ('div', {'id': 'story_body'}),
            ('div', {'id': 'content_body'}),
            ('div', {'id': 'episode_body'}),
            ('div', {'class': 'novel_body'}),
            ('div', {'class': 'novel_view'}),
            ('div', {'class': 'novel_content'}),
            ('div', {'class': 'chapter_body'}),
            ('div', {'class': 'ss_body'}),
            ('div', {'class': 'contents'}),
            ('div', {'class': 'main_content'}),
            ('div', {'class': 'story_content'}),
            ('article', {'class': None}),
            ('main', {'class': None}),
            ('section', {'class': None}),
            ('div', {'class': lambda x: x and any(keyword in ' '.join(x).lower() for keyword in ['body', 'content', 'text', 'story', 'chapter', 'episode', 'novel'])}),
            ('div', {'data-content': 'main'}),
            ('div', {'role': 'main'}),
        ]
        
        for tag, attrs in content_selectors:
            self.logger.debug(f"本文セレクター試行: {tag} {attrs}")
            
            try:
                if callable(attrs.get('class')):
                    elements = soup.find_all(tag, class_=attrs['class'])
                elif callable(attrs.get('id')):
                    elements = soup.find_all(tag, id=attrs['id'])
                elif attrs:
                    elements = soup.find_all(tag, attrs)
                else:
                    elements = soup.find_all(tag)
                
                self.logger.debug(f"見つかった要素数: {len(elements)}")
                
                for element in elements:
                    content_text = element.get_text(strip=True)
                    content_length = len(content_text)
                    
                    if content_length > 50:
                        if self.is_likely_novel_content(content_text):
                            self.logger.debug(f"本文取得成功: {content_length}文字")
                            return self.preserve_original_formatting(element)
                        else:
                            self.logger.debug(f"本文候補だが内容が適切でない: {content_length}文字")
                    else:
                        self.logger.debug(f"要素が短すぎます: {content_length}文字")
                        
            except Exception as e:
                self.logger.error(f"セレクター試行エラー: {e}")
        
        self.logger.warning("本文取得失敗: 適切な要素が見つかりませんでした")
        
        self.investigate_content_structure(soup)
        
        self.logger.debug("最後の手段：最も長いテキスト要素を検索")
        longest_element = None
        longest_length = 0
        
        for div in soup.find_all('div'):
            content_text = div.get_text(strip=True)
            if len(content_text) > longest_length and len(content_text) > 100:
                if not any(keyword in content_text for keyword in ['ナビゲーション', 'メニュー', 'ヘッダー', 'フッター']):
                    longest_element = div
                    longest_length = len(content_text)
        
        if longest_element:
            self.logger.debug(f"最長テキスト要素を使用: {longest_length}文字")
            return self.preserve_original_formatting(longest_element)
        
        return ""
    
    def preserve_original_formatting(self, element):
        """元のHTML構造を保持して見た目を完全再現"""
        html_content = str(element)
        
        html_content = re.sub(r'\s*on\w+\s*=\s*["\'][^"\'>]*["\']', '', html_content)
        html_content = re.sub(r'\s*data-track\w*\s*=\s*["\'][^"\'>]*["\']', '', html_content)
        
        self.logger.debug(f"元のフォーマットを保持: {len(html_content)}バイト")
        return html_content
    
    def is_likely_novel_content(self, text):
        """テキストが小説の本文らしいかチェック"""
        if len(text) < 30:
            return False
        
        exclusion_keywords = [
            'ナビゲーション', 'メニュー', 'ヘッダー', 'フッター',
            'サイドバー', '広告', 'アドバタイズ', 'コメント',
            'ランキング', 'お知らせ', '利用規約', '検索',
            'ログイン', 'マイページ', 'ブックマーク',
            'タグ一覧', 'カテゴリ', 'プロフィール',
            'Twitter', 'Facebook', 'シェア', 'ブックマーク'
        ]
        
        novel_indicators = [
            '。', '、', 'だった', 'である', 'していた',
            'という', 'ところ', 'それは', 'そして', 'しかし',
            'だが', 'しかし', 'ところが', 'けれど', 'なので'
        ]
        
        indicator_count = sum(1 for indicator in novel_indicators if indicator in text)
        
        if any(keyword in text for keyword in exclusion_keywords):
            self.logger.debug("除外キーワードが含まれているため除外")
            return False
        
        if ('総合評価：' in text or '評価：' in text or '連載：' in text or 
            '更新日時：' in text or '小説情報' in text or 'href="//syosetu.org/' in str(text)):
            self.logger.debug("ハーメルン特有の作品説明文として除外")
            return False
        
        self.logger.debug(f"小説コンテンツとして認識: {indicator_count}個の指標を確認")
        return indicator_count >= 3
    
    def investigate_content_structure(self, soup):
        """本文構造を詳細調査"""
        self.logger.debug("=== 本文構造詳細調査 ===")
        
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
        
        text_elements.sort(key=lambda x: x['length'], reverse=True)
        
        self.logger.debug(f"テキスト要素上位5件:")
        for i, elem in enumerate(text_elements[:5]):
            self.logger.debug(f"  [{i+1}] {elem['tag']} class={elem['class']} id={elem['id']} length={elem['length']}")
            self.logger.debug(f"      preview: {elem['preview']}")
        
        all_classes = set()
        for div in soup.find_all('div', class_=True):
            all_classes.update(div.get('class', []))
        
        content_related_classes = [cls for cls in all_classes 
                                 if any(keyword in cls.lower() 
                                       for keyword in ['text', 'content', 'body', 'story', 'novel', 'chapter', 'section'])]
        
        self.logger.debug(f"本文関連クラス名候補: {sorted(content_related_classes)}")
