# 🚀 ハーメルン小説保存アプリ - CI/CDワークフローガイド

## 📋 **ワークフロー概要**

**名前**: `🚀 ハーメルン小説保存アプリ - 自動テスト・ビルド・配布`

**目的**: ハーメルン小説保存アプリケーションの品質保証と自動配布

**実行タイミング**:
- mainブランチへのプッシュ時
- プルリクエスト作成時
- 手動実行（workflow_dispatch）

---

## 🔄 **実行フロー（7段階）**

### **1. 🧪 単体テスト（感想ページ複数取得機能）**
- **目的**: 感想ページの複数ページ取得機能をテスト
- **内容**: pytest実行、URL変換ロジック検証
- **成果物**: テスト結果レポート（HTML・JSON）

### **2. 🌐 機能テスト（URL変換・ページネーション）**
- **目的**: ページネーション検出機能の実機能テスト
- **内容**: 実際のURL変換処理とページ検出ロジック検証
- **成果物**: 機能テスト結果

### **3. 🔗 統合テスト（実際のハーメルンサイト接続）**
- **目的**: 実際のハーメルンサイトでの動作確認
- **内容**: ライブサイト接続、感想ページ取得テスト
- **成果物**: 統合テスト結果 + 実際のダウンロードファイル

### **4. 🏗️ 実行ファイルビルド（Windows・Linux対応）**
- **目的**: PyInstallerで配布用実行ファイル作成
- **内容**: HamelnBookDownloader.specでビルド実行
- **成果物**: 実行ファイル（HamelnBookDownloader）

### **5. 🚀 実行ファイル動作テスト**
- **目的**: ビルドした実行ファイルの動作確認
- **内容**: 実行可能性と基本機能の動作検証
- **成果物**: 実行ファイルテスト結果

### **6. 🎯 完全統合テスト（小説フルダウンロード検証）**
- **目的**: エンドツーエンドでの完全なダウンロードテスト
- **内容**: 実際の小説の完全ダウンロードと感想複数ページ統合確認
- **実行条件**: mainプッシュ時または手動実行時のみ
- **成果物**: 完全テスト結果 + フルダウンロードファイル

### **7. 📋 テスト結果サマリー**
- **目的**: 全テスト結果の統合レポート生成
- **内容**: 各段階の成功/失敗状況、テスト対象機能、生成物一覧
- **成果物**: マークダウン形式の総合レポート

---

## 📦 **生成される成果物（Artifacts）**

| Artifact名 | 内容 | 用途 |
|------------|------|------|
| `test-results` | 単体テスト結果（HTML・JSON） | デバッグ・品質確認 |
| `functional-test-results` | 機能テスト結果 | 機能検証 |
| `integration-test-results` | 統合テスト結果 + ダウンロードファイル | ライブ動作確認 |
| `HamelnBookDownloader-[hash]` | 実行ファイル | ユーザー配布用 |
| `executable-test-results` | 実行ファイルテスト結果 | 配布前検証 |
| `full-integration-test-results` | 完全テスト結果 + フルダウンロード | エンドツーエンド確認 |
| `test-summary-report` | 総合レポート | 全体状況把握 |

---

## 🎯 **キー機能のテスト内容**

### **感想ページ複数取得機能**
- URL変換処理（相対→絶対URL）
- ページネーション検出
- 複数ページ統合処理
- 「統合表示」マーカー確認

### **実行ファイル配布**
- クロスプラットフォーム対応
- 依存関係の完全パッケージング
- 実際の動作確認

### **品質保証**
- コード品質（pytest）
- 実機能動作（ライブサイト）
- エンドツーエンド（完全ダウンロード）

---

## 🔧 **トラブルシューティング**

### **ワークフロー失敗時の確認項目**
1. **依存関係**: requirements.txt更新確認
2. **ファイル管理**: git管理下ファイル確認
3. **サイト接続**: ハーメルンサイトのアクセス可否
4. **ビルド環境**: PyInstaller・specファイル確認

### **Artifacts確認方法**
1. GitHub → Actions → 該当ワークフロー実行をクリック
2. 下部の「Artifacts」セクションから各成果物をダウンロード
3. テスト結果やダウンロードファイルを確認

---

## 📈 **継続的改善**

このワークフローは以下の目的で継続的に改善されています：
- **品質向上**: より包括的なテスト追加
- **効率化**: 実行時間短縮・リソース最適化  
- **ユーザビリティ**: より分かりやすい結果表示