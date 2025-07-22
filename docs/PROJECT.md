# 🏗️ **プロジェクト設計書**

> **ハーメルン小説保存アプリケーション** の技術設計・アーキテクチャ詳細

---

## 🎯 **プロジェクト概要**

### **Mission Statement**
ハーメルン（https://syosetu.org）で公開されている二次創作小説を、**完全なオフライン閲覧環境**として保存し、元のWebサイトと同等のユーザー体験を提供すること。

### **Core Values**
1. **完全性**: 元の見た目・機能を100%再現
2. **安全性**: サイトに負荷をかけない適切なアクセス
3. **使いやすさ**: GUI/CUI両対応の直感的操作
4. **保守性**: モジュラー設計による拡張・改良容易性

---

## 🏛️ **システムアーキテクチャ**

### **全体構成図**
```
ハーメルンサイト
       ↓ (Cloudflare認証・bot検知回避)
    Network Layer
       ↓ (HTML/CSS/JS/画像取得)
    Parsing Layer  
       ↓ (構造解析・データ抽出)
    Processing Layer
       ↓ (ローカライズ・リンク修正)
    Output Layer
       ↓
  ローカルHTML環境
```

### **技術スタック**

#### **Core Technologies**
- **Python 3.8+**: メイン開発言語
- **cloudscraper**: Cloudflare認証突破
- **undetected-chromedriver**: 高度なbot検知回避
- **BeautifulSoup4**: HTML解析・操作
- **tkinter**: GUI フレームワーク

#### **Phase3 追加技術**
- **JavaScript ES6**: 動的感想機能
- **JSON**: 構造化データ保存
- **CSS**: 動的スタイル適用

---

## 📦 **モジュール構成**

### **パッケージ階層**
```
hameln_scraper/
├── core/
│   ├── __init__.py
│   ├── config.py          # 設定管理
│   └── scraper.py         # メインスクレイパー
├── network/
│   ├── __init__.py  
│   ├── client.py          # HTTP通信管理
│   ├── compression.py     # データ圧縮処理
│   └── user_agent.py      # User-Agent管理
├── parsing/
│   ├── __init__.py
│   ├── content_extractor.py # 本文抽出
│   ├── url_extractor.py    # URL抽出・変換  
│   └── validator.py        # データ検証
├── resources/
│   ├── __init__.py
│   ├── downloader.py      # リソースダウンロード
│   ├── file_manager.py    # ファイル管理
│   ├── processor.py       # リソース処理
│   └── saver.py           # 保存機能
└── comments/
    ├── __init__.py
    └── handler.py         # 感想処理
```

### **エントリーポイント**
- **hameln_gui.py**: GUI版メインプログラム
- **hameln_scraper_final.py**: CUI版メインプログラム

---

## 🔧 **技術設計**

### **1. Network Layer (通信層)**

#### **Cloudflare回避戦略**
```python
class NetworkClient:
    - CloudScraper: 基本認証突破
    - undetected_chromedriver: 高度検知回避
    - User-Agent rotation: 5種類ローテーション
    - Adaptive delays: 失敗時段階的延長
```

#### **アクセス制御**
- **基本間隔**: 3-8秒 (章数に応じて調整)
- **失敗時間隔**: 5-30秒段階的延長
- **最大再試行**: 3回
- **適応的待機**: レスポンス時間に基づく調整

### **2. Parsing Layer (解析層)**

#### **HTML構造対応**
```python
# 2024年版ハーメルン対応セレクター
CONTENT_SELECTORS = [
    'div.section1', 'div.section2', ..., 'div.section9',  # 主要本文
    'div.p-novel-text', 'div.novel-text',                  # 新形式
    'div.ss'  # 実際の構造 (AI想定vs実際の差異を解決)
]
```

#### **データ抽出方式**
- **優先順位型**: 特化セレクター → 汎用セレクター
- **フォールバック**: 最長テキスト自動選択
- **検証機能**: 抽出データの品質確認

### **3. Processing Layer (処理層)**

#### **ローカライズ処理**
```python
def localize_content():
    1. 外部URL → ローカルファイルパス変換
    2. 相対パス調整 (フォルダ構造対応)
    3. リソース参照修正 (CSS/JS/画像)
    4. クロスリンク生成 (目次↔章↔感想↔情報)
```

#### **Phase3: 動的機能処理**
```javascript
class CommentsFilter {
    loadCommentsData()     // JSONデータ読み込み
    applyFiltersAndSort()  // 14種類ソート・フィルター
    renderComments()       // 動的HTML生成
    updateSidebarCounts()  // カウント更新
}
```

### **4. Output Layer (出力層)**

#### **ファイル構成**
```
保存フォルダ/
├── 目次.html                    # メインナビゲーション
├── 第001話.html, 第002話.html  # 各章
├── 片田舎の剣聖 錬鉄の英霊 - 小説情報.html
├── 感想/
│   ├── 感想 - ページ1.html
│   ├── 感想 - ページ2.html
│   ├── comments_data.json      # Phase3: 感想データ
│   ├── comments_filter.js      # Phase3: 動的機能
│   └── resources/              # CSS/JS/画像
└── resources/                  # 共有リソース
```

---

## 🔄 **データフロー**

### **基本処理フロー**
```
1. URL入力 → 2. ハーメルンアクセス → 3. Cloudflare認証
    ↓
4. メインページ取得 → 5. 章リスト抽出 → 6. 章別アクセス
    ↓  
7. 本文抽出 → 8. リソースダウンロード → 9. ローカライズ
    ↓
10. 感想取得 → 11. 小説情報取得 → 12. クロスリンク生成
    ↓
13. Phase3: 動的機能統合 → 14. 最終出力
```

### **Phase3 拡張フロー**
```
感想HTML → BeautifulSoup解析 → JSON構造化
    ↓
JavaScript動的機能 → HTML統合 → フォールバック機能
```

---

## 🛡️ **品質保証**

### **テスト戦略**

#### **テストレベル**
1. **Unit Test**: 個別モジュールテスト
2. **Integration Test**: モジュール間連携テスト  
3. **E2E Test**: 実ハーメルンサイトでの動作確認
4. **User Acceptance Test**: 実際のブラウザでの確認

#### **テストダブル使用指針**
- **Mock使用**: 基本ロジックの高速検証のみ
- **実環境優先**: ハーメルン特化機能は必ず実サイトで確認
- **品質基準**: テスト成功率100%（99%でも失敗扱い）

### **品質メトリクス**
- **コード削減率**: Phase2で70%削減達成
- **テスト成功率**: A+評価（100点/100点）
- **パフォーマンス**: Phase3で26.4KB追加のみ

---

## 🔐 **セキュリティ・法的配慮**

### **アクセス制御**
- **適切な間隔**: サーバー負荷軽減
- **失敗時バックオフ**: 段階的アクセス間隔延長
- **User-Agent偽装**: 適切なブラウザ模擬

### **法的コンプライアンス**
- **個人使用限定**: 著作権法準拠
- **利用規約遵守**: ハーメルン利用規約に準拠
- **再配布禁止**: 保存データの商用利用禁止

---

## 📈 **パフォーマンス設計**

### **最適化戦略**
- **モジュラー設計**: 必要な機能のみ読み込み
- **リソース効率**: 重複ダウンロード回避
- **メモリ管理**: 大容量ファイル処理の最適化

### **スケーラビリティ**
- **大量感想対応**: 100件以上での性能維持
- **複数小説対応**: バッチ処理機能
- **拡張可能性**: 他サイト対応の基盤設計

---

## 🔄 **進化の歴史**

### **アーキテクチャ進化**
```
Phase1: モノリシック設計 (1000行)
   ↓ (リファクタリング)
Phase2: モジュラー設計 (700行, 70%削減)
   ↓ (動的機能追加)
Phase3: ハイブリッド設計 (800行, 動的機能込み)
```

### **技術負債の管理**
- **継続的リファクタリング**: 各Phaseでの構造改善
- **テスト駆動開発**: 安全な変更保証
- **ドキュメント維持**: 技術負債の可視化

---

## 🚀 **将来構想**

### **短期計画 (v2.2)**
- 大量感想対応 (ページング実装)
- 感想エクスポート機能 (CSV/JSON)
- カスタムテーマ機能

### **中期計画 (v3.0)**
- 他サイト対応拡張
- クラウド同期機能
- 高度な検索・分析機能

### **技術的展望**
- **AIアシスタント統合**: 感想分析・要約機能
- **PWA化**: オフラインWebアプリ対応
- **API提供**: 外部ツール連携

---

## 📚 **関連ドキュメント**

### **設計書系**
- [MODULAR_ARCHITECTURE.md](MODULAR_ARCHITECTURE.md) - モジュール詳細設計
- [FINAL_INTEGRATION_STRATEGY.md](FINAL_INTEGRATION_STRATEGY.md) - 統合戦略

### **実装系**
- [CLAUDE.md](CLAUDE.md) - 開発ルール・ガイドライン
- [PHASE3_IMPLEMENTATION_SUMMARY.md](PHASE3_IMPLEMENTATION_SUMMARY.md) - Phase3実装詳細

### **運用系**
- [MAINTENANCE_GUIDE.md](MAINTENANCE_GUIDE.md) - 保守・運用ガイド
- [FINAL_BROWSER_TEST_GUIDE.md](FINAL_BROWSER_TEST_GUIDE.md) - テスト手順

---

**🏗️ このプロジェクト設計書は、技術的意思決定と将来の拡張方針を定義します**