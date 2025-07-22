#!/usr/bin/env python3
"""
エンドツーエンド統合テスト - 全機能の包括的検証
"""

import sys
import os
sys.path.append('/home/suiren/ClaudeTest')

from hameln_scraper.core.scraper import HamelnModularScraper
from bs4 import BeautifulSoup

def test_end_to_end_integration():
    """全機能のエンドツーエンド統合テスト"""
    
    # テスト設定
    novel_dir = "/home/suiren/ClaudeTest/novels/片田舎の剣聖 錬鉄の英霊"
    base_url = "https://syosetu.org/novel/380014/"
    
    print("=== エンドツーエンド統合テスト ===")
    print(f"対象ディレクトリ: {novel_dir}")
    print(f"ベースURL: {base_url}")
    
    # 1. ファイル存在確認
    print(f"\n1. 必要ファイルの存在確認:")
    required_files = check_required_files(novel_dir)
    
    # 2. 全ページタイプのナビゲーション確認
    print(f"\n2. 全ページナビゲーション確認:")
    navigation_results = check_comprehensive_navigation(novel_dir)
    
    # 3. 相互リンクの完全性確認
    print(f"\n3. 相互リンクの完全性確認:")
    cross_link_results = check_cross_link_completeness(novel_dir)
    
    # 4. 外部リンク残存確認
    print(f"\n4. 外部リンク残存確認:")
    external_link_results = check_external_links_status(novel_dir)
    
    # 5. 総合評価
    print(f"\n5. 総合評価:")
    overall_score = calculate_overall_score(
        required_files, navigation_results, 
        cross_link_results, external_link_results
    )
    
    return {
        'overall_score': overall_score,
        'required_files': required_files,
        'navigation': navigation_results,
        'cross_links': cross_link_results,
        'external_links': external_link_results
    }

def check_required_files(novel_dir):
    """必要ファイルの存在確認"""
    
    required_files = {
        '目次.html': '目次ページ',
        '片田舎の剣聖 錬鉄の英霊 - 小説情報.html': '小説情報ページ',
        '感想/感想 - ページ1.html': '感想ページ1',
        '感想/感想 - ページ2.html': '感想ページ2',
        '第001話.html': '第1話',
        '第002話.html': '第2話',
        '第003話.html': '第3話',
        '第004話.html': '第4話',
        '第005話.html': '第5話',
        '第006話.html': '第6話'
    }
    
    results = {}
    for file_path, description in required_files.items():
        full_path = os.path.join(novel_dir, file_path)
        exists = os.path.exists(full_path)
        
        if exists:
            file_size = os.path.getsize(full_path)
            results[file_path] = {'exists': True, 'size': file_size, 'description': description}
            print(f"  ✅ {description}: {file_size:,} bytes")
        else:
            results[file_path] = {'exists': False, 'size': 0, 'description': description}
            print(f"  ❌ {description}: ファイルが見つかりません")
    
    total_files = len(required_files)
    existing_files = sum(1 for r in results.values() if r['exists'])
    print(f"  📊 ファイル存在率: {existing_files}/{total_files} ({existing_files/total_files*100:.1f}%)")
    
    return results

def check_comprehensive_navigation(novel_dir):
    """全ページナビゲーションの包括的確認"""
    
    # テスト対象のページと期待されるナビゲーションリンク
    navigation_tests = {
        '目次.html': {
            'expected_local_links': [
                '第001話.html', '第002話.html', '第003話.html', 
                '第004話.html', '第005話.html', '第006話.html',
                '片田舎の剣聖 錬鉄の英霊 - 小説情報.html',
                '感想/感想 - ページ1.html'
            ],
            'description': '目次ページ'
        },
        '片田舎の剣聖 錬鉄の英霊 - 小説情報.html': {
            'expected_local_links': [
                '目次.html',
                '感想/感想 - ページ1.html'
            ],
            'description': '小説情報ページ'
        },
        '感想/感想 - ページ1.html': {
            'expected_local_links': [
                '../目次.html',
                '../片田舎の剣聖 錬鉄の英霊 - 小説情報.html'
            ],
            'description': '感想ページ1'
        },
        '第001話.html': {
            'expected_local_links': [
                '目次.html',
                '片田舎の剣聖 錬鉄の英霊 - 小説情報.html'
            ],
            'description': '第1話'
        }
    }
    
    results = {}
    
    for file_path, test_config in navigation_tests.items():
        full_path = os.path.join(novel_dir, file_path)
        
        if not os.path.exists(full_path):
            results[file_path] = {'status': 'file_not_found'}
            print(f"  ❌ {test_config['description']}: ファイルが見つかりません")
            continue
        
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # 実際に存在するローカルリンクを確認
        found_local_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            for expected_link in test_config['expected_local_links']:
                if expected_link in href and not href.startswith('http'):
                    found_local_links.append(expected_link)
        
        # 重複削除
        found_local_links = list(set(found_local_links))
        
        # 結果評価
        expected_count = len(test_config['expected_local_links'])
        found_count = len(found_local_links)
        success_rate = (found_count / expected_count * 100) if expected_count > 0 else 100
        
        results[file_path] = {
            'status': 'checked',
            'expected_count': expected_count,
            'found_count': found_count,
            'success_rate': success_rate,
            'found_links': found_local_links
        }
        
        status_icon = "✅" if success_rate >= 90 else "⚠️" if success_rate >= 70 else "❌"
        print(f"  {status_icon} {test_config['description']}: {found_count}/{expected_count}個のリンク確認 ({success_rate:.1f}%)")
    
    return results

def check_cross_link_completeness(novel_dir):
    """相互リンクの完全性確認"""
    
    # クロスリンクのペア確認
    cross_link_pairs = [
        ('目次.html', '片田舎の剣聖 錬鉄の英霊 - 小説情報.html'),
        ('目次.html', '感想/感想 - ページ1.html'),
        ('片田舎の剣聖 錬鉄の英霊 - 小説情報.html', '目次.html'),
        ('感想/感想 - ページ1.html', '../目次.html'),
        ('感想/感想 - ページ1.html', '../片田舎の剣聖 錬鉄の英霊 - 小説情報.html')
    ]
    
    results = {
        'total_pairs': len(cross_link_pairs),
        'successful_pairs': 0,
        'details': []
    }
    
    for source_file, target_link in cross_link_pairs:
        source_path = os.path.join(novel_dir, source_file)
        
        if not os.path.exists(source_path):
            results['details'].append({
                'source': source_file,
                'target': target_link,
                'status': 'source_not_found'
            })
            continue
        
        with open(source_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # 対象リンクの存在確認
        link_found = False
        for link in soup.find_all('a', href=True):
            if target_link in link['href']:
                link_found = True
                break
        
        if link_found:
            results['successful_pairs'] += 1
            status = 'success'
            icon = "✅"
        else:
            status = 'link_not_found'
            icon = "❌"
        
        results['details'].append({
            'source': source_file,
            'target': target_link,
            'status': status
        })
        
        print(f"  {icon} {source_file} → {target_link}")
    
    success_rate = (results['successful_pairs'] / results['total_pairs'] * 100)
    print(f"  📊 クロスリンク成功率: {results['successful_pairs']}/{results['total_pairs']} ({success_rate:.1f}%)")
    
    return results

def check_external_links_status(novel_dir):
    """外部リンクの残存確認（意図的残存と意図しない残存の区別）"""
    
    # 意図的に残すべき外部リンクのパターン
    allowed_external_patterns = [
        'https://syosetu.org/search/',  # 検索機能
        'https://syosetu.org/?mode=rank',  # ランキング
        'https://syosetu.org/?mode=login',  # ログイン
        'https://syosetu.org/rule.html',  # 利用規約
        'https://syosetu.org/user/',  # ユーザーページ
        'https://img.syosetu.org/',  # 画像リソース
        'javascript:',  # JavaScript関数
        '#',  # ページ内リンク
        'https://syosetu.org/?mode=ss_detail3',  # 縦書き
        'https://syosetu.org/?mode=rating_input',  # 評価
        'https://syosetu.org/?mode=recommended_list',  # 推薦
        'https://syosetu.org/?mode=ss_detail_like',  # ここすき
        'https://syosetu.org/?mode=ss_config',  # 閲覧設定
        'https://twitter.com/'  # SNS共有
    ]
    
    # 修正すべきだった外部リンクのパターン
    problematic_patterns = [
        'https://syosetu.org/novel/380014/',  # 目次リンク
        'https://syosetu.org/?mode=ss_detail&nid=380014',  # 小説情報リンク
        'https://syosetu.org/?mode=review&nid=380014'  # 感想リンク
    ]
    
    files_to_check = ['目次.html', '片田舎の剣聖 錬鉄の英霊 - 小説情報.html', '第001話.html']
    
    results = {
        'total_problematic': 0,
        'total_allowed': 0,
        'file_details': []
    }
    
    for file_name in files_to_check:
        file_path = os.path.join(novel_dir, file_name)
        
        if not os.path.exists(file_path):
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        problematic_links = []
        allowed_links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            if href.startswith('http') or href.startswith('javascript:'):
                # 問題のあるリンクかチェック
                is_problematic = any(pattern in href for pattern in problematic_patterns)
                
                if is_problematic:
                    problematic_links.append(href)
                else:
                    # 許可されたリンクかチェック
                    is_allowed = any(pattern in href for pattern in allowed_external_patterns)
                    if is_allowed:
                        allowed_links.append(href)
        
        file_result = {
            'file': file_name,
            'problematic_count': len(problematic_links),
            'allowed_count': len(allowed_links),
            'problematic_links': problematic_links[:3],  # 最初の3つのみ表示
            'status': 'good' if len(problematic_links) == 0 else 'needs_fix'
        }
        
        results['file_details'].append(file_result)
        results['total_problematic'] += len(problematic_links)
        results['total_allowed'] += len(allowed_links)
        
        status_icon = "✅" if len(problematic_links) == 0 else "❌"
        print(f"  {status_icon} {file_name}: 問題のある外部リンク{len(problematic_links)}個, 許可された外部リンク{len(allowed_links)}個")
        
        if problematic_links:
            for link in problematic_links[:2]:  # 最初の2つを表示
                print(f"    ⚠️  {link}")
    
    print(f"  📊 全体: 問題のある外部リンク{results['total_problematic']}個, 許可された外部リンク{results['total_allowed']}個")
    
    return results

def calculate_overall_score(required_files, navigation_results, cross_link_results, external_link_results):
    """総合スコア計算"""
    
    # ファイル存在スコア (25%)
    file_count = len(required_files)
    existing_files = sum(1 for r in required_files.values() if r['exists'])
    file_score = (existing_files / file_count) * 25
    
    # ナビゲーションスコア (25%)  
    nav_scores = [r.get('success_rate', 0) for r in navigation_results.values() if r.get('status') == 'checked']
    nav_score = (sum(nav_scores) / len(nav_scores) / 100 * 25) if nav_scores else 0
    
    # クロスリンクスコア (25%)
    cross_score = (cross_link_results['successful_pairs'] / cross_link_results['total_pairs']) * 25
    
    # 外部リンク処理スコア (25%)
    external_score = 25 if external_link_results['total_problematic'] == 0 else max(0, 25 - external_link_results['total_problematic'] * 5)
    
    total_score = file_score + nav_score + cross_score + external_score
    
    print(f"  📊 ファイル存在: {file_score:.1f}/25")
    print(f"  📊 ナビゲーション: {nav_score:.1f}/25") 
    print(f"  📊 クロスリンク: {cross_score:.1f}/25")
    print(f"  📊 外部リンク処理: {external_score:.1f}/25")
    print(f"  🎯 総合スコア: {total_score:.1f}/100")
    
    if total_score >= 95:
        grade = "A+ (優秀)"
    elif total_score >= 90:
        grade = "A (良好)"
    elif total_score >= 85:
        grade = "B+ (概ね良好)"
    elif total_score >= 80:
        grade = "B (普通)"
    else:
        grade = "C (要改善)"
    
    print(f"  🏆 評価: {grade}")
    
    return {
        'total_score': total_score,
        'file_score': file_score,
        'nav_score': nav_score,
        'cross_score': cross_score,
        'external_score': external_score,
        'grade': grade
    }

if __name__ == "__main__":
    test_end_to_end_integration()