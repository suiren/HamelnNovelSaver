#!/usr/bin/env python3
"""
PDFダウンロード機能のデバッグテスト
実際のハーメルン縦書きページでのPDFダウンロード処理を確認
"""

import os
import tempfile
import shutil
from hameln_scraper_final import HamelnFinalScraper

def test_pdf_download_debug():
    """実際のPDFダウンロード処理をテスト"""
    
    # スクレイパーを初期化
    scraper = HamelnFinalScraper()
    
    # 実際の縦書きページのURLを使用
    vertical_url = "https://syosetu.org/?mode=ss_detail3&nid=370348"
    
    print("=== PDFダウンロード機能デバッグテスト ===")
    print(f"縦書きページURL: {vertical_url}")
    
    # 一時ディレクトリを作成
    temp_dir = tempfile.mkdtemp()
    print(f"一時ディレクトリ: {temp_dir}")
    
    try:
        # 縦書きページを取得
        print("\n1. 縦書きページを取得中...")
        soup = scraper.get_page(vertical_url)
        
        if not soup:
            print("❌ 縦書きページの取得に失敗")
            return False
        
        print("✅ 縦書きページ取得成功")
        
        # PDFリンクを抽出
        print("\n2. PDFリンクを抽出中...")
        pdf_links = scraper.extract_pdf_links_from_vertical_page(soup)
        print(f"抽出されたPDFリンク数: {len(pdf_links)}")
        
        for i, link in enumerate(pdf_links):
            print(f"  PDFリンク{i+1}: {link}")
        
        if not pdf_links:
            print("❌ PDFリンクが見つかりません")
            return False
        
        # PDFダウンロード・ローカル化を実行
        print("\n3. PDFダウンロード・ローカル化を実行中...")
        updated_soup = scraper.download_and_localize_pdf_links(soup, temp_dir, "テスト小説")
        
        # 結果を確認
        print("\n4. 結果確認...")
        
        # ダウンロードされたファイルを確認
        downloaded_files = [f for f in os.listdir(temp_dir) if f.endswith(('.pdf', '.txt', '.epub'))]
        print(f"ダウンロードされたファイル数: {len(downloaded_files)}")
        
        for file in downloaded_files:
            file_path = os.path.join(temp_dir, file)
            file_size = os.path.getsize(file_path)
            print(f"  {file} (サイズ: {file_size}バイト)")
        
        # HTML内のリンクが変更されているかを確認
        print("\n5. HTML内のリンク変更確認...")
        pdf_count = 0
        for link in updated_soup.find_all('a', href=True):
            href = link.get('href')
            if any(keyword in href for keyword in ['pdf', 'txt', 'epub', '#']):
                pdf_count += 1
                print(f"  リンク: {href} (テキスト: '{link.get_text(strip=True)}')")
                if 'onclick' in link.attrs:
                    print(f"    onclick: {link.get('onclick')}")
                if 'title' in link.attrs:
                    print(f"    title: {link.get('title')}")
        
        print(f"\n処理されたPDFリンク数: {pdf_count}")
        
        success = len(downloaded_files) > 0
        print(f"\n結果: {'✅ 成功' if success else '❌ 失敗'}")
        return success
        
    finally:
        # 一時ディレクトリを削除
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    test_pdf_download_debug()