# 開発プロセス全般における過去のミス記録

## 🚨 **重要**: このファイルは将来のセッションでの同様ミス防止用

---

## 📅 **2025年7月15日のセッション - CI/CD開発**

### **❌ 発生したミス**

#### **1. actions/upload-artifact非推奨バージョン使用**
- **ミス**: `actions/upload-artifact@v3` を使用
- **結果**: 「This request has been automatically failed because it uses a deprecated version」
- **正解**: `actions/upload-artifact@v4` を使用すべき
- **原因**: 最新バージョン確認不足

#### **2. YAML構文エラー**
- **ミス**: 複数行Python文字列をYAMLに直接記述
- **結果**: 「You have an error in your yaml syntax on line 202」
- **正解**: 別ファイルにPythonスクリプトを分離して実行
- **原因**: YAML構文理解不足

#### **3. 依存関係インストール不一致**
- **ミス**: CI/CDで手動パッケージリスト、requirements.txtを無視
- **結果**: 「ModuleNotFoundError: No module named 'brotli'」
- **正解**: `pip install -r requirements.txt` で統一
- **原因**: 依存関係管理の不一致

#### **4. ローカル事前テスト不足**
- **ミス**: CI/CDにプッシュしてからエラー発見
- **結果**: 複数回の失敗実行履歴蓄積
- **正解**: ローカルで事前に全テスト実行
- **原因**: テスト駆動開発の徹底不足

---

## 🔧 **防止策実装済み**

1. **ローカル事前検証スクリプト**: `test_local_environment.py`
2. **requirements.txt統一**: 全ジョブで`pip install -r requirements.txt`
3. **YAML構文改善**: Python長文は別ファイル分離
4. **最新バージョン使用**: actions/upload-artifact@v4

---

## 📋 **今後のセッションでの必須チェック項目**

### **CI/CD関連タスク開始時**
- [ ] 最新のGitHub Actions公式ドキュメント確認
- [ ] requirements.txtと実際のインストール処理の一致確認
- [ ] YAMLファイルの構文チェック実行
- [ ] ローカル環境での事前テスト必須実行

### **プッシュ前必須実行**
```bash
python test_local_environment.py
```
このスクリプトが全て成功するまでプッシュ禁止

---

## 🎯 **教訓**

1. **「小さなミスが大きな問題に」**: バージョン違い1文字が全体停止
2. **「ローカルテスト最重要」**: CI/CDは最後の確認、事前検証必須
3. **「設定ファイル統一性」**: requirements.txtと実装の乖離は致命的
4. **「構文チェック基本」**: YAML等の構文は事前確認必須

---

## 🤖 **ミス発生時の自動対応ルール**

### **Claude必須実行事項**
1. **即座にMISTAKES_LOG.mdにミス記録を追加**
   - 日付、タスク内容、ミス詳細、原因分析、防止策を記録
2. **CLAUDE.mdの該当セクションを強化**
   - 新しいチェック項目を追加
   - 禁止事項リストを更新
3. **関連する検証スクリプトを作成・改善**
   - ローカル事前検証の強化
   - 自動チェック機能の追加

### **テンプレート**
```markdown
## 📅 **[日付] - [タスク種別]**

### **❌ 発生したミス**
#### **[ミス名]**
- **ミス**: [具体的な間違い]
- **結果**: [発生した問題]
- **正解**: [正しい方法]
- **原因**: [根本原因]

### **🔧 防止策実装済み**
- [実装した対策1]
- [実装した対策2]

### **📋 今後のチェック項目**
- [ ] [新しいチェック項目1]
- [ ] [新しいチェック項目2]
```

---

## 📚 **参考リンク**
- [GitHub Actions公式ドキュメント](https://docs.github.com/en/actions)
- [actions/upload-artifact最新情報](https://github.com/actions/upload-artifact)
- [YAML構文チェッカー](https://yaml-online-parser.appspot.com/)