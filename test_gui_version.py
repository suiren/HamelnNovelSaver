#!/usr/bin/env python3
"""
修正版GUI版のテスト
resource_processorエラーが解決されているか確認
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hameln_scraper.core.scraper import HamelnScraper
from hameln_scraper.core.config import ScraperConfig

def test_gui_version_fix():
    """GUI版修正のテスト"""
    
    print("=== GUI版修正テスト ===")
    
    try:
        # 設定を作成
        config = ScraperConfig()
        config.enable_resource_saving = True  # リソース保存を有効にしてテスト
        
        # スクレイパーを初期化
        scraper = HamelnScraper(config)
        
        print("✓ HamelnScraper初期化成功")
        
        # resource_processorプロパティが存在するか確認
        if hasattr(scraper, 'resource_processor'):
            print("✓ resource_processorプロパティ存在確認")
        else:
            print("❌ resource_processorプロパティが存在しません")
            return False
        
        # process_html_resourcesメソッドが存在するか確認
        if hasattr(scraper.resource_processor, 'process_html_resources'):
            print("✓ process_html_resourcesメソッド存在確認")
        else:
            print("❌ process_html_resourcesメソッドが存在しません")
            return False
        
        # debug_logメソッドが存在するか確認
        if hasattr(scraper, 'debug_log'):
            print("✓ debug_logメソッド存在確認")
        else:
            print("❌ debug_logメソッドが存在しません")
            return False
            
        print("\n✓ すべてのメソッドとプロパティが正常に存在します")
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'scraper' in locals():
            scraper.close()

if __name__ == "__main__":
    success = test_gui_version_fix()
    if success:
        print("\n✅ GUI版修正テストが成功しました")
    else:
        print("\n❌ GUI版修正テストが失敗しました")
        sys.exit(1)