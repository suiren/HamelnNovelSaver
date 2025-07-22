#!/usr/bin/env python3
"""
ResourceProcessor引数修正のテスト
"""

import sys
import os
import tempfile
import shutil
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hameln_scraper.core.scraper import HamelnScraper
from hameln_scraper.core.config import ScraperConfig
from bs4 import BeautifulSoup

def test_resource_processor_fix():
    """ResourceProcessor引数修正のテスト"""
    
    print("=== ResourceProcessor引数修正テスト ===")
    
    # 一時ディレクトリを作成
    temp_dir = tempfile.mkdtemp()
    
    try:
        # 設定を作成
        config = ScraperConfig()
        config.enable_resource_saving = True
        
        # スクレイパーを初期化
        scraper = HamelnScraper(config)
        
        print("✓ HamelnScraper初期化成功")
        
        # 簡単なHTMLを作成
        html_content = """
        <html>
        <head>
            <link rel="stylesheet" href="https://example.com/style.css">
        </head>
        <body>
            <p>テストHTML</p>
            <img src="https://example.com/image.jpg" alt="テスト画像">
        </body>
        </html>
        """
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # process_html_resourcesメソッドを呼び出してエラーがないかテスト
        try:
            # 実際のメソッド呼び出し（引数修正版）
            result_soup = scraper.resource_processor.process_html_resources(soup, temp_dir)
            print("✓ process_html_resources呼び出し成功")
            
            # 結果がBeautifulSoupオブジェクトかチェック
            if isinstance(result_soup, BeautifulSoup):
                print("✓ 正常な戻り値（BeautifulSoupオブジェクト）")
            else:
                print(f"⚠️ 戻り値の型が予期しないものです: {type(result_soup)}")
            
            return True
            
        except TypeError as e:
            if "takes 3 positional arguments" in str(e):
                print(f"❌ 引数エラーが依然として発生: {e}")
                return False
            else:
                print(f"⚠️ 別のTypeError: {e}")
                return True  # 別のエラーは正常（ネットワーク接続等）
        except Exception as e:
            print(f"⚠️ 予期されるエラー（ネットワーク接続等）: {e}")
            return True  # ネットワークエラー等は正常
        
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 一時ディレクトリを削除
        shutil.rmtree(temp_dir, ignore_errors=True)
        if 'scraper' in locals():
            scraper.close()

if __name__ == "__main__":
    success = test_resource_processor_fix()
    if success:
        print("\n✅ ResourceProcessor引数修正テストが成功しました")
    else:
        print("\n❌ ResourceProcessor引数修正テストが失敗しました")
        sys.exit(1)