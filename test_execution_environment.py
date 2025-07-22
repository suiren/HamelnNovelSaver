#!/usr/bin/env python3
"""
実行環境完全テストスクリプト
テスト成功→実際失敗問題を防ぐための包括的検証
"""

import os
import sys
import platform
import subprocess
import tempfile
import shutil
import time
from pathlib import Path
from typing import Dict, List, Tuple, Any
import traceback

class ExecutionEnvironmentTester:
    """実行環境の完全性テスト"""
    
    def __init__(self):
        self.test_results = []
        self.critical_failures = []
        self.warnings = []
        
    def log_result(self, test_name: str, success: bool, details: str, critical: bool = False):
        """テスト結果をログ"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'critical': critical,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        self.test_results.append(result)
        
        if not success:
            if critical:
                self.critical_failures.append(result)
            else:
                self.warnings.append(result)
        
        status = "✅ PASS" if success else ("🚨 CRITICAL FAIL" if critical else "⚠️  WARNING")
        print(f"{status} {test_name}: {details}")
    
    def test_python_environment(self) -> bool:
        """Python実行環境テスト"""
        print("\n=== Python実行環境テスト ===")
        
        # Python版本確認
        py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        self.log_result(
            "Python版本", 
            sys.version_info >= (3, 8), 
            f"Version: {py_version} (Required: 3.8+)",
            critical=True
        )
        
        # プラットフォーム情報
        platform_info = f"{platform.system()} {platform.release()} ({platform.machine()})"
        self.log_result(
            "プラットフォーム", 
            True, 
            platform_info
        )
        
        # 重要モジュール存在確認
        required_modules = [
            'requests', 'beautifulsoup4', 'lxml', 'cloudscraper', 
            'selenium', 'PIL', 'brotli', 'tkinter'
        ]
        
        for module in required_modules:
            try:
                if module == 'beautifulsoup4':
                    import bs4
                    version = getattr(bs4, '__version__', 'unknown')
                elif module == 'PIL':
                    from PIL import Image
                    version = getattr(Image, '__version__', 'unknown')
                else:
                    imported = __import__(module)
                    version = getattr(imported, '__version__', 'unknown')
                
                self.log_result(
                    f"モジュール {module}",
                    True,
                    f"Version: {version}",
                    critical=True
                )
            except ImportError as e:
                self.log_result(
                    f"モジュール {module}",
                    False,
                    f"ImportError: {e}",
                    critical=True
                )
        
        return len(self.critical_failures) == 0
    
    def test_file_structure(self) -> bool:
        """ファイル構造完全性テスト"""
        print("\n=== ファイル構造完全性テスト ===")
        
        # 重要ファイルの存在確認
        critical_files = [
            'hameln_gui.py',
            'hameln_scraper_final.py',
            'requirements.txt',
            'HamelnNovelArchiverGUI.spec',
            'HamelnNovelArchiverCUI.spec'
        ]
        
        for file_path in critical_files:
            exists = os.path.exists(file_path)
            self.log_result(
                f"重要ファイル {file_path}",
                exists,
                "存在" if exists else "不存在",
                critical=True
            )
        
        # hameln_scraperモジュール構造確認
        module_paths = [
            'hameln_scraper/__init__.py',
            'hameln_scraper/core/scraper.py',
            'hameln_scraper/core/config.py',
            'hameln_scraper/network/client.py',
            'hameln_scraper/parsing/url_extractor.py',
            'hameln_scraper/resources/saver.py'
        ]
        
        for path in module_paths:
            exists = os.path.exists(path)
            self.log_result(
                f"モジュール {path}",
                exists,
                "存在" if exists else "不存在",
                critical=True
            )
        
        return len(self.critical_failures) == 0
    
    def test_import_functionality(self) -> bool:
        """インポート機能テスト"""
        print("\n=== インポート機能テスト ===")
        
        # 重要クラスのインポートテスト
        import_tests = [
            ('hameln_scraper.core.scraper', 'HamelnModularScraper'),
            ('hameln_scraper.core.config', 'HamelnConfig'),
            ('hameln_scraper.network.client', 'HamelnNetworkClient'),
            ('hameln_scraper.parsing.url_extractor', 'UrlExtractor'),
            ('hameln_scraper.resources.saver', 'PageSaver')
        ]
        
        for module_name, class_name in import_tests:
            try:
                module = __import__(module_name, fromlist=[class_name])
                cls = getattr(module, class_name)
                # 簡単なインスタンス化テスト
                if class_name == 'HamelnModularScraper':
                    instance = cls()
                    has_required_methods = all(hasattr(instance, method) for method in ['get_page', 'scrape_novel'])
                else:
                    has_required_methods = True
                
                self.log_result(
                    f"インポート {module_name}.{class_name}",
                    has_required_methods,
                    "成功" if has_required_methods else "メソッド不足",
                    critical=True
                )
            except Exception as e:
                self.log_result(
                    f"インポート {module_name}.{class_name}",
                    False,
                    f"Error: {e}",
                    critical=True
                )
        
        return len(self.critical_failures) == 0
    
    def test_network_access(self) -> bool:
        """ネットワークアクセステスト"""
        print("\n=== ネットワークアクセステスト ===")
        
        try:
            from hameln_scraper.core.scraper import HamelnModularScraper
            scraper = HamelnModularScraper()
            
            # 実際のハーメルンサイトアクセステスト
            test_url = "https://syosetu.org/novel/380014/"
            print(f"テストURL: {test_url}")
            
            start_time = time.time()
            result = scraper.get_page(test_url)
            access_time = time.time() - start_time
            
            if result and result.get('success'):
                content_length = len(result.get('content', ''))
                self.log_result(
                    "ハーメルンアクセス",
                    True,
                    f"成功 - {content_length}文字 ({access_time:.2f}秒)",
                    critical=True
                )
                
                # 小説情報抽出テスト
                info_result = scraper.extract_novel_info(result['content'], test_url)
                self.log_result(
                    "小説情報抽出",
                    info_result.get('success', False),
                    f"タイトル: {info_result.get('title', 'N/A')}",
                    critical=True
                )
                
                # 章リンク取得テスト
                links_result = scraper.get_chapter_links(result['content'], test_url)
                chapter_count = len(links_result.get('chapter_links', []))
                self.log_result(
                    "章リンク取得",
                    links_result.get('success', False),
                    f"{chapter_count}章取得",
                    critical=True
                )
            else:
                error_msg = result.get('error', '不明エラー') if result else 'None応答'
                self.log_result(
                    "ハーメルンアクセス",
                    False,
                    f"失敗: {error_msg}",
                    critical=True
                )
            
            scraper.close()
            
        except Exception as e:
            self.log_result(
                "ネットワークテスト",
                False,
                f"Exception: {e}",
                critical=True
            )
        
        return len(self.critical_failures) == 0
    
    def test_build_capability(self) -> bool:
        """ビルド機能テスト"""
        print("\n=== ビルド機能テスト ===")
        
        # PyInstaller存在確認
        try:
            result = subprocess.run(['pyinstaller', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version = result.stdout.strip()
                self.log_result(
                    "PyInstaller",
                    True,
                    f"Version: {version}"
                )
            else:
                self.log_result(
                    "PyInstaller",
                    False,
                    "実行失敗",
                    critical=True
                )
        except subprocess.TimeoutExpired:
            self.log_result("PyInstaller", False, "タイムアウト", critical=True)
        except FileNotFoundError:
            self.log_result("PyInstaller", False, "未インストール", critical=True)
        
        # スペックファイル構文確認
        spec_files = ['HamelnNovelArchiverGUI.spec', 'HamelnNovelArchiverCUI.spec']
        for spec_file in spec_files:
            if os.path.exists(spec_file):
                try:
                    with open(spec_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    # 基本的な構文チェック
                    has_analysis = 'Analysis(' in content
                    has_exe = 'EXE(' in content
                    self.log_result(
                        f"スペックファイル {spec_file}",
                        has_analysis and has_exe,
                        "構文OK" if has_analysis and has_exe else "構文問題",
                        critical=True
                    )
                except Exception as e:
                    self.log_result(
                        f"スペックファイル {spec_file}",
                        False,
                        f"読み込みエラー: {e}",
                        critical=True
                    )
        
        return len(self.critical_failures) == 0
    
    def test_gui_functionality(self) -> bool:
        """GUI機能テスト（非対話式）"""
        print("\n=== GUI機能テスト ===")
        
        try:
            # GUI関連モジュールのインポートテスト
            import tkinter as tk
            self.log_result(
                "tkinter",
                True,
                "インポート成功"
            )
            
            # HamelnGUIクラスの基本構造テスト
            sys.path.insert(0, '.')
            from hameln_gui import HamelnGUI
            
            # 基本メソッド存在確認
            required_methods = ['create_widgets', 'start_download', 'download_novel']
            has_all_methods = all(hasattr(HamelnGUI, method) for method in required_methods)
            
            self.log_result(
                "HamelnGUIクラス",
                has_all_methods,
                "必要メソッド存在" if has_all_methods else "メソッド不足",
                critical=True
            )
            
        except ImportError as e:
            self.log_result(
                "GUI機能",
                False,
                f"インポートエラー: {e}",
                critical=True
            )
        except Exception as e:
            self.log_result(
                "GUI機能",
                False,
                f"エラー: {e}",
                critical=True
            )
        
        return len(self.critical_failures) == 0
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """包括的テスト実行"""
        print("🔍 実行環境完全性テスト開始")
        print("=" * 60)
        
        test_phases = [
            ("Python実行環境", self.test_python_environment),
            ("ファイル構造", self.test_file_structure),
            ("インポート機能", self.test_import_functionality),
            ("ネットワークアクセス", self.test_network_access),
            ("ビルド機能", self.test_build_capability),
            ("GUI機能", self.test_gui_functionality)
        ]
        
        overall_success = True
        for phase_name, test_func in test_phases:
            try:
                phase_success = test_func()
                if not phase_success:
                    overall_success = False
            except Exception as e:
                self.log_result(
                    f"{phase_name} (例外)",
                    False,
                    f"予期せぬエラー: {e}",
                    critical=True
                )
                overall_success = False
        
        return self.generate_report(overall_success)
    
    def generate_report(self, overall_success: bool) -> Dict[str, Any]:
        """テストレポート生成"""
        print("\n" + "=" * 60)
        print("📊 実行環境テスト結果サマリー")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['success'])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"総テスト数: {total_tests}")
        print(f"成功: {passed_tests}")
        print(f"失敗: {total_tests - passed_tests}")
        print(f"成功率: {success_rate:.1f}%")
        
        if self.critical_failures:
            print(f"\n🚨 重大な問題 ({len(self.critical_failures)}件):")
            for failure in self.critical_failures:
                print(f"  - {failure['test']}: {failure['details']}")
        
        if self.warnings:
            print(f"\n⚠️  警告 ({len(self.warnings)}件):")
            for warning in self.warnings:
                print(f"  - {warning['test']}: {warning['details']}")
        
        final_status = "✅ 実行環境OK" if overall_success else "❌ 実行環境に問題"
        print(f"\n{final_status}")
        
        # 詳細レポートファイル出力
        report_file = f"execution_environment_test_{int(time.time())}.json"
        import json
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                'overall_success': overall_success,
                'success_rate': success_rate,
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'critical_failures': len(self.critical_failures),
                'warnings': len(self.warnings),
                'test_results': self.test_results,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 詳細レポート: {report_file}")
        
        return {
            'success': overall_success,
            'success_rate': success_rate,
            'critical_failures': len(self.critical_failures),
            'report_file': report_file
        }

def main():
    """メイン実行"""
    try:
        tester = ExecutionEnvironmentTester()
        result = tester.run_comprehensive_test()
        
        # 終了コード設定
        exit_code = 0 if result['success'] else 1
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  テスト中断")
        sys.exit(2)
    except Exception as e:
        print(f"\n\n🚨 テスト実行エラー: {e}")
        traceback.print_exc()
        sys.exit(3)

if __name__ == "__main__":
    main()