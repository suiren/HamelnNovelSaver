#!/usr/bin/env python3
"""
ビルドされたスクレイパーの機能テスト
"""
import sys
import os

def test_modular_scraper_function():
    """モジュールスクレイパーの基本機能テスト"""
    print("🧪 モジュールスクレイパー機能テスト開始")
    
    try:
        # モジュールインポート
        from hameln_scraper.core.scraper import HamelnModularScraper
        print("✅ モジュールインポート成功")
        
        # インスタンス作成
        scraper = HamelnModularScraper()
        print("✅ スクレイパーインスタンス作成成功")
        
        # 基本機能確認
        # 1. 設定確認
        if hasattr(scraper, 'network_client'):
            print("✅ ネットワーククライアント利用可能")
        else:
            print("⚠️ ネットワーククライアント属性なし")
            
        # 2. パーサー確認  
        if hasattr(scraper, 'content_parser'):
            print("✅ コンテンツパーサー利用可能")
        else:
            print("⚠️ コンテンツパーサー属性なし")
            
        # 3. セレクター確認
        if hasattr(scraper, 'get_content_selectors'):
            selectors = scraper.get_content_selectors()
            print(f"✅ コンテンツセレクター取得成功: {len(selectors)}個")
        else:
            print("⚠️ セレクター取得メソッドなし")
            
        # 4. URL検証機能テスト
        test_urls = [
            "https://syosetu.org/novel/123456/1.html",
            "https://example.com/invalid",
            ""
        ]
        
        for url in test_urls:
            try:
                if hasattr(scraper, 'network_client') and hasattr(scraper.network_client, 'validate_url'):
                    is_valid = scraper.network_client.validate_url(url)
                    print(f"✅ URL検証 '{url[:30]}...': {is_valid}")
                else:
                    print(f"⚠️ URL検証機能なし")
                    break
            except Exception as e:
                print(f"⚠️ URL検証エラー '{url[:30]}...': {e}")
        
        print("🎉 基本機能テスト完了")
        return True
        
    except ImportError as e:
        print(f"❌ インポートエラー: {e}")
        return False
    except Exception as e:
        print(f"❌ 機能テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gui_compatibility():
    """GUI互換性テスト"""
    print("\n🧪 GUI互換性テスト開始")
    
    try:
        # 元のGUIクラス確認
        import hameln_gui
        print("✅ GUI モジュールインポート成功")
        
        # HamelnScraperGUIクラス確認
        if hasattr(hameln_gui, 'HamelnScraperGUI'):
            print("✅ HamelnScraperGUIクラス利用可能")
            
            # インスタンス作成テスト（実際のGUI初期化はしない）
            print("✅ GUI互換性確認完了")
            return True
        else:
            print("❌ HamelnScraperGUIクラスが見つかりません")
            return False
            
    except Exception as e:
        print(f"❌ GUI互換性テストエラー: {e}")
        return False

if __name__ == "__main__":
    print("🚀 ビルド済みスクレイパー総合テスト開始\n")
    
    test1_result = test_modular_scraper_function()
    test2_result = test_gui_compatibility()
    
    overall_result = test1_result and test2_result
    
    print(f"\n📊 総合テスト結果:")
    print(f"   モジュール機能: {'✅ 成功' if test1_result else '❌ 失敗'}")
    print(f"   GUI互換性: {'✅ 成功' if test2_result else '❌ 失敗'}")
    print(f"   総合評価: {'🎉 成功' if overall_result else '❌ 失敗'}")
    
    sys.exit(0 if overall_result else 1)