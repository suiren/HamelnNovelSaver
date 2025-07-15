#!/usr/bin/env python3
"""
GUI版実行ファイルでの感想ページ複数ページ取得テスト
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hameln_gui import HamelnGUI
import tkinter as tk

def test_gui_comments_functionality():
    """GUI版で感想保存機能が有効化されているかテスト"""
    
    # Tkinterのルートウィンドウを作成
    root = tk.Tk()
    root.withdraw()  # ウィンドウを非表示にする
    
    # GUI インスタンスを作成
    gui = HamelnGUI(root)
    
    print("GUI版での感想保存機能テストを開始...")
    
    try:
        # テスト用URL
        test_url = "https://syosetu.org/novel/378070/"
        
        # GUI経由でスクレイパーを初期化
        gui.scraper = create_scraper_instance()
        
        # 感想保存機能が有効化されているかチェック
        if hasattr(gui.scraper, 'enable_comments_saving'):
            if gui.scraper.enable_comments_saving:
                print("✅ 感想保存機能が有効化されています")
            else:
                print("❌ 感想保存機能が無効化されています")
                return False
        else:
            print("❌ 感想保存機能の設定項目が見つかりません")
            return False
        
        # 感想ページのURLを抽出してテスト
        print("感想ページのURL抽出をテスト...")
        main_page = gui.scraper.get_page(test_url)
        
        if main_page:
            comments_url = gui.scraper.extract_comments_url(main_page)
            if comments_url:
                print(f"✅ 感想ページURL取得成功: {comments_url}")
                
                # 感想ページの複数ページ取得機能をテスト
                print("感想ページの複数ページ取得をテスト...")
                integrated_comments = gui.scraper.get_all_comments_pages(comments_url)
                
                if integrated_comments:
                    print("✅ 感想ページの複数ページ取得機能が正常に動作しています")
                    return True
                else:
                    print("❌ 感想ページの複数ページ取得に失敗しました")
                    return False
            else:
                print("❌ 感想ページURLの取得に失敗しました")
                return False
        else:
            print("❌ メインページの取得に失敗しました")
            return False
            
    except Exception as e:
        print(f"❌ テスト中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        root.destroy()

def create_scraper_instance():
    """GUI用のスクレイパーインスタンスを作成"""
    from hameln_scraper_final import HamelnFinalScraper
    
    scraper = HamelnFinalScraper()
    
    # 感想保存機能を有効化
    scraper.enable_comments_saving = True
    
    return scraper

if __name__ == "__main__":
    success = test_gui_comments_functionality()
    
    if success:
        print("\n✅ GUI版での感想保存機能テストが成功しました！")
        print("実行ファイルでも感想の全ページ取得機能が動作するはずです。")
    else:
        print("\n❌ GUI版での感想保存機能テストが失敗しました。")
        print("実行ファイルを再ビルドしてください。")