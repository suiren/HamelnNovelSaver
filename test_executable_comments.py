#!/usr/bin/env python3
"""
実行ファイルでの感想ページ複数ページ取得機能テスト
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hameln_scraper_final import HamelnFinalScraper

def test_executable_comments_functionality():
    """実行ファイルで使用される感想保存機能をテスト"""
    
    print("実行ファイル用の感想保存機能テストを開始...")
    
    try:
        # スクレイパーを初期化（実行ファイルと同じ設定）
        scraper = HamelnFinalScraper()
        
        # 感想保存機能を有効化（hameln_gui.pyの設定に合わせる）
        scraper.enable_comments_saving = True
        
        print(f"感想保存機能の状態: {scraper.enable_comments_saving}")
        
        # テスト用URL
        test_url = "https://syosetu.org/novel/378070/"
        
        # メインページを取得
        print("メインページを取得中...")
        main_page = scraper.get_page(test_url)
        
        if not main_page:
            print("❌ メインページの取得に失敗しました")
            return False
            
        # 感想ページのURLを抽出
        print("感想ページのURL抽出中...")
        comments_url = scraper.extract_comments_url(main_page)
        
        if not comments_url:
            print("❌ 感想ページURLの取得に失敗しました")
            return False
            
        print(f"✅ 感想ページURL取得成功: {comments_url}")
        
        # 感想ページの複数ページ取得機能をテスト
        print("感想ページの複数ページ取得をテスト中...")
        integrated_comments = scraper.get_all_comments_pages(comments_url)
        
        if integrated_comments:
            print("✅ 感想ページの複数ページ取得機能が正常に動作しています")
            
            # 統合結果の詳細情報を出力
            comments_text = str(integrated_comments)
            if "統合表示" in comments_text:
                print("✅ 複数ページの統合処理が実行されました")
            else:
                print("✅ 単一ページの感想が正常に取得されました")
                
            return True
        else:
            print("❌ 感想ページの複数ページ取得に失敗しました")
            return False
            
    except Exception as e:
        print(f"❌ テスト中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_executable_comments_functionality()
    
    if success:
        print("\n✅ 実行ファイル用の感想保存機能テストが成功しました！")
        print("実行ファイルでも感想の全ページ取得機能が動作するはずです。")
    else:
        print("\n❌ 実行ファイル用の感想保存機能テストが失敗しました。")
        print("実行ファイルを再ビルドしてください。")