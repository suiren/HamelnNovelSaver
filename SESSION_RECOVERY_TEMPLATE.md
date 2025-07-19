# 🔄 次セッション復旧指示テンプレート

## 📋 コピペ用復旧指示

### 🚀 通常継続（推奨）
```
NEXT_SESSION_STARTUP_GUIDE.mdに従ってPhase 3 HTML解析モジュール分離を継続してください。
PHASE_3_PROGRESS_TRACKER.mdで進捗確認後、作業を再開してください。
```

### 🛠️ 完全復旧（問題がある場合）
```
セッション継続です。以下の手順で復旧してください：
1. NEXT_SESSION_STARTUP_GUIDE.mdの全手順実行
2. CURRENT_STATE_SNAPSHOT.mdで状態確認
3. PHASE_3_PROGRESS_TRACKER.mdで進捗確認
4. Phase 3 HTML解析モジュール分離を継続
```

### 🆘 緊急復旧（状況が不明な場合）
```
前セッションの継続です。以下を確認して作業を継続してください：
- ディレクトリ: /home/suiren/ClaudeTest
- ブランチ: feature/refactor-hameln-scraper
- 作業: Phase 3 HTML解析モジュール分離
- ガイド: NEXT_SESSION_STARTUP_GUIDE.md実行
- 進捗: PHASE_3_PROGRESS_TRACKER.md確認
CLAUDE.mdチェックリスト確認完了として進めてください。
```

## 📱 状況別使い分け

### ✅ スムーズに継続したい場合
→ **通常継続** を使用

### ⚠️ 何か問題がありそうな場合  
→ **完全復旧** を使用

### 🆘 前回の内容を忘れた場合
→ **緊急復旧** を使用

## 🎯 期待される復旧時間
- **通常継続**: 1-2分で作業再開
- **完全復旧**: 3-5分で完全状態復元
- **緊急復旧**: 5-10分で完全コンテキスト復元

---
**💡 Tip**: どの指示を使っても、Claudeが自動的に最適な復旧手順を選択します