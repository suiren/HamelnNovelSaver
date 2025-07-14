#!/usr/bin/env python3
"""
ハーメルン小説保存アプリケーション - 高度版
DrissionPageを使用してCloudflareの高度な保護機能を突破
"""

import time
import os
import re
from typing import Dict, List, Optional
from DrissionPage import ChromiumPage
from bs4 import BeautifulSoup

class HamelnAdvancedScraper:
    def __init__(self, base_url: str = "https://syosetu.org"):
        self.base_url = base_url
        self.page = None
        self.setup_browser()
        
    def setup_browser(self):
        """ブラウザを設定"""
        try:
            # DrissionPageのChromiumPageを設定
            self.page = ChromiumPage()
            
            # ブラウザオプション設定
            self.page.set.window_size(1920, 1080)
            self.page.set.user_agent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            print("ブラウザ設定完了")
            
        except Exception as e:
            print(f"ブラウザ設定エラー: {e}")
            self.page = None
            
    def get_page(self, url: str, retry_count: int = 3) -> Optional[BeautifulSoup]:
        """指定されたURLのページを取得"""
        if not self.page:
            print("ブラウザが初期化されていません")
            return None
            
        for attempt in range(retry_count):
            try:
                print(f"ページ取得中: {url} (試行 {attempt + 1}/{retry_count})")
                
                # ページにアクセス
                self.page.get(url)
                
                # Cloudflareの認証チェック待機
                time.sleep(3)
                
                # 認証チェック中かどうか確認
                if self.page.title and 'Cloudflare' in self.page.title:
                    print("Cloudflareの認証チェック中...")
                    # 最大30秒待機
                    for i in range(30):
                        time.sleep(1)
                        if 'Cloudflare' not in self.page.title:
                            break
                        if i == 29:
                            print("Cloudflareの認証チェックがタイムアウトしました")
                            if attempt < retry_count - 1:
                                continue
                            else:
                                return None
                
                # ページが正常に読み込まれたかチェック
                if not self.page.html:
                    print("ページの読み込みに失敗しました")
                    if attempt < retry_count - 1:
                        time.sleep(5)
                        continue
                    else:
                        return None
                
                # HTMLをBeautifulSoupで解析
                soup = BeautifulSoup(self.page.html, 'html.parser')
                
                # エラーページでないかチェック
                if soup.find('title') and ('404' in soup.find('title').get_text() or 'Error' in soup.find('title').get_text()):
                    print("エラーページが返されました")
                    return None
                
                print(f"ページ取得成功: {url}")
                return soup
                
            except Exception as e:
                print(f"ページ取得エラー (試行 {attempt + 1}/{retry_count}): {e}")
                if attempt < retry_count - 1:
                    time.sleep(5 + (attempt * 2))
                else:
                    return None
                    
        return None
        
    def extract_novel_info(self, soup: BeautifulSoup) -> Dict:
        """小説の基本情報を抽出"""
        info = {}
        
        # タイトル
        title_elem = soup.find('h1') or soup.find('title')
        if title_elem:
            info['title'] = title_elem.get_text(strip=True)
        
        # 作者
        author_elem = soup.find('a', href=lambda x: x and '/user/' in x)
        if author_elem:
            info['author'] = author_elem.get_text(strip=True)
        
        # あらすじ
        synopsis_elem = soup.find('div', class_='novel_ex')
        if synopsis_elem:
            info['synopsis'] = synopsis_elem.get_text(strip=True)
        
        return info
        
    def get_chapter_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """章のリンクを抽出"""
        chapter_links = []
        
        # 章リンクの一般的なパターンを検索
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href and '/novel/' in href and href.count('/') >= 2:
                if href.startswith('http'):
                    full_url = href
                else:
                    full_url = base_url + href if not href.startswith('/') else base_url + href
                
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
        chapter_links = self.get_chapter_links(soup, self.base_url)
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
                time.sleep(2)
        
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
        """ブラウザを閉じる"""
        if self.page:
            self.page.quit()
            print("ブラウザを閉じました")

def main():
    """メイン関数"""
    scraper = None
    
    try:
        scraper = HamelnAdvancedScraper()
        
        print("ハーメルン小説保存ツール（高度版）")
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