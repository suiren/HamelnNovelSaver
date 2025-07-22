#!/usr/bin/env python3
"""
メソッド重複・不整合自動検出スクリプト
横展開ミス防止のための包括的コード分析
"""

import os
import ast
import re
import json
import time
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from collections import defaultdict
import traceback

class MethodConflictDetector:
    """メソッド重複・不整合検出器"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.method_definitions = defaultdict(list)
        self.class_methods = defaultdict(dict)
        self.function_signatures = {}
        self.conflicts = []
        self.inconsistencies = []
        
    def scan_python_files(self) -> List[Path]:
        """Python ファイルをスキャン"""
        python_files = []
        exclude_patterns = {
            '__pycache__', '.git', '.pytest_cache', 'build', 'dist',
            'venv', 'env', '.venv', 'node_modules', 'backup_original_files'
        }
        
        for py_file in self.root_dir.rglob("*.py"):
            # 除外パターンチェック
            if any(part in exclude_patterns for part in py_file.parts):
                continue
            python_files.append(py_file)
        
        return python_files
    
    def parse_file(self, file_path: Path) -> Dict[str, Any]:
        """ファイル解析してAST情報取得"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=str(file_path))
            return {
                'ast': tree,
                'content': content,
                'lines': content.split('\n')
            }
        except Exception as e:
            print(f"⚠️  ファイル解析エラー {file_path}: {e}")
            return None
    
    def extract_method_info(self, node: ast.FunctionDef, class_name: str, file_path: Path, lines: List[str]) -> Dict[str, Any]:
        """メソッド情報を抽出"""
        # 引数情報
        args = []
        for arg in node.args.args:
            args.append(arg.arg)
        
        # 戻り値アノテーション
        return_annotation = None
        if node.returns:
            return_annotation = ast.unparse(node.returns) if hasattr(ast, 'unparse') else str(node.returns)
        
        # メソッド本体の最初の数行を取得
        start_line = node.lineno - 1
        end_line = min(start_line + 10, len(lines))
        body_preview = '\n'.join(lines[start_line:end_line])
        
        # return 文の抽出
        return_statements = []
        for child in ast.walk(node):
            if isinstance(child, ast.Return) and child.value:
                try:
                    return_stmt = ast.unparse(child.value) if hasattr(ast, 'unparse') else str(child.value)
                    return_statements.append(return_stmt)
                except:
                    return_statements.append("<complex_return>")
        
        return {
            'name': node.name,
            'class_name': class_name,
            'file_path': str(file_path),
            'line_number': node.lineno,
            'args': args,
            'return_annotation': return_annotation,
            'return_statements': return_statements,
            'body_preview': body_preview,
            'is_property': any(isinstance(d, ast.Name) and d.id == 'property' for d in node.decorator_list),
            'is_staticmethod': any(isinstance(d, ast.Name) and d.id == 'staticmethod' for d in node.decorator_list),
            'is_classmethod': any(isinstance(d, ast.Name) and d.id == 'classmethod' for d in node.decorator_list)
        }
    
    def analyze_file(self, file_path: Path) -> None:
        """単一ファイルを分析"""
        file_info = self.parse_file(file_path)
        if not file_info:
            return
        
        tree = file_info['ast']
        lines = file_info['lines']
        
        # クラス内のメソッドを分析
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name
                
                for child in node.body:
                    if isinstance(child, ast.FunctionDef):
                        method_info = self.extract_method_info(child, class_name, file_path, lines)
                        
                        # メソッド定義を記録
                        method_key = f"{class_name}.{child.name}"
                        self.method_definitions[method_key].append(method_info)
                        
                        # クラス内メソッド情報を記録
                        if class_name not in self.class_methods:
                            self.class_methods[class_name] = {}
                        self.class_methods[class_name][child.name] = method_info
            
            # モジュールレベルの関数を分析
            elif isinstance(node, ast.FunctionDef):
                function_info = self.extract_method_info(node, None, file_path, lines)
                self.function_signatures[f"{file_path.stem}.{node.name}"] = function_info
    
    def detect_method_conflicts(self) -> None:
        """メソッド重複を検出"""
        print("\n🔍 メソッド重複検出中...")
        
        for method_key, definitions in self.method_definitions.items():
            if len(definitions) > 1:
                # 同一クラス内での重複
                same_class_defs = [d for d in definitions if d['class_name'] == definitions[0]['class_name']]
                if len(same_class_defs) > 1:
                    self.conflicts.append({
                        'type': 'method_redefinition',
                        'method': method_key,
                        'severity': 'critical',
                        'descriptions': same_class_defs,
                        'message': f"同一クラス内でメソッド '{method_key}' が重複定義されています"
                    })
                
                # 異なるファイルでの同名メソッド（潜在的な問題）
                file_groups = defaultdict(list)
                for definition in definitions:
                    file_groups[definition['file_path']].append(definition)
                
                if len(file_groups) > 1:
                    self.conflicts.append({
                        'type': 'cross_file_method_name',
                        'method': method_key,
                        'severity': 'warning',
                        'descriptions': definitions,
                        'message': f"複数ファイルで同名メソッド '{method_key}' が定義されています"
                    })
    
    def detect_return_type_inconsistencies(self) -> None:
        """戻り値型の不整合を検出"""
        print("\n🔍 戻り値型不整合検出中...")
        
        # 同名メソッドの戻り値型比較
        for method_key, definitions in self.method_definitions.items():
            if len(definitions) < 2:
                continue
            
            return_types = set()
            return_patterns = set()
            
            for definition in definitions:
                # アノテーション型
                if definition['return_annotation']:
                    return_types.add(definition['return_annotation'])
                
                # 実際のreturn文パターン分析
                for ret_stmt in definition['return_statements']:
                    if 'dict' in ret_stmt or '{' in ret_stmt:
                        return_patterns.add('dict')
                    elif 'BeautifulSoup' in ret_stmt or 'soup' in ret_stmt:
                        return_patterns.add('BeautifulSoup')
                    elif 'None' in ret_stmt:
                        return_patterns.add('None')
                    elif 'str(' in ret_stmt or 'f"' in ret_stmt or "'" in ret_stmt:
                        return_patterns.add('str')
                    elif 'list(' in ret_stmt or '[' in ret_stmt:
                        return_patterns.add('list')
            
            # 不整合チェック
            if len(return_types) > 1 or len(return_patterns) > 1:
                self.inconsistencies.append({
                    'type': 'return_type_inconsistency',
                    'method': method_key,
                    'severity': 'high',
                    'return_types': list(return_types),
                    'return_patterns': list(return_patterns),
                    'definitions': definitions,
                    'message': f"メソッド '{method_key}' の戻り値型が不整合です"
                })
    
    def detect_get_page_issues(self) -> None:
        """get_pageメソッド特有の問題を検出"""
        print("\n🔍 get_pageメソッド特有問題検出中...")
        
        get_page_methods = [
            (key, defs) for key, defs in self.method_definitions.items() 
            if 'get_page' in key
        ]
        
        if not get_page_methods:
            return
        
        # get_pageメソッドの詳細分析
        for method_key, definitions in get_page_methods:
            for definition in definitions:
                body = definition['body_preview']
                
                # kwargs使用パターン検出
                if '**kwargs' in definition['args']:
                    self.inconsistencies.append({
                        'type': 'get_page_kwargs_usage',
                        'method': method_key,
                        'severity': 'medium',
                        'file': definition['file_path'],
                        'line': definition['line_number'],
                        'message': f"get_pageメソッドで**kwargsが使用されています（潜在的オーバーライド問題）"
                    })
                
                # 直接return パターン検出
                if 'return self.network_client.get_page' in body:
                    self.inconsistencies.append({
                        'type': 'get_page_direct_delegation',
                        'method': method_key,
                        'severity': 'high',
                        'file': definition['file_path'],
                        'line': definition['line_number'],
                        'message': f"get_pageメソッドが直接network_clientに委譲しています（戻り値型不整合の可能性）"
                    })
    
    def detect_url_processing_inconsistencies(self) -> None:
        """URL処理の不整合を検出"""
        print("\n🔍 URL処理不整合検出中...")
        
        url_processing_patterns = {
            'urljoin': [],
            'relative_to_absolute': [],
            'url_validation': []
        }
        
        for method_key, definitions in self.method_definitions.items():
            for definition in definitions:
                body = definition['body_preview'].lower()
                
                if 'urljoin' in body:
                    url_processing_patterns['urljoin'].append((method_key, definition))
                
                if 'href' in body and ('relative' in body or './' in body):
                    url_processing_patterns['relative_to_absolute'].append((method_key, definition))
                
                if 'startswith(\'http' in body or 'http://' in body:
                    url_processing_patterns['url_validation'].append((method_key, definition))
        
        # パターン不整合の検出
        for pattern_type, methods in url_processing_patterns.items():
            if len(methods) > 1:
                # 実装の一貫性チェック
                implementations = set()
                for method_key, definition in methods:
                    # 簡単な実装パターン抽出
                    body = definition['body_preview']
                    if 'urljoin(base_novel_url, href)' in body:
                        implementations.add('base_novel_url_pattern')
                    elif 'urljoin(base_url, href)' in body:
                        implementations.add('base_url_pattern')
                    else:
                        implementations.add('custom_pattern')
                
                if len(implementations) > 1:
                    self.inconsistencies.append({
                        'type': f'url_processing_{pattern_type}_inconsistency',
                        'severity': 'medium',
                        'implementations': list(implementations),
                        'methods': [m[0] for m in methods],
                        'message': f"URL処理パターン '{pattern_type}' の実装が不整合です"
                    })
    
    def generate_report(self) -> Dict[str, Any]:
        """検出結果レポート生成"""
        print("\n" + "=" * 60)
        print("📊 メソッド競合・不整合検出結果")
        print("=" * 60)
        
        total_issues = len(self.conflicts) + len(self.inconsistencies)
        
        print(f"検出された問題数: {total_issues}")
        print(f"メソッド重複: {len(self.conflicts)}")
        print(f"実装不整合: {len(self.inconsistencies)}")
        
        # 重大な問題の表示
        critical_issues = [c for c in self.conflicts if c['severity'] == 'critical']
        if critical_issues:
            print(f"\n🚨 重大な問題 ({len(critical_issues)}件):")
            for issue in critical_issues:
                print(f"  - {issue['message']}")
                for desc in issue['descriptions']:
                    print(f"    📍 {desc['file_path']}:{desc['line_number']}")
        
        # 高優先度の不整合
        high_priority = [i for i in self.inconsistencies if i['severity'] == 'high']
        if high_priority:
            print(f"\n⚠️  高優先度不整合 ({len(high_priority)}件):")
            for issue in high_priority:
                print(f"  - {issue['message']}")
                if 'file' in issue:
                    print(f"    📍 {issue['file']}:{issue['line']}")
        
        # レポートファイル出力
        report_data = {
            'scan_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_issues': total_issues,
            'conflicts': self.conflicts,
            'inconsistencies': self.inconsistencies,
            'method_definitions_count': {k: len(v) for k, v in self.method_definitions.items()},
            'summary': {
                'critical_issues': len(critical_issues),
                'high_priority_issues': len(high_priority),
                'total_methods_scanned': len(self.method_definitions)
            }
        }
        
        report_file = f"method_conflicts_report_{int(time.time())}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 詳細レポート: {report_file}")
        
        return {
            'success': total_issues == 0,
            'total_issues': total_issues,
            'critical_issues': len(critical_issues),
            'report_file': report_file
        }
    
    def run_analysis(self) -> Dict[str, Any]:
        """包括的分析実行"""
        print("🔍 メソッド競合・不整合検出開始")
        print("=" * 60)
        
        # Python ファイルスキャン
        python_files = self.scan_python_files()
        print(f"📁 スキャン対象: {len(python_files)} ファイル")
        
        # 各ファイルを分析
        for file_path in python_files:
            self.analyze_file(file_path)
        
        print(f"📊 検出されたメソッド定義: {len(self.method_definitions)}")
        
        # 問題検出
        self.detect_method_conflicts()
        self.detect_return_type_inconsistencies()
        self.detect_get_page_issues()
        self.detect_url_processing_inconsistencies()
        
        return self.generate_report()

def main():
    """メイン実行"""
    try:
        detector = MethodConflictDetector()
        result = detector.run_analysis()
        
        # 終了コード設定
        exit_code = 0 if result['success'] else 1
        print(f"\n{'✅ 検出問題なし' if result['success'] else '❌ 問題検出'}")
        return exit_code
        
    except KeyboardInterrupt:
        print("\n\n⏹️  分析中断")
        return 2
    except Exception as e:
        print(f"\n\n🚨 分析実行エラー: {e}")
        traceback.print_exc()
        return 3

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)