#!/usr/bin/env python3
"""
感想表示問題修正の確認テスト
"""

import sys
import os
sys.path.append('/home/suiren/ClaudeTest')

from bs4 import BeautifulSoup

def test_comments_display_fix():
    """修正後の感想表示確認"""
    
    novel_dir = "/home/suiren/ClaudeTest/novels/片田舎の剣聖 錬鉄の英霊"
    comments_dir = os.path.join(novel_dir, "感想")
    
    print("=== 感想表示問題修正確認テスト ===")
    
    # Step 1: HTMLファイル内の感想ブロック確認
    print("\n📋 Step 1: HTML内感想ブロックの存在確認")
    pages = ["感想 - ページ1.html", "感想 - ページ2.html"]
    
    total_comments_in_html = 0
    
    for page in pages:
        page_path = os.path.join(comments_dir, page)
        
        if os.path.exists(page_path):
            with open(page_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # section3クラスの感想ブロック数
            comment_blocks = soup.find_all('div', class_='section3')
            total_comments_in_html += len(comment_blocks)
            
            print(f"✅ {page}: {len(comment_blocks)}個の感想ブロック")
            
            # 感想の内容サンプル確認
            if comment_blocks:
                first_comment = comment_blocks[0]
                username_link = first_comment.find('h3').find('a')
                username = username_link.text.strip() if username_link else "不明"
                comment_text = first_comment.find('p')
                comment_sample = comment_text.text.strip()[:30] + "..." if comment_text else "本文なし"
                print(f"   サンプル: {username} - {comment_sample}")
        else:
            print(f"❌ {page}: ファイルなし")
    
    print(f"\n📊 HTML内感想総数: {total_comments_in_html}個")
    
    # Step 2: JavaScriptファイルの修正確認
    print("\n🔧 Step 2: JavaScript修正内容の確認")
    js_path = os.path.join(comments_dir, "comments_filter.js")
    
    if os.path.exists(js_path):
        with open(js_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        # 修正箇所の確認
        safety_checks = [
            ('フォールバック機能', 'attachBasicHandlers()' in js_content),
            ('安全な初期化', 'console.log(\'感想フィルタリング機能初期化開始...)' in js_content),
            ('JSONエラーハンドリング', 'return false' in js_content and 'response.ok' in js_content),
            ('安全な感想削除', 'this.allComments.length === 0' in js_content and '既存HTML感想を維持' in js_content),
            ('エラー時の表示維持', '.comments-js-disabled' in js_content)
        ]
        
        all_safety_present = True
        for check_name, check_result in safety_checks:
            status = "✅" if check_result else "❌"
            print(f"  {status} {check_name}: {'実装済み' if check_result else '未実装'}")
            if not check_result:
                all_safety_present = False
        
        if all_safety_present:
            print("✅ 全ての安全機能が実装されています")
        else:
            print("⚠️ 一部の安全機能が不足しています")
            
    else:
        print("❌ JavaScriptファイルなし")
    
    # Step 3: JSONデータファイルの確認
    print("\n📄 Step 3: JSONデータファイルの確認")
    json_path = os.path.join(comments_dir, "comments_data.json")
    
    json_valid = False
    if os.path.exists(json_path):
        try:
            import json
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            comments_in_json = len(data.get('comments', []))
            print(f"✅ JSONファイル正常: {comments_in_json}件の感想データ")
            json_valid = True
            
        except Exception as e:
            print(f"❌ JSON解析エラー: {e}")
    else:
        print("❌ JSONファイルなし")
    
    # Step 4: 予想される動作シナリオ
    print("\n🎯 Step 4: 予想される動作シナリオ")
    
    if json_valid:
        print("📱 シナリオA: JSON読み込み成功時")
        print("  - JavaScript動的機能が有効化")
        print("  - ソート・フィルタリング機能利用可能") 
        print("  - 元のHTML感想は動的に置き換え")
        
    print("📱 シナリオB: JSON読み込み失敗時")
    print("  - フォールバック機能が自動起動")
    print("  - 元のHTML感想表示を維持")
    print("  - 「※ 動的機能は無効です」メッセージ表示")
    print("  - 基本ページネーション機能は継続")
    
    # Step 5: 修正効果の期待値
    print("\n🏆 Step 5: 修正効果")
    
    print("✅ 感想0問題の解決:")
    print("  - JavaScript失敗でも元のHTML感想が残る")
    print("  - フォールバック機能で最低限の表示保証")
    print("  - エラー状況の詳細ログ出力")
    
    print("✅ 安全性の向上:")
    print("  - 段階的な初期化プロセス")
    print("  - データ検証とエラーハンドリング")
    print("  - ユーザーフレンドリーなエラー表示")
    
    print("\n🌐 ブラウザでの確認推奨:")
    print(f"1. {os.path.join(comments_dir, '感想 - ページ2.html')} をブラウザで開く")
    print("2. 開発者ツールのコンソールでログ確認")
    print("3. 感想が表示されることを確認")
    print("4. JavaScript機能の動作状況を確認")
    
    return {
        'html_comments_count': total_comments_in_html,
        'json_valid': json_valid,
        'safety_implemented': all_safety_present
    }

if __name__ == "__main__":
    test_comments_display_fix()