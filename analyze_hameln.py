#!/usr/bin/env python3
"""
ハーメルンページ構造の詳細分析スクリプト
"""

import requests
import cloudscraper
from bs4 import BeautifulSoup
import brotli
import re

def analyze_hameln_page(url):
    """ハーメルンページの構造を詳細分析"""
    print(f"ページ分析開始: {url}")
    
    # CloudScraperで取得
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url)
    
    print(f"ステータス: {response.status_code}")
    print(f"レスポンスサイズ: {len(response.content)} bytes")
    print(f"Content-Encoding: {response.headers.get('content-encoding', 'なし')}")
    
    # Brotli解凍処理
    content = response.content
    encoding = response.headers.get('content-encoding', '').lower()
    
    if encoding == 'br':
        try:
            content = brotli.decompress(content)
            print("Brotli解凍成功")
        except Exception as e:
            print(f"Brotli解凍失敗: {e}")
    
    soup = BeautifulSoup(content, 'html.parser')
    
    print("\n=== ページ構造分析 ===")
    
    # タイトル情報
    title = soup.title.string if soup.title else "タイトルなし"
    print(f"ページタイトル: {title}")
    
    # 基本統計
    print(f"div要素数: {len(soup.find_all('div'))}")
    print(f"p要素数: {len(soup.find_all('p'))}")
    print(f"span要素数: {len(soup.find_all('span'))}")
    
    # 本文要素の詳細分析
    print("\n=== 本文要素の分析 ===")
    
    # 一般的な本文クラスの検索
    text_classes = [
        'novel_view', 'novel_body', 'novel-view', 'novel-body',
        'text_body', 'text-body', 'content_body', 'content-body',
        'main_text', 'main-text', 'story_text', 'story-text',
        'section1', 'section2', 'section3', 'section4', 'section5',
        'section6', 'section7', 'section8', 'section9',
        'p-novel-text', 'novel-text'
    ]
    
    for class_name in text_classes:
        elements = soup.find_all(class_=class_name)
        if elements:
            print(f"クラス '{class_name}': {len(elements)}個の要素")
            for i, elem in enumerate(elements[:3]):  # 最初の3個だけ表示
                text = elem.get_text(strip=True)[:200]
                print(f"  {i+1}: {text}...")
    
    # ID属性での検索
    print("\n=== ID属性の分析 ===")
    id_patterns = ['novel', 'text', 'content', 'main', 'body', 'story']
    for pattern in id_patterns:
        elements = soup.find_all(id=re.compile(pattern, re.I))
        if elements:
            print(f"ID '{pattern}' パターン: {len(elements)}個")
            for elem in elements:
                print(f"  ID: {elem.get('id')}, タグ: {elem.name}")
    
    # すべてのp要素を確認（本文の可能性）
    print("\n=== p要素の内容分析 ===")
    p_elements = soup.find_all('p')
    long_paragraphs = []
    
    for i, p in enumerate(p_elements):
        text = p.get_text(strip=True)
        if len(text) > 50:  # 50文字以上の段落
            long_paragraphs.append((i, text[:100], len(text)))
    
    print(f"50文字以上の段落: {len(long_paragraphs)}個")
    for i, (idx, text, length) in enumerate(long_paragraphs[:5]):
        print(f"  {i+1}. p[{idx}] ({length}文字): {text}...")
    
    # div要素の詳細分析
    print("\n=== div要素のクラス分析 ===")
    div_classes = {}
    for div in soup.find_all('div'):
        classes = div.get('class', [])
        if classes:
            class_str = ' '.join(classes)
            if class_str not in div_classes:
                div_classes[class_str] = 0
            div_classes[class_str] += 1
    
    # 頻度順でソート
    sorted_classes = sorted(div_classes.items(), key=lambda x: x[1], reverse=True)
    print("頻出divクラス:")
    for class_name, count in sorted_classes[:10]:
        print(f"  {class_name}: {count}個")
    
    # HTMLの先頭部分を保存（デバッグ用）
    with open('hameln_page_debug.html', 'w', encoding='utf-8') as f:
        f.write(str(soup))
    print("\n完全なHTMLを hameln_page_debug.html に保存しました")
    
    return soup

if __name__ == "__main__":
    url = "https://syosetu.org/novel/378070/2.html"
    soup = analyze_hameln_page(url)