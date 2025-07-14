#!/usr/bin/env python3
"""
ハーメルン小説保存ツール - 包括的テスト
章ページ抽出 + 章リンク抽出のテスト
"""

import cloudscraper
from bs4 import BeautifulSoup
import re
import sys
import os

# 現在のディレクトリをパスに追加（インポート用）
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_chapter_extraction():
    """章ページから本文を抽出"""
    # 章ページのURL
    chapter_url = "https://syosetu.org/novel/378070/2.html"
    
    # CloudScraperで取得
    scraper = cloudscraper.create_scraper()
    response = scraper.get(chapter_url)
    
    print(f"ステータス: {response.status_code}")
    print(f"Content-Encoding: {response.headers.get('content-encoding', 'なし')}")
    
    # BeautifulSoupでパース（response.textを使用してCloudScraperの自動解凍を利用）
    soup = BeautifulSoup(response.text, 'html.parser')
    
    print(f"タイトル: {soup.title.string if soup.title else 'なし'}")
    
    # honbun要素を検索
    honbun = soup.find('div', id='honbun')
    if honbun:
        print(f"\n=== div[id='honbun'] 発見！ ===")
        
        # p要素を取得
        paragraphs = honbun.find_all('p')
        print(f"段落数: {len(paragraphs)}個")
        
        # 最初の10段落を表示
        for i, p in enumerate(paragraphs[:10]):
            text = p.get_text(strip=True)
            if text:  # 空でない段落のみ
                print(f"p[{i}] ({p.get('id', 'no-id')}): {text[:100]}...")
        
        # 本文全体の文字数
        full_text = honbun.get_text()
        print(f"\n本文全体: {len(full_text)}文字")
        
        return True
    else:
        print("div[id='honbun'] が見つかりません")
        
        # 代替検索
        print("\n=== 代替検索 ===")
        main_div = soup.find('div', id='maind')
        if main_div:
            print("div[id='maind'] を発見")
            ss_divs = main_div.find_all('div', class_='ss')
            print(f"div.ss: {len(ss_divs)}個")
            
            # 各div.ssの内容を確認
            for i, div in enumerate(ss_divs):
                text = div.get_text(strip=True)
                print(f"ss[{i}]: {len(text)}文字 - {text[:100]}...")
        
        return False

if __name__ == "__main__":
    test_chapter_extraction()