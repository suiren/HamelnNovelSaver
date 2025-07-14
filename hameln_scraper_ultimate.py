#!/usr/bin/env python3
"""
ハーメルン小説保存アプリケーション - 最終版
CloudScraper + undetected-chromedriver を使用
"""

import time
import os
import re
from typing import Dict, List, Optional
import cloudscraper
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from urllib.parse import urljoin, urlparse

class HamelnUltimateScraper:
    def __init__(self, base_url: str = "https://syosetu.org"):
        self.base_url = base_url
        self.driver = None
        self.cloudscraper = None
        self.setup_scrapers()
        
    def setup_scrapers(self):
        """スクレイパーを設定"""
        try:
            # CloudScraper設定
            self.cloudscraper = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'desktop': True
                }
            )
            print("CloudScraper設定完了")
            
            # undetected-chromedriver設定
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-plugins')
            chrome_options.add_argument('--disable-images')
            chrome_options.add_argument('--disable-javascript')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            self.driver = uc.Chrome(options=chrome_options, version_main=None)
            print("undetected-chromedriver設定完了")
            
        except Exception as e:
            print(f"スクレイパー設定エラー: {e}")
            
    def get_page_cloudscraper(self, url: str) -> Optional[BeautifulSoup]:
        """CloudScraperでページを取得"""
        try:
            print(f"CloudScraperでページ取得中: {url}")
            response = self.cloudscraper.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            print(f"CloudScraperでページ取得成功: {url}")
            return soup
            
        except Exception as e:
            print(f"CloudScraperでのページ取得エラー: {e}")
            return None
            
    def get_page_selenium(self, url: str) -> Optional[BeautifulSoup]:
        """Seleniumでページを取得"""
        try:
            print(f"Seleniumでページ取得中: {url}")
            
            if not self.driver:
                print("Seleniumドライバーが初期化されていません")
                return None
                
            self.driver.get(url)
            
            # Cloudflareの認証チェック待機
            WebDriverWait(self.driver, 10).until(
                lambda driver: "Cloudflare" not in driver.title
            )
            
            # ページの読み込み完了を待機
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            time.sleep(2)  # 追加の待機時間
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            print(f"Seleniumでページ取得成功: {url}")
            return soup
            
        except Exception as e:
            print(f"Seleniumでのページ取得エラー: {e}")
            return None
            
    def get_page(self, url: str) -> Optional[BeautifulSoup]:
        """ページを取得（CloudScraper → Selenium の順で試行）"""
        # まずCloudScraperを試す
        soup = self.get_page_cloudscraper(url)
        if soup and self.validate_page(soup):
            return soup
            
        print("CloudScraperが失敗、Seleniumで再試行...")
        
        # Seleniumで再試行
        soup = self.get_page_selenium(url)
        if soup and self.validate_page(soup):
            return soup
            
        print("両方の手法で失敗しました")
        return None
        
    def validate_page(self, soup: BeautifulSoup) -> bool:
        """ページが正常に取得できたかチェック"""
        if not soup:
            return False
            
        # Cloudflareの認証ページチェック
        if soup.find('title') and 'Cloudflare' in soup.find('title').get_text():
            return False
            
        # エラーページチェック
        if soup.find('title') and ('404' in soup.find('title').get_text() or 'Error' in soup.find('title').get_text()):
            return False
            
        # 基本的なHTML構造チェック
        if not soup.find('body'):
            return False
            
        return True
        
    def extract_novel_info(self, soup: BeautifulSoup) -> Dict:
        """小説の基本情報を抽出"""
        info = {}
        
        # デバッグ用: HTMLの一部を表示
        print(f"HTMLタイトル: {soup.title.string if soup.title else 'None'}")
        
        # タイトル抽出（複数のセレクターを試行）
        title_selectors = [
            ('h1', {'class': 'title'}),
            ('h1', {'class': 'novel_title'}),
            ('div', {'class': 'novel_title'}),
            ('h1', {}),
            ('title', {})
        ]
        
        for tag, attrs in title_selectors:
            title_elem = soup.find(tag, attrs) if attrs else soup.find(tag)
            if title_elem:
                title_text = title_elem.get_text(strip=True)
                # ハーメルンの場合、タイトルから余分な文字を除去
                if ' - ハーメルン' in title_text:
                    title_text = title_text.replace(' - ハーメルン', '')
                if title_text and title_text not in ['Unknown Title', '']:
                    info['title'] = title_text
                    print(f"抽出されたタイトル: {title_text}")
                    break
        
        # 作者抽出
        author_selectors = [
            ('a', {'href': lambda x: x and '/user/' in x}),
            ('div', {'class': 'author'}),
            ('span', {'class': 'author'}),
            ('a', {'class': 'author'})
        ]
        
        for tag, attrs in author_selectors:
            if callable(attrs.get('href')):
                author_elem = soup.find(tag, href=attrs['href'])
            else:
                author_elem = soup.find(tag, attrs)
            
            if author_elem:
                author_text = author_elem.get_text(strip=True)
                if author_text and author_text not in ['Unknown Author', '']:
                    info['author'] = author_text
                    print(f"抽出された作者: {author_text}")
                    break
        
        # あらすじ抽出
        synopsis_selectors = [
            ('div', {'class': 'novel_ex'}),
            ('div', {'class': 'synopsis'}),
            ('div', {'class': 'summary'}),
            ('div', {'class': 'description'})
        ]
        
        for tag, attrs in synopsis_selectors:
            synopsis_elem = soup.find(tag, attrs)
            if synopsis_elem:
                synopsis_text = synopsis_elem.get_text(strip=True)
                if synopsis_text:
                    info['synopsis'] = synopsis_text
                    print(f"あらすじ取得: {len(synopsis_text)}文字")
                    break
        
        # 情報が取得できない場合の詳細調査
        if not info.get('title') or not info.get('author'):
            print("タイトルまたは作者が取得できませんでした")
            print("利用可能なh1タグ:")
            for h1 in soup.find_all('h1')[:3]:
                print(f"  - {h1.get_text(strip=True)[:50]}...")
            print("利用可能なリンク:")
            for link in soup.find_all('a', href=True)[:5]:
                print(f"  - {link.get('href')}: {link.get_text(strip=True)[:30]}...")
        
        return info
        
    def get_chapter_links(self, soup: BeautifulSoup) -> List[str]:
        """章のリンクを抽出"""
        chapter_links = []
        
        # 章リンクの一般的なパターンを検索
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href and '/novel/' in href and href.count('/') >= 2:
                if href.startswith('http'):
                    full_url = href
                else:
                    full_url = urljoin(self.base_url, href)
                
                if full_url not in chapter_links:
                    chapter_links.append(full_url)
        
        return chapter_links
        
    def save_as_html(self, content: str, filename: str, output_dir: str = "saved_novels"):
        """コンテンツをHTMLファイルとして保存"""
        os.makedirs(output_dir, exist_ok=True)
        
        # ファイル名を安全にする
        safe_filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        if not safe_filename.endswith('.html'):
            safe_filename += '.html'
            
        filepath = os.path.join(output_dir, safe_filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"保存完了: {filepath}")
        return filepath
        
    def create_html_template(self, title: str, author: str, content: str) -> str:
        """HTMLテンプレートを作成"""
        return f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Helvetica Neue', Arial, 'Hiragino Kaku Gothic ProN', 'Hiragino Sans', Meiryo, sans-serif;
            line-height: 1.8;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #fafafa;
        }}
        .header {{
            border-bottom: 2px solid #ddd;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .title {{
            font-size: 2em;
            color: #333;
            margin-bottom: 10px;
        }}
        .author {{
            font-size: 1.2em;
            color: #666;
            margin-bottom: 10px;
        }}
        .content {{
            background-color: white;
            padding: 30px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .chapter {{
            margin-bottom: 40px;
        }}
        .chapter-title {{
            font-size: 1.5em;
            color: #444;
            border-left: 4px solid #007acc;
            padding-left: 15px;
            margin-bottom: 20px;
        }}
        p {{
            margin-bottom: 15px;
            text-indent: 1em;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1 class="title">{title}</h1>
        <div class="author">作者: {author}</div>
    </div>
    <div class="content">
        {content}
    </div>
</body>
</html>"""
        
    def scrape_novel(self, novel_url: str) -> Optional[str]:
        """小説全体をスクレイピングして保存"""
        print(f"小説を取得中: {novel_url}")
        
        # メインページを取得
        soup = self.get_page(novel_url)
        if not soup:
            print("メインページの取得に失敗しました")
            return None
            
        # 小説情報を抽出
        novel_info = self.extract_novel_info(soup)
        print(f"タイトル: {novel_info.get('title', 'Unknown')}")
        print(f"作者: {novel_info.get('author', 'Unknown')}")
        
        # 章リンクを取得
        chapter_links = self.get_chapter_links(soup)
        print(f"章数: {len(chapter_links)}")
        
        # 各章を取得
        all_content = []
        for i, chapter_url in enumerate(chapter_links, 1):
            print(f"章 {i}/{len(chapter_links)} を取得中...")
            chapter_soup = self.get_page(chapter_url)
            
            if chapter_soup:
                # 章のタイトルを抽出
                chapter_title = chapter_soup.find('h1')
                if chapter_title:
                    chapter_title_text = chapter_title.get_text(strip=True)
                else:
                    chapter_title_text = f"第{i}章"
                
                # 章の本文を抽出
                content_div = (chapter_soup.find('div', class_='novel_body') or 
                              chapter_soup.find('div', class_='novel_view') or
                              chapter_soup.find('div', class_='novel_content'))
                
                if content_div:
                    chapter_content = str(content_div)
                    all_content.append(f'<div class="chapter"><h2 class="chapter-title">{chapter_title_text}</h2>{chapter_content}</div>')
                
                # サーバーに負荷をかけないよう待機
                time.sleep(3)
        
        # HTMLを生成
        final_content = '\n'.join(all_content)
        html_content = self.create_html_template(
            novel_info.get('title', 'Unknown Title'),
            novel_info.get('author', 'Unknown Author'),
            final_content
        )
        
        # ファイルに保存
        filename = f"{novel_info.get('title', 'novel')}.html"
        saved_path = self.save_as_html(html_content, filename)
        
        print(f"小説の保存が完了しました: {saved_path}")
        return saved_path
        
    def close(self):
        """リソースを解放"""
        if self.driver:
            self.driver.quit()
            print("ブラウザを閉じました")

def main():
    """メイン関数"""
    scraper = None
    
    try:
        scraper = HamelnUltimateScraper()
        
        print("ハーメルン小説保存ツール（最終版）")
        print("=" * 40)
        
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
    finally:
        if scraper:
            scraper.close()

if __name__ == "__main__":
    main()