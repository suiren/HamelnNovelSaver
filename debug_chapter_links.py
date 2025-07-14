#!/usr/bin/env python3
"""
章リンク抽出の詳細デバッグ
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hameln_scraper_final import HamelnFinalScraper
import re

def debug_chapter_links():
    """章リンク抽出の詳細デバッグ"""
    index_url = "https://syosetu.org/novel/378070/"
    
    print(f"=== 章リンク抽出詳細デバッグ ===")
    print(f"目次URL: {index_url}")
    
    scraper = HamelnFinalScraper()
    
    try:
        # 目次ページを取得
        soup = scraper.get_page(index_url)
        if not soup:
            print("✗ 目次ページの取得に失敗")
            return False
        
        print("✓ 目次ページの取得成功")
        
        # 全てのaタグとhref属性を詳細調査
        print("\n=== 全aタグのhref属性詳細調査 ===")
        all_links = soup.find_all('a', href=True)
        print(f"総aタグ数: {len(all_links)}")
        
        # 特定パターンでのリンク検索
        patterns_to_check = [
            r'/novel/378070/\d+\.html',  # /novel/378070/1.html 形式
            r'/novel/378070/\d+',        # /novel/378070/1 形式
            r'378070/\d+\.html',         # 378070/1.html 形式
            r'378070/\d+',               # 378070/1 形式
        ]
        
        found_patterns = {}
        for pattern in patterns_to_check:
            found_patterns[pattern] = []
        
        for i, link in enumerate(all_links):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # 各パターンをチェック
            for pattern in patterns_to_check:
                if re.search(pattern, href):
                    found_patterns[pattern].append({
                        'index': i,
                        'href': href,
                        'text': text[:50],
                        'full_href': href if href.startswith('http') else f"https://syosetu.org{href}"
                    })
        
        # パターン別結果表示
        for pattern, matches in found_patterns.items():
            print(f"\nパターン '{pattern}': {len(matches)}件")
            for match in matches[:5]:  # 最初の5件のみ表示
                print(f"  [{match['index']}] {match['text']}... -> {match['href']}")
                print(f"      完全URL: {match['full_href']}")
        
        # 数字を含むリンクをすべて調査
        print(f"\n=== 数字を含む全リンク調査 ===")
        numeric_links = []
        for i, link in enumerate(all_links):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # 数字を含むhrefを検索
            if re.search(r'\d', href):
                numeric_links.append({
                    'index': i,
                    'href': href,
                    'text': text[:30]
                })
        
        print(f"数字を含むリンク総数: {len(numeric_links)}")
        for link in numeric_links[:10]:  # 最初の10件
            print(f"  [{link['index']}] {link['text']}... -> {link['href']}")
        
        # 特定の文字列を含むリンクを検索
        search_terms = ['第', '話', 'chapter', 'episode', '1', '2', '3']
        print(f"\n=== 特定文字列を含むリンク検索 ===")
        
        for term in search_terms:
            matches = []
            for i, link in enumerate(all_links):
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                if term in text.lower() or term in href.lower():
                    matches.append({
                        'index': i,
                        'href': href,
                        'text': text[:30]
                    })
            
            print(f"'{term}'を含むリンク: {len(matches)}件")
            for match in matches[:3]:  # 最初の3件
                print(f"  [{match['index']}] {match['text']}... -> {match['href']}")
        
        # HTMLの生データからパターンマッチング検索
        print(f"\n=== HTML生データからのパターン検索 ===")
        html_content = str(soup)
        
        # 章リンクらしきパターンを検索
        chapter_patterns = [
            r'href="[^"]*378070/\d+\.html[^"]*"',
            r'href="[^"]*378070/\d+[^"]*"',
            r'/novel/378070/\d+\.html',
            r'第\d+話',
            r'chapter\s*\d+',
            r'episode\s*\d+',
        ]
        
        for pattern in chapter_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            print(f"パターン '{pattern}': {len(matches)}件")
            for match in matches[:3]:
                print(f"  {match}")
        
        return True
            
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        scraper.close()

if __name__ == "__main__":
    debug_chapter_links()