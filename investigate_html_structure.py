#!/usr/bin/env python3
"""
ハーメルンのHTML構造調査
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hameln_scraper.core.scraper import HamelnScraper as HamelnFinalScraper
import re

def investigate_html_structure():
    """ハーメルンのHTML構造を詳細調査"""
    # 目次ページのURL
    index_url = "https://syosetu.org/novel/378070/"
    
    print(f"=== ハーメルンHTML構造調査 ===")
    print(f"目次URL: {index_url}")
    
    # スクレイパーを初期化
    scraper = HamelnFinalScraper()
    
    try:
        # 目次ページを取得
        soup = scraper.get_page(index_url)
        if not soup:
            print("✗ 目次ページの取得に失敗")
            return False
        
        print("✓ 目次ページの取得成功")
        
        # 全てのaタグとそのhref属性を調査
        print("\n=== 全aタグ調査 ===")
        all_links = soup.find_all('a', href=True)
        print(f"総aタグ数: {len(all_links)}")
        
        # 小説に関連するリンクを特定
        novel_links = []
        for i, link in enumerate(all_links):
            href = link.get('href')
            text = link.get_text(strip=True)
            
            # 378070を含むリンクを特別に表示
            if '378070' in href:
                print(f"★ 作品関連リンク [{i}]: {text[:50]}... -> {href}")
                novel_links.append((text, href))
            # 他の小説リンクも参考として
            elif '/novel/' in href and href.count('/') >= 4:
                print(f"  他作品リンク [{i}]: {text[:30]}... -> {href}")
        
        print(f"\n対象作品のリンク数: {len(novel_links)}")
        
        # 章番号パターンを調査
        print("\n=== 章番号パターン調査 ===")
        chapter_pattern = re.compile(r'/novel/378070/(\d+)\.html')
        chapters_found = {}
        
        for text, href in novel_links:
            match = chapter_pattern.search(href)
            if match:
                chapter_num = int(match.group(1))
                chapters_found[chapter_num] = {
                    'url': href,
                    'title': text,
                    'full_url': f"https://syosetu.org{href}" if href.startswith('/') else href
                }
                print(f"第{chapter_num}話: {text[:40]}...")
        
        print(f"\n発見された章数: {len(chapters_found)}")
        if chapters_found:
            sorted_chapters = sorted(chapters_found.keys())
            print(f"章番号範囲: {sorted_chapters[0]} - {sorted_chapters[-1]}")
            
            # 最初の数話を詳細表示
            for num in sorted_chapters[:5]:
                chapter = chapters_found[num]
                print(f"  第{num}話: {chapter['title'][:40]}... -> {chapter['full_url']}")
        
        # div要素の調査
        print("\n=== div要素構造調査 ===")
        
        # よくある章リスト用のクラス名を調査
        potential_containers = [
            'chapter_list', 'episode_list', 'novel_sublist', 'index_box',
            'novel_index', 'chapter_index', 'episode_index', 'story_list'
        ]
        
        for class_name in potential_containers:
            divs = soup.find_all('div', class_=class_name)
            if divs:
                print(f"✓ div.{class_name}: {len(divs)}個発見")
                for i, div in enumerate(divs[:2]):  # 最初の2個のみ
                    links_in_div = div.find_all('a', href=True)
                    print(f"  div[{i}]内のリンク数: {len(links_in_div)}")
        
        # ul/ol要素の調査
        print("\n=== ul/ol要素調査 ===")
        for tag_name in ['ul', 'ol']:
            lists = soup.find_all(tag_name)
            print(f"{tag_name}要素数: {len(lists)}")
            for i, list_elem in enumerate(lists[:3]):  # 最初の3個のみ
                class_attr = list_elem.get('class', [])
                links_in_list = list_elem.find_all('a', href=True)
                if links_in_list:
                    print(f"  {tag_name}[{i}] (class={class_attr}): {len(links_in_list)}個のリンク")
                    # 378070を含むリンクがあるかチェック
                    relevant_links = [a for a in links_in_list if '378070' in a.get('href', '')]
                    if relevant_links:
                        print(f"    -> 関連リンク{len(relevant_links)}個発見！")
        
        return True
            
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        scraper.close()

if __name__ == "__main__":
    investigate_html_structure()
