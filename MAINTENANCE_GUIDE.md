# 🔧 **ハーメルン感想システム - 保守・運用ガイド**

## 📋 **システム構成**

### **コアファイル**
- **`/感想/comments_data.json`** - 感想データ（6.5KB）
- **`/感想/comments_filter.js`** - 動的機能（18KB）  
- **`/感想/感想 - ページ1.html`** - 感想ページ1（JavaScript統合済み）
- **`/感想/感想 - ページ2.html`** - 感想ページ2（JavaScript統合済み）

### **テスト・保守ツール**
- **`extract_comments_data.py`** - 感想データ再抽出スクリプト
- **`test_comments_filtering.py`** - 動的機能テスト
- **`test_comments_display_fix.py`** - 表示問題確認テスト

---

## 🔍 **トラブルシューティング**

### **問題1: 感想が表示されない**

#### **症状**
- ブラウザで感想ページを開いても感想が0件

#### **診断手順**
1. **開発者ツール確認** (F12)
   ```javascript
   // コンソールで確認すべきメッセージ
   "感想フィルタリング機能初期化開始..."
   "JSONファイル読み込み試行: ./comments_data.json"
   ```

2. **JSONファイル確認**
   ```bash
   # ファイル存在確認
   ls -la "/感想/comments_data.json"
   
   # JSON構文確認
   python3 -c "import json; json.load(open('/感想/comments_data.json'))"
   ```

#### **解決方法**
- **シナリオA**: JSONエラー
  ```bash
  # データ再生成
  python3 extract_comments_data.py
  ```

- **シナリオB**: JavaScript無効
  - ブラウザのJavaScript有効化確認
  - 「※ 動的機能は無効です」メッセージで元HTML表示確認

### **問題2: フィルタリング機能が動作しない**

#### **症状**
- 検索・ソート機能が反応しない

#### **診断手順**
1. **コンソールエラー確認**
2. **イベントハンドラ確認**
   ```javascript
   // ブラウザコンソールで実行
   console.log(commentsFilter);
   commentsFilter.allComments.length; // データ数確認
   ```

#### **解決方法**
1. **ページリロード**: Ctrl+F5
2. **キャッシュクリア**: ブラウザキャッシュ削除
3. **JavaScript再読み込み**: comments_filter.jsの更新確認

### **問題3: ページネーションが機能しない**

#### **症状**  
- 感想ページ1↔2の移動ができない

#### **解決方法**
```bash
# ページネーション修正の再実行
python3 test_comments_navigation.py
```

---

## 📊 **データ更新手順**

### **新しい感想の追加**

1. **新しい感想ページ保存**
   - ハーメルンスクレイパーで最新データ取得

2. **JSONデータ再生成**
   ```bash
   python3 extract_comments_data.py
   ```

3. **動作確認**
   ```bash
   python3 test_comments_filtering.py
   ```

### **感想データ構造の理解**

#### **基本構造**
```json
{
  "comment_id": "レビューID",
  "username": "投稿者名",
  "date_text": "投稿日時文字列", 
  "comment_text": "感想本文",
  "good_count": "Good数（数値）",
  "bad_count": "Bad数（数値）",
  "chapter_number": "対象話数（数値）",
  "good_rate": "Good率（数値）",
  "is_hidden": "隠しコメント（boolean）"
}
```

#### **追加・修正時の注意点**
- **chapter_number**: 0は話数なし、1-6が各話
- **good_rate**: good_count/(good_count+bad_count)*100で自動計算
- **is_hidden**: ▼このコメントは隠されています。の判定

---

## ⚙️ **カスタマイズガイド**

### **ソート機能の追加**

#### **新しいソート条件を追加する場合**
1. **`comments_filter.js`の`sortComments()`メソッド修正**
   ```javascript
   case '15': // 新しいソート条件
       return a.new_field - b.new_field; // 昇順
   ```

2. **HTMLの`<select>`オプション追加**
   ```html
   <option value="15">新しいソート条件</option>
   ```

### **フィルター機能の拡張**

#### **新しいフィルター条件**
1. **`applyFiltersAndSort()`メソッド修正**
   ```javascript
   // 新しいフィルター条件
   if (this.currentFilters.newFilter) {
       if (!comment.new_field.includes(this.currentFilters.newFilter)) {
           return false;
       }
   }
   ```

### **見た目のカスタマイズ**

#### **CSS修正**
- **`/感想/resources/style_v2.css`** - 元のスタイル
- **`comments_filter.js`** - 動的スタイル追加箇所

---

## 🛡️ **安全性とバックアップ**

### **重要ファイルのバックアップ**
```bash
# 定期バックアップ推奨
cp "/感想/comments_data.json" "/感想/comments_data_backup_$(date +%Y%m%d).json"
cp "/感想/comments_filter.js" "/感想/comments_filter_backup_$(date +%Y%m%d).js"
```

### **フォールバック機能の維持**
- **元HTMLの保護**: JavaScript無効時も感想表示確保
- **段階的初期化**: データ検証後のみHTML操作
- **詳細ログ出力**: 問題発生時の迅速な特定

---

## 📈 **パフォーマンス最適化**

### **現在の性能**
- **総追加サイズ**: 26.4KB
- **感想データ**: 6.5KB  
- **JavaScript**: 18KB
- **読み込み時間**: <100ms（ローカル）

### **大量データ対応**
感想が100件を超える場合の推奨対応：

1. **ページング実装**
   ```javascript
   // 50件ずつ表示
   const ITEMS_PER_PAGE = 50;
   ```

2. **遅延読み込み**
   ```javascript
   // 必要時にのみデータ読み込み
   async loadMoreComments() { ... }
   ```

---

## 📚 **関連ドキュメント**

### **プロジェクト文書**
- **`CLAUDE.md`** - 開発ルールと実装記録
- **`PHASE3_IMPLEMENTATION_SUMMARY.md`** - 今回の実装成果
- **`FINAL_BROWSER_TEST_GUIDE.md`** - ブラウザテスト手順

### **技術参考**
- **BeautifulSoup**: HTML解析ライブラリ
- **JavaScript ES6**: モダンJavaScript機能
- **JSON**: データ構造仕様
- **select2.js**: ドロップダウン拡張ライブラリ

---

## 🆘 **サポート情報**

### **問題報告時の情報収集**
1. **ブラウザ**: Chrome/Firefox/Safari + バージョン
2. **エラーメッセージ**: 開発者ツールのコンソール内容
3. **操作手順**: 問題発生までの具体的な手順
4. **ファイル状況**: 感想ページ・JSONファイルの存在確認

### **よくある質問**

#### **Q: 新しい章が追加された場合は？**
A: ハーメルンスクレイパーで再取得後、`extract_comments_data.py`実行

#### **Q: JavaScript機能を無効にしたい場合は？**  
A: HTMLから`<script src="./comments_filter.js"></script>`を削除

#### **Q: ソート順序をカスタマイズしたい場合は？**
A: `comments_filter.js`の`sortComments()`メソッドを修正

---

**🔧 システムの健全性を保つため、定期的な動作確認を推奨します 🔧**