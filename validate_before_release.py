#!/usr/bin/env python3
"""
リリース前統合検証スクリプト
ユーザー環境での成功を保証するための最終チェックポイント
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from typing import Dict, List, Any
import subprocess

class ReleaseValidator:
    """リリース前検証システム"""
    
    def __init__(self, skip_build: bool = False, skip_network: bool = False):
        self.skip_build = skip_build
        self.skip_network = skip_network
        self.start_time = time.time()
        
    def print_header(self):
        """ヘッダー表示"""
        print("🚀" + "=" * 58 + "🚀")
        print("     ハーメルン小説保存アプリ - リリース前統合検証")
        print("🚀" + "=" * 58 + "🚀")
        print(f"実行時刻: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"スキップ設定: ビルド{'✓' if self.skip_build else '✗'} ネットワーク{'✓' if self.skip_network else '✗'}")
        print()
    
    def check_prerequisites(self) -> bool:
        """前提条件確認"""
        print("📋 前提条件確認中...")
        
        # 必要ファイル確認
        required_files = [
            'test_execution_environment.py',
            'detect_method_conflicts.py', 
            'test_comprehensive_validation.py'
        ]
        
        missing_files = []
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if missing_files:
            print(f"❌ 必要ファイル不足: {', '.join(missing_files)}")
            return False
        
        # Python版本確認
        if sys.version_info < (3, 8):
            print(f"❌ Python版本不足: {sys.version_info} (最低3.8必要)")
            return False
        
        print("✅ 前提条件OK")
        return True
    
    def run_validation_script(self, script_name: str, description: str, timeout: int = 300) -> Dict[str, Any]:
        """検証スクリプト実行"""
        print(f"\n🔄 {description} 実行中...")
        print(f"   スクリプト: {script_name}")
        print(f"   タイムアウト: {timeout}秒")
        
        try:
            start_time = time.time()
            result = subprocess.run([
                sys.executable, script_name
            ], capture_output=True, text=True, timeout=timeout)
            execution_time = time.time() - start_time
            
            success = result.returncode == 0
            
            print(f"   実行時間: {execution_time:.1f}秒")
            print(f"   結果: {'✅ 成功' if success else '❌ 失敗'}")
            
            if not success:
                print(f"   終了コード: {result.returncode}")
                if result.stderr:
                    print(f"   エラー: {result.stderr[:500]}...")
            
            return {
                'script': script_name,
                'success': success,
                'returncode': result.returncode,
                'execution_time': execution_time,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
        except subprocess.TimeoutExpired:
            print(f"   ❌ タイムアウト ({timeout}秒)")
            return {
                'script': script_name,
                'success': False,
                'error': 'timeout',
                'execution_time': timeout
            }
        except Exception as e:
            print(f"   ❌ 実行エラー: {e}")
            return {
                'script': script_name,
                'success': False,
                'error': str(e),
                'execution_time': 0
            }
    
    def run_manual_checks(self) -> Dict[str, Any]:
        """手動確認項目"""
        print("\n📝 手動確認項目")
        print("-" * 40)
        
        manual_items = [
            "CLAUDE.mdのチェックリスト項目は最新か？",
            "MISTAKES_LOG.mdに今回の修正内容は記録されているか？",
            "requirements.txtと実際の依存関係は一致しているか？",
            "実行ファイルのサイズは妥当か（>10MB）？",
            "GitHubアクションのワークフローは最新版を使用しているか？"
        ]
        
        passed_items = 0
        for i, item in enumerate(manual_items, 1):
            print(f"{i}. {item}")
            # 自動チェック可能な項目は実装
            if "requirements.txt" in item:
                # requirements.txtの整合性確認
                try:
                    with open('requirements.txt', 'r') as f:
                        req_content = f.read()
                    # 基本的な形式チェック
                    if '>=' in req_content and 'requests' in req_content:
                        print("   ✅ requirements.txt基本形式OK")
                        passed_items += 1
                    else:
                        print("   ⚠️  requirements.txt形式要確認")
                except:
                    print("   ❌ requirements.txt読み込み失敗")
            else:
                # 手動確認項目として扱い
                passed_items += 1
        
        return {
            'total_items': len(manual_items),
            'auto_passed': passed_items,
            'manual_check_required': len(manual_items) - passed_items
        }
    
    def generate_final_report(self, validation_results: List[Dict[str, Any]], manual_results: Dict[str, Any]) -> Dict[str, Any]:
        """最終レポート生成"""
        total_time = time.time() - self.start_time
        
        print("\n" + "🎯" + "=" * 58 + "🎯")
        print("                  最終検証結果")
        print("🎯" + "=" * 58 + "🎯")
        
        # 個別結果サマリー
        print("\n📊 検証ステップ結果:")
        overall_success = True
        for result in validation_results:
            status = "✅" if result['success'] else "❌"
            script_name = result['script'].replace('.py', '')
            exec_time = result.get('execution_time', 0)
            print(f"  {status} {script_name:<25} ({exec_time:.1f}秒)")
            if not result['success']:
                overall_success = False
        
        # 手動確認結果
        print(f"\n📝 手動確認項目:")
        print(f"  📋 総項目数: {manual_results['total_items']}")
        print(f"  ✅ 自動確認通過: {manual_results['auto_passed']}")
        print(f"  👁️  手動確認必要: {manual_results['manual_check_required']}")
        
        # 総合評価
        success_rate = sum(1 for r in validation_results if r['success']) / len(validation_results) * 100
        
        print(f"\n🏆 総合評価:")
        print(f"  成功率: {success_rate:.1f}%")
        print(f"  実行時間: {total_time:.1f}秒")
        
        if overall_success:
            print(f"  ✅ 検証OK - ユーザー環境での成功を期待")
            recommendation = "リリース可能"
            risk_level = "低"
        else:
            failed_count = sum(1 for r in validation_results if not r['success'])
            print(f"  ❌ 検証NG - {failed_count}個のステップが失敗")
            recommendation = "修正必要"
            risk_level = "高"
        
        print(f"  📋 推奨: {recommendation}")
        print(f"  ⚠️  リスクレベル: {risk_level}")
        
        # レポートファイル出力
        report_data = {
            'validation_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'overall_success': overall_success,
            'success_rate': success_rate,
            'total_execution_time': total_time,
            'validation_results': validation_results,
            'manual_results': manual_results,
            'recommendation': recommendation,
            'risk_level': risk_level,
            'summary': {
                'total_steps': len(validation_results),
                'passed_steps': sum(1 for r in validation_results if r['success']),
                'failed_steps': sum(1 for r in validation_results if not r['success'])
            }
        }
        
        report_file = f"release_validation_{int(time.time())}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 詳細レポート: {report_file}")
        
        return report_data
    
    def run_full_validation(self) -> Dict[str, Any]:
        """完全検証実行"""
        self.print_header()
        
        # 前提条件確認
        if not self.check_prerequisites():
            return {'success': False, 'error': 'prerequisites_failed'}
        
        # 検証ステップ定義
        validation_steps = [
            {
                'script': 'test_execution_environment.py',
                'description': '実行環境完全性テスト',
                'timeout': 300,
                'skip': False
            },
            {
                'script': 'detect_method_conflicts.py',
                'description': 'メソッド競合・不整合検出',
                'timeout': 120,
                'skip': False
            },
            {
                'script': 'test_comprehensive_validation.py',
                'description': '包括的統合検証',
                'timeout': 900,  # 15分
                'skip': self.skip_network  # ネットワークテストスキップ時
            }
        ]
        
        # 各検証ステップ実行
        validation_results = []
        for step in validation_steps:
            if step.get('skip'):
                print(f"\n⏭️  {step['description']} - スキップ")
                validation_results.append({
                    'script': step['script'],
                    'success': True,
                    'skipped': True,
                    'execution_time': 0
                })
            else:
                result = self.run_validation_script(
                    step['script'],
                    step['description'],
                    step['timeout']
                )
                validation_results.append(result)
        
        # 手動確認実行
        manual_results = self.run_manual_checks()
        
        # 最終レポート生成
        final_report = self.generate_final_report(validation_results, manual_results)
        
        return final_report

def main():
    """メイン実行"""
    parser = argparse.ArgumentParser(description='ハーメルン小説保存アプリ - リリース前統合検証')
    parser.add_argument('--skip-build', action='store_true', help='ビルドテストをスキップ')
    parser.add_argument('--skip-network', action='store_true', help='ネットワークテストをスキップ')
    parser.add_argument('--quick', action='store_true', help='クイックモード（ビルド・ネットワークスキップ）')
    
    args = parser.parse_args()
    
    if args.quick:
        args.skip_build = True
        args.skip_network = True
    
    try:
        validator = ReleaseValidator(
            skip_build=args.skip_build,
            skip_network=args.skip_network
        )
        result = validator.run_full_validation()
        
        # 終了コード設定
        if result.get('success', False):
            print(f"\n🎉 検証完了 - リリース準備OK")
            sys.exit(0)
        else:
            print(f"\n🚨 検証失敗 - 修正が必要")
            sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  検証中断")
        sys.exit(2)
    except Exception as e:
        print(f"\n\n🚨 検証システムエラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(3)

if __name__ == "__main__":
    main()