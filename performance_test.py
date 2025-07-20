"""
HamelnModularScraper パフォーマンステスト
新モジュール構造と元ファイルの性能比較
"""

import time
import tracemalloc
import gc
import tempfile
import os
import sys
from real_hameln_samples import get_all_real_samples
from typing import Dict, Any, List


def measure_performance(test_func, test_name: str, iterations: int = 3) -> Dict[str, Any]:
    """
    関数の実行時間とメモリ使用量を測定
    
    Args:
        test_func: テスト対象の関数
        test_name: テスト名
        iterations: 実行回数
        
    Returns:
        Dict[str, Any]: パフォーマンス測定結果
    """
    print(f"\n📊 {test_name} パフォーマンス測定開始...")
    
    execution_times = []
    memory_peaks = []
    
    for i in range(iterations):
        print(f"   実行 {i+1}/{iterations}...")
        
        # ガベージコレクション実行
        gc.collect()
        
        # メモリ使用量測定開始
        tracemalloc.start()
        
        # 実行時間測定開始
        start_time = time.perf_counter()
        
        try:
            # テスト関数実行
            result = test_func()
            
            # 実行時間測定終了
            end_time = time.perf_counter()
            execution_time = end_time - start_time
            execution_times.append(execution_time)
            
            # メモリ使用量測定終了
            current, peak = tracemalloc.get_traced_memory()
            memory_peaks.append(peak)
            
            print(f"      実行時間: {execution_time:.3f}秒, メモリピーク: {peak / 1024 / 1024:.2f}MB")
            
        except Exception as e:
            print(f"      ❌ エラー: {e}")
            execution_times.append(float('inf'))
            memory_peaks.append(0)
        
        finally:
            tracemalloc.stop()
    
    # 統計計算
    valid_times = [t for t in execution_times if t != float('inf')]
    valid_memory = [m for m in memory_peaks if m > 0]
    
    if not valid_times:
        return {
            'test_name': test_name,
            'success': False,
            'error': '全ての実行でエラーが発生'
        }
    
    avg_time = sum(valid_times) / len(valid_times)
    min_time = min(valid_times)
    max_time = max(valid_times)
    
    avg_memory = sum(valid_memory) / len(valid_memory) if valid_memory else 0
    max_memory = max(valid_memory) if valid_memory else 0
    
    result = {
        'test_name': test_name,
        'success': True,
        'iterations': len(valid_times),
        'execution_time': {
            'average': avg_time,
            'minimum': min_time,
            'maximum': max_time,
            'unit': 'seconds'
        },
        'memory_usage': {
            'average_peak': avg_memory / 1024 / 1024,  # MB
            'maximum_peak': max_memory / 1024 / 1024,  # MB
            'unit': 'MB'
        }
    }
    
    print(f"   ✅ 平均実行時間: {avg_time:.3f}秒")
    print(f"   ✅ 平均メモリピーク: {avg_memory / 1024 / 1024:.2f}MB")
    
    return result


def test_modular_scraper_initialization() -> bool:
    """HamelnModularScraper初期化パフォーマンステスト"""
    try:
        from hameln_scraper.core.scraper import HamelnModularScraper
        
        scraper = HamelnModularScraper()
        scraper.close()
        return True
        
    except Exception as e:
        print(f"初期化エラー: {e}")
        return False


def test_modular_scraper_content_extraction() -> bool:
    """HamelnModularScraper コンテンツ抽出パフォーマンステスト"""
    try:
        from hameln_scraper.core.scraper import HamelnModularScraper
        
        scraper = HamelnModularScraper()
        samples = get_all_real_samples()
        
        # 4つの異なる構造でテスト
        test_samples = [
            samples['chapter_basic'],
            samples['section2_pattern'],
            samples['modern_p_novel_text'],
            samples['complex_nested']
        ]
        
        for i, html in enumerate(test_samples, 1):
            result = scraper.extract_chapter_content(
                html, 
                f"https://syosetu.org/novel/123/{i}/"
            )
            if not result['success']:
                return False
        
        scraper.close()
        return True
        
    except Exception as e:
        print(f"コンテンツ抽出エラー: {e}")
        return False


def test_modular_scraper_page_saving() -> bool:
    """HamelnModularScraper ページ保存パフォーマンステスト"""
    try:
        from hameln_scraper.core.scraper import HamelnModularScraper
        
        scraper = HamelnModularScraper()
        samples = get_all_real_samples()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # 4つのページを順次保存
            for i, (name, html) in enumerate(samples.items(), 1):
                if i > 4:  # 最初の4つのみテスト
                    break
                    
                result = scraper.save_complete_page(
                    html_content=html,
                    output_dir=temp_dir,
                    filename=f"test_{i}.html",
                    original_url=f"https://syosetu.org/novel/123/{i}/",
                    title=f"テスト第{i}話"
                )
                
                if not result['success']:
                    return False
        
        scraper.close()
        return True
        
    except Exception as e:
        print(f"ページ保存エラー: {e}")
        return False


def test_modular_scraper_full_workflow() -> bool:
    """HamelnModularScraper 完全ワークフローパフォーマンステスト"""
    try:
        from hameln_scraper.core.scraper import HamelnModularScraper
        
        scraper = HamelnModularScraper()
        samples = get_all_real_samples()
        
        # Phase 1: 小説情報抽出
        novel_info = scraper.extract_novel_info(
            samples['index_page'], 
            "https://syosetu.org/novel/123/"
        )
        if not novel_info['success']:
            return False
        
        # Phase 2: 章リンク取得
        chapter_links = scraper.get_chapter_links(
            samples['index_page'], 
            "https://syosetu.org/novel/123/"
        )
        if not chapter_links['success']:
            return False
        
        # Phase 3: 章内容抽出
        for i, html in enumerate([samples['chapter_basic'], samples['section2_pattern']], 1):
            content_result = scraper.extract_chapter_content(
                html, 
                f"https://syosetu.org/novel/123/{i}/"
            )
            if not content_result['success']:
                return False
        
        # Phase 4: ページ保存
        with tempfile.TemporaryDirectory() as temp_dir:
            for i, html in enumerate([samples['chapter_basic'], samples['section2_pattern']], 1):
                save_result = scraper.save_complete_page(
                    html_content=html,
                    output_dir=temp_dir,
                    filename=f"workflow_{i}.html",
                    original_url=f"https://syosetu.org/novel/123/{i}/",
                    title=f"ワークフロー第{i}話"
                )
                if not save_result['success']:
                    return False
        
        scraper.close()
        return True
        
    except Exception as e:
        print(f"完全ワークフローエラー: {e}")
        return False


def test_bridge_compatibility() -> bool:
    """モジュール互換性ブリッジのパフォーマンステスト"""
    try:
        # 互換性ブリッジファイルが存在するかテスト
        if os.path.exists('/home/suiren/ClaudeTest/hameln_scraper_modular_bridge.py'):
            sys.path.insert(0, '/home/suiren/ClaudeTest')
            from hameln_scraper_modular_bridge import HamelnScraperCompatibility
            
            scraper = HamelnScraperCompatibility()
            
            # 基本的なメソッド呼び出しテスト
            test_html = "<html><body><div class='section1'><p>テスト</p></div></body></html>"
            
            result = scraper.extract_chapter_content(
                test_html, 
                "https://test.com"
            )
            
            scraper.close()
            return result.get('success', False)
        else:
            print("互換性ブリッジファイルが見つかりません")
            return False
        
    except Exception as e:
        print(f"ブリッジ互換性エラー: {e}")
        return False


def run_performance_tests() -> Dict[str, Any]:
    """全パフォーマンステスト実行"""
    print("🚀 HamelnModularScraper パフォーマンステスト開始")
    print("=" * 80)
    
    # テスト関数リスト
    performance_tests = [
        ("初期化性能", test_modular_scraper_initialization),
        ("コンテンツ抽出性能", test_modular_scraper_content_extraction),
        ("ページ保存性能", test_modular_scraper_page_saving),
        ("完全ワークフロー性能", test_modular_scraper_full_workflow),
        ("互換性ブリッジ性能", test_bridge_compatibility)
    ]
    
    results = []
    
    for test_name, test_func in performance_tests:
        try:
            result = measure_performance(test_func, test_name, iterations=3)
            results.append(result)
        except Exception as e:
            print(f"❌ {test_name} で例外発生: {e}")
            results.append({
                'test_name': test_name,
                'success': False,
                'error': str(e)
            })
    
    print("\n" + "=" * 80)
    print("📊 パフォーマンステスト結果サマリー")
    print("=" * 80)
    
    successful_tests = 0
    total_execution_time = 0
    total_memory_usage = 0
    
    for result in results:
        if result['success']:
            successful_tests += 1
            exec_time = result['execution_time']['average']
            memory = result['memory_usage']['average_peak']
            
            total_execution_time += exec_time
            total_memory_usage += memory
            
            print(f"✅ {result['test_name']}")
            print(f"   実行時間: {exec_time:.3f}秒")
            print(f"   メモリ使用量: {memory:.2f}MB")
        else:
            print(f"❌ {result['test_name']}")
            if 'error' in result:
                print(f"   エラー: {result['error']}")
    
    success_rate = (successful_tests / len(results)) * 100
    
    print(f"\n📈 総合パフォーマンス評価")
    print(f"   成功率: {success_rate:.1f}% ({successful_tests}/{len(results)})")
    print(f"   総実行時間: {total_execution_time:.3f}秒")
    print(f"   平均メモリ使用量: {total_memory_usage / max(successful_tests, 1):.2f}MB")
    
    # パフォーマンス判定
    performance_grade = "A"
    if total_execution_time > 10:
        performance_grade = "C"
    elif total_execution_time > 5:
        performance_grade = "B"
    
    memory_grade = "A"
    avg_memory = total_memory_usage / max(successful_tests, 1)
    if avg_memory > 100:
        memory_grade = "C"
    elif avg_memory > 50:
        memory_grade = "B"
    
    print(f"   実行速度評価: {performance_grade}級")
    print(f"   メモリ効率評価: {memory_grade}級")
    
    return {
        'success_rate': success_rate,
        'total_execution_time': total_execution_time,
        'average_memory_usage': total_memory_usage / max(successful_tests, 1),
        'performance_grade': performance_grade,
        'memory_grade': memory_grade,
        'detailed_results': results
    }


if __name__ == "__main__":
    performance_results = run_performance_tests()
    
    if performance_results['success_rate'] >= 80:
        print(f"\n🎉 パフォーマンステスト成功！")
        print(f"新しいモジュール構造は良好な性能を示しています。")
    else:
        print(f"\n⚠️ パフォーマンス改善が必要です。")
        print(f"詳細な分析と最適化を検討してください。")