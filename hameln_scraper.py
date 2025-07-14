#!/usr/bin/env python3
"""
ハーメルン小説保存アプリケーション
特定の小説サイトのページを保存するスクレイピングツール
"""

import requests
from bs4 import BeautifulSoup
import os
import time
import json
import re
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Optional

class HamelnScraper:
    def __init__(self, base_url: str = "https://syosetu.org"):
        self.base_url = base_url
        self.session = requests.Session()
        
        # より詳細なヘッダー設定でbot検知を回避
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        })
        
        # Cookieを有効にする
        self.session.cookies.set('__cfduid', 'test', domain='syosetu.org')
        
    def get_page(self, url: str, retry_count: int = 5) -> Optional[BeautifulSoup]:
        """指定されたURLのページを取得"""
        for attempt in range(retry_count):
            try:
                # リファラーを設定（前のページから遷移したように見せる）
                if attempt > 0:
                    self.session.headers.update({
                        'Referer': self.base_url
                    })
                
                # より長い待機時間とタイムアウト設定
                response = self.session.get(url, timeout=45, allow_redirects=True)
                
                # ステータスコードを詳細チェック
                if response.status_code == 403:
                    print(f"アクセス拒否 (403): サイトのbot対策により拒否されました")
                    if attempt < retry_count - 1:
                        print(f"待機後に再試行します... (試行 {attempt + 1}/{retry_count})")
                        time.sleep(10 + (attempt * 5))  # 段階的に待機時間を増やす
                        continue
                    else:
                        return None
                elif response.status_code == 429:
                    print(f"レート制限 (429): アクセス頻度が高すぎます")
                    if attempt < retry_count - 1:
                        print(f"待機後に再試行します... (試行 {attempt + 1}/{retry_count})")
                        time.sleep(30 + (attempt * 10))
                        continue
                    else:
                        return None
                elif response.status_code == 503:
                    print(f"サービス一時停止 (503): サーバーメンテナンス中の可能性があります")
                    if attempt < retry_count - 1:
                        print(f"待機後に再試行します... (試行 {attempt + 1}/{retry_count})")
                        time.sleep(60)
                        continue
                    else:
                        return None
                
                response.raise_for_status()
                
                # レスポンスが空でないことを確認
                if not response.content:
                    print(f"空のレスポンスを受信しました")
                    if attempt < retry_count - 1:
                        time.sleep(3 + attempt)
                        continue
                    else:
                        return None
                
                # HTMLパース
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Cloudflareの認証ページかどうかチェック
                if soup.find('title') and 'Cloudflare' in soup.find('title').get_text():
                    print(f"Cloudflareの認証ページが表示されました")
                    if attempt < retry_count - 1:
                        print(f"待機後に再試行します... (試行 {attempt + 1}/{retry_count})")
                        time.sleep(20 + (attempt * 5))
                        continue
                    else:
                        return None
                
                print(f"ページ取得成功: {url}")
                return soup
                
            except requests.exceptions.Timeout:
                print(f"タイムアウト (試行 {attempt + 1}/{retry_count}): {url}")
                if attempt < retry_count - 1:
                    time.sleep(5 + (attempt * 2))
                else:
                    print("タイムアウトにより取得に失敗しました")
                    return None
            except requests.exceptions.ConnectionError:
                print(f"接続エラー (試行 {attempt + 1}/{retry_count}): ネットワーク接続を確認してください")
                if attempt < retry_count - 1:
                    time.sleep(10 + (attempt * 3))
                else:
                    return None
            except requests.exceptions.RequestException as e:
                print(f"リクエストエラー (試行 {attempt + 1}/{retry_count}): {e}")
                if attempt < retry_count - 1:
                    time.sleep(3 + (attempt * 2))
                else:
                    return None
            except Exception as e:
                print(f"予期しないエラー (試行 {attempt + 1}/{retry_count}): {e}")
                if attempt < retry_count - 1:
                    time.sleep(5)
                else:
                    return None
                    
    def extract_novel_info(self, soup: BeautifulSoup) -> Dict:
        """小説の基本情報を抽出"""
        info = {}
        
        # デバッグ用: HTMLの一部を表示
        print(f"HTMLタイトル: {soup.title.string if soup.title else 'None'}")
        
        # タイトル - より具体的なセレクター
        title_elem = (soup.find('h1', class_='title') or 
                     soup.find('h1', class_='novel_title') or
                     soup.find('div', class_='novel_title') or
                     soup.find('h1') or 
                     soup.find('title'))
        
        if title_elem:
            title_text = title_elem.get_text(strip=True)
            # ハーメルンの場合、タイトルから余分な文字を除去
            if ' - ハーメルン' in title_text:
                title_text = title_text.replace(' - ハーメルン', '')
            info['title'] = title_text
            print(f"抽出されたタイトル: {title_text}")
        
        # 作者 - より具体的なセレクター
        author_elem = (soup.find('a', href=lambda x: x and '/user/' in x) or
                      soup.find('div', class_='author') or
                      soup.find('span', class_='author'))
        
        if author_elem:
            author_text = author_elem.get_text(strip=True)
            info['author'] = author_text
            print(f"抽出された作者: {author_text}")
        
        # あらすじ - より具体的なセレクター
        synopsis_elem = (soup.find('div', class_='novel_ex') or
                        soup.find('div', class_='synopsis') or
                        soup.find('div', class_='summary'))
        
        if synopsis_elem:
            synopsis_text = synopsis_elem.get_text(strip=True)
            info['synopsis'] = synopsis_text
            print(f"あらすじ取得: {len(synopsis_text)}文字")
        
        # 情報が取得できない場合の詳細調査
        if not info.get('title') or not info.get('author'):
            print("タイトルまたは作者が取得できませんでした")
            print("利用可能なh1タグ:")
            for h1 in soup.find_all('h1'):
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
                content_div = chapter_soup.find('div', class_='novel_body') or chapter_soup.find('div', class_='novel_view')
                if content_div:
                    chapter_content = str(content_div)
                    all_content.append(f'<div class="chapter"><h2 class="chapter-title">{chapter_title_text}</h2>{chapter_content}</div>')
                
                # サーバーに負荷をかけないよう待機
                time.sleep(1)
        
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

def main():
    """メイン関数"""
    scraper = HamelnScraper()
    
    # 使用例
    print("ハーメルン小説保存ツール")
    print("=" * 40)
    
    novel_url = input("小説のURLを入力してください: ").strip()
    
    if not novel_url:
        print("URLが入力されていません。")
        return
    
    try:
        result = scraper.scrape_novel(novel_url)
        if result:
            print(f"\n✓ 保存完了: {result}")
        else:
            print("\n✗ 保存に失敗しました。")
    except KeyboardInterrupt:
        print("\n\n処理が中断されました。")
    except Exception as e:
        print(f"\nエラーが発生しました: {e}")

if __name__ == "__main__":
    main()