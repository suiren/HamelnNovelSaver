#!/usr/bin/env python3
"""
修正されたPDFリンク処理機能のテスト
"""

import os
import tempfile
import shutil
from hameln_scraper_final import HamelnFinalScraper
from bs4 import BeautifulSoup

def test_pdf_link_processing():
    """PDFリンク処理機能のテスト"""
    
    print("=== PDFリンク処理機能テスト ===")
    
    # スクレイパーを初期化
    scraper = HamelnFinalScraper()
    
    # 一時ディレクトリを作成
    temp_dir = tempfile.mkdtemp()
    
    try:
        # 縦書きページHTMLの作成（PDFリンクを含む）
        html_content = """
        <html>
        <head><title>テスト縦書きページ</title></head>
        <body>
            <div class="section normal">
                <h2>縦書きファイル出力</h2>
                <p><a href="/conv/pdf/378070/1/">縦書きＰＤＦ(文庫・特殊タグ一部あり)</a></p>
                <p><a href="/conv/pdf/378070/2/">縦書きＰＤＦ(文庫・特殊タグなし)</a></p>
                <p><a href="/conv/pdf/378070/3/">縦書きＰＤＦ(横長・特殊タグ一部あり)</a></p>
                <p><a href="/conv/pdf/378070/4/">縦書きＰＤＦ(横長・特殊タグなし)</a></p>
            </div>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # PDFリンクを抽出
        print("1. PDFリンク抽出テスト")
        pdf_links = scraper.extract_pdf_links_from_vertical_page(soup)
        print(f"抽出されたPDFリンク数: {len(pdf_links)}")
        
        expected_links = [
            "/conv/pdf/378070/1/",
            "/conv/pdf/378070/2/",
            "/conv/pdf/378070/3/",
            "/conv/pdf/378070/4/"
        ]
        
        if len(pdf_links) == len(expected_links):
            print("✓ PDFリンク抽出数が正しいです")
        else:
            print(f"❌ PDFリンク抽出数が不正です。期待値: {len(expected_links)}, 実際: {len(pdf_links)}")
            return False
        
        # PDFリンクの内容確認
        for i, link in enumerate(pdf_links):
            print(f"  PDFリンク{i+1}: {link}")
            if link not in expected_links:
                print(f"❌ 予期しないPDFリンクが抽出されました: {link}")
                return False
        
        print("✓ PDFリンクの内容が正しいです")
        
        # PDFリンク処理テスト
        print("\n2. PDFリンク処理テスト")
        print("修正版: PDFリンクを元のまま保持（サーバーサイド生成対応）")
        
        updated_soup = scraper.download_and_localize_pdf_links(soup, temp_dir, "テスト小説")
        
        # 処理後のリンクを確認
        processed_links = []
        for link in updated_soup.find_all('a', href=True):
            href = link.get('href')
            if any(keyword in href for keyword in ['pdf', 'conv']):
                processed_links.append({
                    'href': href,
                    'text': link.get_text(strip=True),
                    'title': link.get('title', ''),
                    'target': link.get('target', ''),
                    'rel': link.get('rel', '')
                })
        
        print(f"処理後のPDFリンク数: {len(processed_links)}")
        
        # 処理結果を検証
        success = True
        for link in processed_links:
            print(f"  処理済みリンク: {link['href']}")
            print(f"    テキスト: {link['text']}")
            print(f"    タイトル: {link['title']}")
            print(f"    ターゲット: {link['target']}")
            print(f"    Rel: {link['rel']}")
            
            # 絶対URLに変換されているかチェック
            if not link['href'].startswith('https://syosetu.org'):
                print(f"❌ 絶対URLに変換されていません: {link['href']}")
                success = False
            
            # 外部リンク属性がセットされているかチェック
            if link['target'] != '_blank':
                print(f"❌ target属性が正しくありません: {link['target']}")
                success = False
            
            # title属性があるかチェック
            if not link['title'] or 'PDFファイル生成' not in link['title']:
                print(f"❌ title属性が正しくありません: {link['title']}")
                success = False
        
        if success:
            print("✓ PDFリンク処理が正しく動作しています")
        else:
            print("❌ PDFリンク処理に問題があります")
            return False
        
        # 無効化処理が行われていないことを確認
        print("\n3. 無効化処理確認テスト")
        disabled_links = []
        for link in updated_soup.find_all('a', href=True):
            href = link.get('href')
            onclick = link.get('onclick', '')
            if href == '#' or 'alert' in onclick:
                disabled_links.append(link)
        
        if len(disabled_links) == 0:
            print("✓ PDFリンクの無効化処理は行われていません（正常）")
        else:
            print(f"❌ PDFリンクが無効化されています: {len(disabled_links)}個")
            return False
        
        return True
        
    finally:
        # 一時ディレクトリを削除
        shutil.rmtree(temp_dir, ignore_errors=True)
        scraper.close()

if __name__ == "__main__":
    success = test_pdf_link_processing()
    if success:
        print("\n✅ PDFリンク処理機能のテストが成功しました")
    else:
        print("\n❌ PDFリンク処理機能のテストが失敗しました")
        exit(1)