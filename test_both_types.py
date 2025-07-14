#!/usr/bin/env python3
"""
単話作品と複数話作品の両方をテスト
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hameln_scraper_final import HamelnFinalScraper

def test_single_chapter_work():
    """単話作品のテスト（378070）"""
    print("=== 単話作品テスト ===")
    index_url = "https://syosetu.org/novel/378070/"
    
    scraper = HamelnFinalScraper()
    
    try:
        # 単話作品として処理されるかテスト
        print(f"URL: {index_url}")
        
        # ページを取得
        soup = scraper.get_page(index_url)
        if not soup:
            print("✗ ページ取得失敗")
            return False
        
        # 章リンクを取得
        chapter_links = scraper.get_chapter_links(soup, index_url)
        print(f"発見された章数: {len(chapter_links)}")
        
        # 本文を抽出（単話作品の場合、目次ページに本文があるはず）
        chapter_content = scraper.extract_chapter_content(soup, index_url)
        if chapter_content:
            print(f"✓ 単話本文取得成功: {len(chapter_content)}文字")
            print(f"本文冒頭: {chapter_content[:100]}...")
            return True
        else:
            print("✗ 単話本文取得失敗")
            return False
            
    except Exception as e:
        print(f"エラー: {e}")
        return False
    finally:
        scraper.close()

def find_multi_chapter_work():
    """複数話作品を検索"""
    print("\n=== 複数話作品検索 ===")
    
    # ハーメルンの人気作品で複数話ありそうなもの
    # （例として、ランキングにありそうな作品IDをいくつか試す）
    candidate_ids = ['380501', '372482', '379635', '371096']  # 前の調査で見つかった他の作品ID
    
    scraper = HamelnFinalScraper()
    
    try:
        for novel_id in candidate_ids:
            url = f"https://syosetu.org/novel/{novel_id}/"
            print(f"\n作品ID {novel_id} を調査中...")
            
            soup = scraper.get_page(url)
            if not soup:
                print(f"  ✗ 取得失敗")
                continue
                
            # タイトルを取得
            title_elem = soup.find('title')
            title = title_elem.get_text() if title_elem else 'Unknown'
            print(f"  タイトル: {title[:50]}...")
            
            # 章リンクを取得
            chapter_links = scraper.get_chapter_links(soup, url)
            print(f"  章数: {len(chapter_links)}")
            
            if len(chapter_links) > 1:
                print(f"  ✓ 複数話作品発見！")
                for i, link in enumerate(chapter_links[:3]):
                    print(f"    第{i+1}話: {link}")
                return novel_id, url, len(chapter_links)
        
        print("複数話作品が見つかりませんでした")
        return None, None, 0
        
    except Exception as e:
        print(f"エラー: {e}")
        return None, None, 0
    finally:
        scraper.close()

def test_multi_chapter_work(novel_id, url, expected_chapters):
    """複数話作品のテスト"""
    print(f"\n=== 複数話作品テスト ({novel_id}) ===")
    print(f"URL: {url}")
    print(f"期待される章数: {expected_chapters}")
    
    scraper = HamelnFinalScraper()
    
    try:
        # 全話取得をテスト（実際の保存はしない）
        soup = scraper.get_page(url)
        if not soup:
            print("✗ ページ取得失敗")
            return False
        
        chapter_links = scraper.get_chapter_links(soup, url)
        print(f"実際の章数: {len(chapter_links)}")
        
        if len(chapter_links) >= 2:
            print("✓ 複数話作品として正しく認識")
            
            # 最初の章の本文を取得してみる
            if chapter_links:
                first_chapter_url = chapter_links[0]
                print(f"第1話URL: {first_chapter_url}")
                
                # 第1話のページを取得
                first_chapter_soup = scraper.get_page(first_chapter_url)
                if first_chapter_soup:
                    content = scraper.extract_chapter_content(first_chapter_soup, first_chapter_url)
                    if content:
                        print(f"✓ 第1話本文取得成功: {len(content)}文字")
                        print(f"本文冒頭: {content[:100]}...")
                        return True
                    else:
                        print("✗ 第1話本文取得失敗")
                        return False
                else:
                    print("✗ 第1話ページ取得失敗")
                    return False
        else:
            print("✗ 単話作品として認識されました")
            return False
            
    except Exception as e:
        print(f"エラー: {e}")
        return False
    finally:
        scraper.close()

if __name__ == "__main__":
    print("ハーメルン作品タイプ別テスト開始")
    
    # 1. 単話作品テスト
    single_result = test_single_chapter_work()
    
    # 2. 複数話作品を検索
    multi_id, multi_url, chapter_count = find_multi_chapter_work()
    
    # 3. 複数話作品テスト
    multi_result = False
    if multi_id:
        multi_result = test_multi_chapter_work(multi_id, multi_url, chapter_count)
    
    # 結果まとめ
    print("\n=== テスト結果まとめ ===")
    print(f"単話作品テスト: {'✓ 成功' if single_result else '✗ 失敗'}")
    print(f"複数話作品テスト: {'✓ 成功' if multi_result else '✗ 失敗 (または複数話作品が見つからない)'}")
    
    if single_result and multi_result:
        print("✓ 両方のタイプが正しく処理されています")
    elif single_result:
        print("⚠ 単話作品のみ正常に処理されています")
    elif multi_result:
        print("⚠ 複数話作品のみ正常に処理されています")
    else:
        print("✗ 両方とも問題があります")