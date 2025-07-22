#!/usr/bin/env python3
"""
包括的検証テストスクリプト
テスト成功→実際失敗問題を防ぐための最終検証システム
"""

import os
import sys
import json
import time
import tempfile
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Any
import traceback

class ComprehensiveValidator:
    """包括的検証システム"""
    
    def __init__(self):
        self.test_results = []
        self.validation_errors = []
        
    def log_validation(self, test_name: str, success: bool, details: str, critical: bool = False):
        """検証結果をログ"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'critical': critical,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        self.test_results.append(result)
        
        if not success:
            self.validation_errors.append(result)
        
        status = "✅ PASS" if success else ("🚨 FAIL" if critical else "⚠️  WARNING")
        print(f"{status} {test_name}: {details}")
    
    def run_execution_environment_test(self) -> bool:
        """実行環境テストを実行"""
        print("\n=== Step 1: 実行環境テスト ===")
        
        try:
            result = subprocess.run([
                sys.executable, 'test_execution_environment.py'
            ], capture_output=True, text=True, timeout=300)
            
            success = result.returncode == 0
            self.log_validation(
                "実行環境完全性",
                success,
                f"終了コード: {result.returncode}",
                critical=True
            )
            
            if not success:
                print("実行環境テスト出力:")
                print(result.stdout)
                if result.stderr:
                    print("エラー出力:")
                    print(result.stderr)
            
            return success
            
        except subprocess.TimeoutExpired:
            self.log_validation(
                "実行環境完全性",
                False,
                "テストタイムアウト（5分）",
                critical=True
            )
            return False
        except Exception as e:
            self.log_validation(
                "実行環境完全性",
                False,
                f"実行エラー: {e}",
                critical=True
            )
            return False
    
    def run_method_conflict_detection(self) -> bool:
        """メソッド競合検出を実行"""
        print("\n=== Step 2: メソッド競合検出 ===")
        
        try:
            result = subprocess.run([
                sys.executable, 'detect_method_conflicts.py'
            ], capture_output=True, text=True, timeout=120)
            
            success = result.returncode == 0
            self.log_validation(
                "メソッド競合検出",
                success,
                f"終了コード: {result.returncode}",
                critical=True
            )
            
            if not success:
                print("メソッド競合検出出力:")
                print(result.stdout)
                if result.stderr:
                    print("エラー出力:")
                    print(result.stderr)
            
            return success
            
        except subprocess.TimeoutExpired:
            self.log_validation(
                "メソッド競合検出",
                False,
                "検出タイムアウト（2分）",
                critical=True
            )
            return False
        except Exception as e:
            self.log_validation(
                "メソッド競合検出",
                False,
                f"実行エラー: {e}",
                critical=True
            )
            return False
    
    def test_gui_cli_consistency(self) -> bool:
        """GUI版とCLI版の一貫性テスト"""
        print("\n=== Step 3: GUI/CLI一貫性テスト ===")
        
        test_url = "https://syosetu.org/novel/380014/"
        
        try:
            # CLI版テスト（hameln_scraper_final.py）
            print("CLI版テスト中...")
            sys.path.insert(0, '.')
            
            from hameln_scraper_final import HamelnFinalScraper
            cli_scraper = HamelnFinalScraper()
            
            # 基本機能テスト
            cli_result = cli_scraper.get_page(test_url)
            cli_success = cli_result is not None
            
            if cli_success:
                cli_content_len = len(str(cli_result))
            else:
                cli_content_len = 0
            
            self.log_validation(
                "CLI版基本機能",
                cli_success,
                f"ページ取得: {cli_content_len}文字"
            )
            
            cli_scraper.close()
            
            # GUI版統合テスト（HamelnModularScraper）
            print("GUI版統合テスト中...")
            from hameln_scraper.core.scraper import HamelnModularScraper
            gui_scraper = HamelnModularScraper()
            
            gui_result = gui_scraper.get_page(test_url)
            gui_success = gui_result and gui_result.get('success', False)
            
            if gui_success:
                gui_content_len = len(gui_result.get('content', ''))
            else:
                gui_content_len = 0
            
            self.log_validation(
                "GUI版基本機能",
                gui_success,
                f"ページ取得: {gui_content_len}文字"
            )
            
            # 一貫性確認
            if cli_success and gui_success:
                content_diff = abs(cli_content_len - gui_content_len)
                consistency_ok = content_diff < 1000  # 1000文字以内の差異は許容
                
                self.log_validation(
                    "GUI/CLI一貫性",
                    consistency_ok,
                    f"コンテンツ長差異: {content_diff}文字",
                    critical=True
                )
            else:
                self.log_validation(
                    "GUI/CLI一貫性",
                    False,
                    "一方または両方が失敗",
                    critical=True
                )
            
            gui_scraper.close()
            
            return cli_success and gui_success
            
        except Exception as e:
            self.log_validation(
                "GUI/CLI一貫性テスト",
                False,
                f"例外: {e}",
                critical=True
            )
            return False
    
    def test_build_system(self) -> bool:
        """ビルドシステムテスト"""
        print("\n=== Step 4: ビルドシステムテスト ===")
        
        # 一時ディレクトリでビルドテスト
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # GUI版ビルドテスト
                print("GUI版ビルドテスト中...")
                gui_build_result = subprocess.run([
                    'pyinstaller', '--clean', '--distpath', temp_dir,
                    'HamelnNovelArchiverGUI.spec'
                ], capture_output=True, text=True, timeout=600)
                
                gui_build_success = gui_build_result.returncode == 0
                self.log_validation(
                    "GUI版ビルド",
                    gui_build_success,
                    f"終了コード: {gui_build_result.returncode}",
                    critical=True
                )
                
                # ビルド成果物確認
                if gui_build_success:
                    gui_exe_path = Path(temp_dir) / "HamelnNovelArchiverGUI"
                    if gui_exe_path.exists():
                        file_size = gui_exe_path.stat().st_size
                        size_ok = file_size > 10 * 1024 * 1024  # 10MB以上
                        
                        self.log_validation(
                            "GUI実行ファイル生成",
                            size_ok,
                            f"サイズ: {file_size / 1024 / 1024:.1f}MB",
                            critical=True
                        )
                    else:
                        self.log_validation(
                            "GUI実行ファイル生成",
                            False,
                            "実行ファイルが見つからない",
                            critical=True
                        )
                        gui_build_success = False
                
                # CUI版ビルドテスト
                print("CUI版ビルドテスト中...")
                cui_build_result = subprocess.run([
                    'pyinstaller', '--clean', '--distpath', temp_dir,
                    'HamelnNovelArchiverCUI.spec'
                ], capture_output=True, text=True, timeout=600)
                
                cui_build_success = cui_build_result.returncode == 0
                self.log_validation(
                    "CUI版ビルド",
                    cui_build_success,
                    f"終了コード: {cui_build_result.returncode}",
                    critical=True
                )
                
                return gui_build_success and cui_build_success
                
            except subprocess.TimeoutExpired:
                self.log_validation(
                    "ビルドシステム",
                    False,
                    "ビルドタイムアウト（10分）",
                    critical=True
                )
                return False
            except Exception as e:
                self.log_validation(
                    "ビルドシステム",
                    False,
                    f"ビルドエラー: {e}",
                    critical=True
                )
                return False
    
    def test_real_usage_scenario(self) -> bool:
        """実使用シナリオテスト"""
        print("\n=== Step 5: 実使用シナリオテスト ===")
        
        try:
            from hameln_scraper.core.scraper import HamelnModularScraper
            
            # 実際のワークフロー模擬
            scraper = HamelnModularScraper()
            test_url = "https://syosetu.org/novel/380014/"
            
            print(f"実使用テスト URL: {test_url}")
            
            # Step 1: ページ取得
            page_result = scraper.get_page(test_url)
            step1_success = page_result and page_result.get('success', False)
            
            self.log_validation(
                "実使用-ページ取得",
                step1_success,
                f"成功: {step1_success}",
                critical=True
            )
            
            if not step1_success:
                return False
            
            # Step 2: 小説情報抽出
            info_result = scraper.extract_novel_info(page_result['content'], test_url)
            step2_success = info_result and info_result.get('success', False)
            
            self.log_validation(
                "実使用-小説情報抽出",
                step2_success,
                f"タイトル: {info_result.get('title', 'N/A')}",
                critical=True
            )
            
            # Step 3: 章リンク取得
            links_result = scraper.get_chapter_links(page_result['content'], test_url)
            step3_success = links_result and links_result.get('success', False)
            chapter_count = len(links_result.get('chapter_links', []))
            
            self.log_validation(
                "実使用-章リンク取得",
                step3_success and chapter_count > 0,
                f"章数: {chapter_count}",
                critical=True
            )
            
            # Step 4: 第1章アクセステスト
            if step3_success and chapter_count > 0:
                first_chapter_url = links_result['chapter_links'][0]
                chapter_result = scraper.get_page(first_chapter_url)
                step4_success = chapter_result and chapter_result.get('success', False)
                
                self.log_validation(
                    "実使用-章ページアクセス",
                    step4_success,
                    f"第1章アクセス: {step4_success}",
                    critical=True
                )
            else:
                step4_success = False
                self.log_validation(
                    "実使用-章ページアクセス",
                    False,
                    "章リンク取得失敗により未実行",
                    critical=True
                )
            
            scraper.close()
            
            return step1_success and step2_success and step3_success and step4_success
            
        except Exception as e:
            self.log_validation(
                "実使用シナリオ",
                False,
                f"例外: {e}",
                critical=True
            )
            return False
    
    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """包括的検証実行"""
        print("🔍 包括的検証テスト開始")
        print("=" * 60)
        
        validation_steps = [
            ("実行環境テスト", self.run_execution_environment_test),
            ("メソッド競合検出", self.run_method_conflict_detection),
            ("GUI/CLI一貫性", self.test_gui_cli_consistency),
            ("ビルドシステム", self.test_build_system),
            ("実使用シナリオ", self.test_real_usage_scenario)
        ]
        
        overall_success = True
        step_results = {}
        
        for step_name, test_func in validation_steps:
            print(f"\n🔄 {step_name} 実行中...")
            try:
                step_success = test_func()
                step_results[step_name] = step_success
                if not step_success:
                    overall_success = False
                    print(f"❌ {step_name} 失敗")
                else:
                    print(f"✅ {step_name} 成功")
            except Exception as e:
                print(f"🚨 {step_name} 例外: {e}")
                step_results[step_name] = False
                overall_success = False
        
        return self.generate_validation_report(overall_success, step_results)
    
    def generate_validation_report(self, overall_success: bool, step_results: Dict[str, bool]) -> Dict[str, Any]:
        """検証レポート生成"""
        print("\n" + "=" * 60)
        print("📊 包括的検証結果サマリー")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['success'])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"全体成功: {'✅ YES' if overall_success else '❌ NO'}")
        print(f"総テスト数: {total_tests}")
        print(f"成功: {passed_tests}")
        print(f"失敗: {total_tests - passed_tests}")
        print(f"成功率: {success_rate:.1f}%")
        
        print(f"\nステップ別結果:")
        for step, success in step_results.items():
            status = "✅" if success else "❌"
            print(f"  {status} {step}")
        
        # 重大エラー表示
        critical_errors = [e for e in self.validation_errors if e.get('critical', False)]
        if critical_errors:
            print(f"\n🚨 重大エラー ({len(critical_errors)}件):")
            for error in critical_errors:
                print(f"  - {error['test']}: {error['details']}")
        
        # レポートファイル出力
        report_data = {
            'validation_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'overall_success': overall_success,
            'success_rate': success_rate,
            'step_results': step_results,
            'test_results': self.test_results,
            'validation_errors': self.validation_errors,
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'critical_errors': len(critical_errors)
            }
        }
        
        report_file = f"comprehensive_validation_{int(time.time())}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 詳細レポート: {report_file}")
        
        final_status = "✅ 検証OK - 実環境での成功を期待" if overall_success else "❌ 検証NG - 実環境失敗のリスク高"
        print(f"\n{final_status}")
        
        return {
            'success': overall_success,
            'success_rate': success_rate,
            'critical_errors': len(critical_errors),
            'report_file': report_file
        }

def main():
    """メイン実行"""
    try:
        validator = ComprehensiveValidator()
        result = validator.run_comprehensive_validation()
        
        # 終了コード設定
        exit_code = 0 if result['success'] else 1
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  検証中断")
        sys.exit(2)
    except Exception as e:
        print(f"\n\n🚨 検証実行エラー: {e}")
        traceback.print_exc()
        sys.exit(3)

if __name__ == "__main__":
    main()