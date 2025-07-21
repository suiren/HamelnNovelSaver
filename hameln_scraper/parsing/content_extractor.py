"""
コンテンツ抽出モジュール - ハーメルン2024年対応完全版
"""

import logging
import re
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any


class ContentExtractor:
    """コンテンツ抽出クラス - ハーメルン2024年対応完全版"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 2024年ハーメルン特有の本文セレクター（元ファイルから移植）
        self.content_selectors = [
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
    
    def extract_chapter_content(self, soup: BeautifulSoup, url: str) -> str:
        """
        章のコンテンツを抽出（2024年版ハーメルン完全対応）
        
        Args:
            soup: BeautifulSoupオブジェクト
            url: ページURL
            
        Returns:
            str: 抽出されたコンテンツ
        """
        self.logger.debug(f"本文抽出開始: {url}")
        
        for tag, attrs in self.content_selectors:
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
                    
                    # より詳細な条件チェック
                    if content_length > 50:  # 基準を緩和（短い章にも対応）
                        # 本文らしい内容かチェック
                        if self.is_likely_novel_content(content_text):
                            self.logger.debug(f"本文取得成功: {content_length}文字")
                            # テキストを正規化して返す（空白とタブ、改行を一つのスペースに統一）
                            normalized_text = re.sub(r'\s+', ' ', content_text.strip())
                            return normalized_text
                        else:
                            self.logger.debug(f"本文候補だが内容が適切でない: {content_length}文字")
                    else:
                        self.logger.debug(f"要素が短すぎます: {content_length}文字")
                        
            except Exception as e:
                self.logger.error(f"セレクター試行エラー: {e}")
        
        self.logger.warning("本文取得失敗: 適切な要素が見つかりませんでした")
        
        # 最後の手段：最も長いテキストを含む要素を選択
        self.logger.debug("最後の手段：最も長いテキスト要素を検索")
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
            self.logger.debug(f"最長テキスト要素を使用: {longest_length}文字")
            normalized_text = re.sub(r'\s+', ' ', longest_element.get_text(strip=True))
            return normalized_text
        
        return ""
    
    def is_likely_novel_content(self, text: str) -> bool:
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
                self.logger.debug(f"除外キーワード検出: {keyword}")
                return False
        
        # 小説らしい要素をチェック（より柔軟に）
        novel_indicators = [
            '。', '「', '」', 'だ', 'である', 'です', 'ます',
            'した', 'する', 'その', 'この', 'あの', 'が', 'を', 'に', 'は', 'で'
        ]
        
        indicator_count = sum(1 for indicator in novel_indicators if indicator in text)
        if indicator_count < 2:  # 緩和された基準
            self.logger.debug(f"小説らしい要素が少ない: {indicator_count}/{len(novel_indicators)}")
            return False
        
        return True
    
    def extract_novel_info(self, soup: BeautifulSoup) -> Dict[str, str]:
        """小説の基本情報を抽出（2024年版ハーメルン対応）"""
        info = {}
        
        self.logger.debug("小説情報抽出開始")
        
        # タイトル抽出（優先順序を調整）
        title_selectors = [
            # 最優先：2024年ハーメルン用（クラス付きh1を優先）
            ('h1', {'class': 'p-novel-title'}),
            ('h1', {'class': 'novel-title'}),
            ('div', {'class': 'p-novel-title'}),
            ('span', {'class': 'novel-title'}),
            # 従来のセレクター
            ('h1', {'class': 'title'}),
            ('h1', {'class': 'novel_title'}),
            ('div', {'class': 'novel_title'}),
            # titleタグ
            ('title', {}),
            # ★ Gemini発見：ハーメルンの数字クラス構造（最後の手段）
            ('div', {'class': 'section1'}),  # タイトルセクション候補
            ('div', {'class': 'section2'}),  # タイトルセクション候補
            ('h1', {'class': lambda x: x and any(cls.startswith('section') for cls in x if isinstance(cls, str))}),
            # フォールバック：クラスなしh1タグ（最後の手段）
            ('h1', {})
        ]
        
        self.logger.debug("タイトル抽出試行中...")
        for tag, attrs in title_selectors:
            self.logger.debug(f"タイトルセレクター試行: {tag} {attrs}")
            title_elem = soup.find(tag, attrs) if attrs else soup.find(tag)
            if title_elem:
                title_text = title_elem.get_text(strip=True)
                # ハーメルンの場合、タイトルから余分な文字を除去
                if ' - ハーメルン' in title_text:
                    title_text = title_text.replace(' - ハーメルン', '')
                if title_text and title_text not in ['Unknown Title', '']:
                    info['title'] = title_text
                    self.logger.debug(f"タイトル取得成功: {title_text}")
                    break
            else:
                self.logger.debug(f"セレクター {tag} {attrs} で要素が見つかりませんでした")
        
        # 作者抽出（幅広いセレクター）
        author_selectors = [
            # 2024年ハーメルン用
            ('a', {'class': 'p-novel-author'}),
            ('span', {'class': 'p-novel-author'}),
            ('div', {'class': 'novel-author'}),
            ('a', {'class': 'author-link'}),
            # 従来のセレクター
            ('a', {'href': lambda x: x and '/user/' in x}),
            ('span', {'class': 'author'}),
            ('div', {'class': 'author'}),
            ('a', {'class': 'user'}),
            ('span', {'class': 'user'})
        ]
        
        self.logger.debug("作者抽出試行中...")
        for tag, attrs in author_selectors:
            author_elem = soup.find(tag, attrs)
            if author_elem:
                author_text = author_elem.get_text(strip=True)
                if author_text and author_text not in ['Unknown Author', '']:
                    info['author'] = author_text
                    self.logger.debug(f"作者取得成功: {author_text}")
                    break
        
        # デフォルト値設定
        if 'title' not in info:
            info['title'] = "不明なタイトル"
        if 'author' not in info:
            info['author'] = "不明な作者"
        
        return info