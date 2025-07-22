#!/usr/bin/env python3
"""
リンク形式とファイル名修正のためのテスト
TDD手順に従って期待される動作を定義
"""
import tempfile
import os
import pytest

def test_chapter_links_should_return_relative_paths():
    """章リンク抽出は相対パス形式で返すべき"""
    print("=== 章リンク相対パス形式テスト ===")
    
    try:
        from hameln_scraper.core.scraper import HamelnModularScraper
        
        # テスト用HTML（相対パスリンクを含む）
        test_html = """
        <html>
        <body>
            <a href="./1.html">第1話 始まりの章</a>
            <a href="./2.html">第2話 新たな力</a>
            <a href="./3.html">第3話 仲間との出会い</a>
        </body>
        </html>
        """
        
        scraper = HamelnModularScraper()
        
        # 章リンク抽出
        result = scraper.get_chapter_links(test_html, "https://syosetu.org/novel/123/")
        
        # 期待値: 相対パス形式のリンク
        expected_relative_links = ['./1.html', './2.html', './3.html']
        
        print(f"実際のリンク: {result.get('chapter_links', [])}")
        print(f"期待されるリンク: {expected_relative_links}")
        
        # テストは現在失敗するはず（修正前）
        for expected_link in expected_relative_links:
            if expected_link not in result.get('chapter_links', []):
                print(f"❌ 期待されるリンク {expected_link} が見つかりません")
                print("🔧 修正が必要: URL抽出で相対パスを保持する機能を追加")
                return False
        
        print("✅ 相対パス形式リンク抽出成功")
        scraper.close()
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        return False

def test_filename_should_respect_specified_name():
    """ファイル保存は指定されたfilename引数を尊重すべき"""
    print("=== filename引数尊重テスト ===")
    
    try:
        from hameln_scraper.core.scraper import HamelnModularScraper
        
        # テスト用HTML
        test_html = """
        <html>
        <head><title>テスト小説</title></head>
        <body>
            <div id="honbun">これはテスト内容です</div>
        </body>
        </html>
        """
        
        scraper = HamelnModularScraper()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # 指定されたファイル名で保存
            specified_filename = "test_chapter.html"
            
            result = scraper.save_complete_page(
                html_content=test_html,
                output_dir=temp_dir,
                filename=specified_filename,
                original_url="https://syosetu.org/novel/123/1/",
                title="第1話 自動生成されるべきでないタイトル"
            )
            
            expected_file_path = os.path.join(temp_dir, specified_filename)
            actual_saved_path = result.get('saved_path', '')
            
            print(f"期待されるファイルパス: {expected_file_path}")
            print(f"実際の保存パス: {actual_saved_path}")
            
            # テストは現在失敗するはず（修正前）
            if not os.path.exists(expected_file_path):
                print(f"❌ 指定されたファイル名 {specified_filename} で保存されていません")
                print("🔧 修正が必要: filename引数を優先する保存機能を追加")
                
                # 実際に生成されたファイルを確認
                files_in_dir = os.listdir(temp_dir)
                print(f"実際に生成されたファイル: {files_in_dir}")
                return False
            
            print("✅ 指定ファイル名での保存成功")
            scraper.close()
            return True
            
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        return False

def test_absolute_to_relative_conversion():
    """絶対パスから相対パスへの変換機能テスト"""
    print("=== 絶対パス→相対パス変換テスト ===")
    
    try:
        from hameln_scraper.core.scraper import HamelnModularScraper
        
        # テスト用HTML（絶対パスリンクを含む）
        test_html = """
        <html>
        <body>
            <a href="https://syosetu.org/novel/123/1/">第1話</a>
            <a href="https://syosetu.org/novel/123/2/">第2話</a>
            <a href="https://syosetu.org/novel/123/3/">第3話</a>
        </body>
        </html>
        """
        
        scraper = HamelnModularScraper()
        
        # 章リンク抽出（相対パス変換オプション付き）
        result = scraper.get_chapter_links(
            test_html, 
            "https://syosetu.org/novel/123/",
            convert_to_relative=True  # 新しいオプション
        )
        
        # 期待値: 絶対パスが相対パスに変換される
        expected_relative_links = ['./1.html', './2.html', './3.html']
        
        print(f"変換後のリンク: {result.get('chapter_links', [])}")
        print(f"期待される相対パス: {expected_relative_links}")
        
        # この機能は新規追加なので最初は失敗するはず
        for expected_link in expected_relative_links:
            if expected_link not in result.get('chapter_links', []):
                print(f"❌ 変換後リンク {expected_link} が見つかりません")
                print("🔧 修正が必要: 絶対パス→相対パス変換機能を追加")
                return False
        
        print("✅ 絶対パス→相対パス変換成功")
        scraper.close()
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        return False

if __name__ == "__main__":
    print("🧪 リンク形式・ファイル名修正テスト開始\n")
    
    tests = [
        ("相対パス形式リンク抽出", test_chapter_links_should_return_relative_paths),
        ("filename引数尊重", test_filename_should_respect_specified_name),
        ("絶対パス→相対パス変換", test_absolute_to_relative_conversion)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"📋 テスト: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ テスト実行エラー: {e}")
            results.append((test_name, False))
        print()
    
    print("📊 テスト結果サマリー:")
    success_count = 0
    for test_name, success in results:
        status = "✅ 成功" if success else "❌ 失敗"
        print(f"   {status}: {test_name}")
        if success:
            success_count += 1
    
    total_count = len(results)
    success_rate = (success_count / total_count) * 100 if total_count > 0 else 0
    
    print(f"\n📈 結果: {success_count}/{total_count} テスト成功")
    print(f"成功率: {success_rate:.1f}%")
    
    if success_count == total_count:
        print("🎉 全テスト成功！修正は不要です")
    else:
        print("🔧 修正が必要なテストがあります")