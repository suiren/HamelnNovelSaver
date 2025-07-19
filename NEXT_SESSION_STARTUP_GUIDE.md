# 🚀 次セッション即座開始ガイド

## 🎯 このガイドの目的
セッションが途切れた後、次のセッションで即座にPhase 3を継続するための完全マニュアル

## ⚡ ワンライナー復旧 (最速開始)

```bash
# 状況確認・作業継続
git status && git log --oneline -3 && cat PHASE_3_PROGRESS_TRACKER.md | head -20
```

## 📊 Step-by-Step 復旧手順

### 1. 基本状況確認 (30秒)
```bash
# 現在地確認
pwd  # /home/suiren/ClaudeTest にいるか確認

# Git状況確認  
git branch  # feature/refactor-hameln-scraper にいるか確認
git status  # 作業ディレクトリの状態確認

# 最新コミット確認
git log --oneline -5
# 期待値: 2f05a97 🔧 Phase 2.5完了: クリティカル統合問題修正とテスト
```

### 2. Progress Tracker確認 (1分)
```bash
# 進捗状況確認
cat PHASE_3_PROGRESS_TRACKER.md | grep -A 10 "📋 Todo リスト状況"

# 完了済み作業確認
cat PHASE_3_PROGRESS_TRACKER.md | grep "✅"
```

### 3. 前回までの実績確認 (1分)
```bash
# モジュール構造確認
find hameln_scraper -name "*.py" | head -10

# テスト状況確認
python -m pytest test_network_module.py --tb=no -q
# 期待値: 12 passed

# 現在のコード行数確認  
find hameln_scraper -name "*.py" -exec wc -l {} + | tail -1
# 期待値: 967行程度
```

### 4. Phase 3 作業再開準備 (2分)
```bash
# 元ファイル確認
wc -l hameln_scraper_final.py
# 期待値: 2503行

# 移行対象関数確認
grep -n "def extract_chapter_content\|def get_chapter_links\|def extract_novel_info" hameln_scraper_final.py

# 現在のparsingモジュール確認
ls -la hameln_scraper/parsing/
```

### 5. Claude への状況説明テンプレート

**Claudeに伝える内容**:
```
Phase 3 HTML解析モジュール分離の継続作業です。

現在の状況:
- ブランチ: feature/refactor-hameln-scraper  
- 前段階: Phase 2.5 完了 (クリティカル統合問題修正済み)
- 進捗: [STEP 2の結果を貼り付け]
- 次のタスク: [STEP 2のTodo状況から次のタスクを特定]

CLAUDE.mdチェックリスト確認完了として、TDD手順に従って継続してください。
```

## 🔧 作業再開時の確認事項

### 必須チェック項目
- [ ] ブランチが `feature/refactor-hameln-scraper` か
- [ ] 最新コミットが `2f05a97` (Phase 2.5完了) か  
- [ ] 既存テストが 12/12 通過するか
- [ ] `PHASE_3_PROGRESS_TRACKER.md` が存在するか
- [ ] Todo リストの次のタスクが明確か

### トラブルシューティング

#### 問題: ブランチが違う
```bash
git checkout feature/refactor-hameln-scraper
```

#### 問題: テストが失敗する
```bash  
# 統合問題のチェック
python -c "from hameln_scraper.core.scraper import HamelnScraper; print('OK')"
```

#### 問題: 進捗が不明
```bash
# 最新の進捗ファイル確認
ls -la *PROGRESS* *GUIDE* *SNAPSHOT*
```

## 📋 Phase 3 専用コマンドセット

### 開発・テスト用
```bash
# 新しいテスト実行
python -m pytest test_parsing_module.py -v

# 統合テスト確認
python -m pytest test_network_module.py test_integration_success.py -q

# 実URL動作確認
python -c "
from hameln_scraper.core.scraper import HamelnScraper
scraper = HamelnScraper()
result = scraper.scrape_novel('https://syosetu.org/novel/219754/')
print('成功' if result['success'] else '失敗')
scraper.close()
"
```

### 進捗管理用
```bash
# 進捗更新コマンド（Claudeが実行）
echo "$(date): [タスク名] 完了" >> PHASE_3_PROGRESS_TRACKER.md

# 状態スナップショット更新
git status > CURRENT_STATE_SNAPSHOT.md
```

## 🎯 Phase 3 完了条件の再確認

- [ ] 元ファイル解析関数をすべてモジュール分離
- [ ] 全テスト通過 (既存+新規)
- [ ] 実ハーメルンURLでの動作確認
- [ ] コード品質: 最大ファイル200行以下
- [ ] 1500行以下の目標達成 (40%以上削減)

## 📞 緊急時の対応

### 完全にわからなくなった場合
1. この `NEXT_SESSION_STARTUP_GUIDE.md` を最初から実行
2. `PHASE_3_PROGRESS_TRACKER.md` を詳読
3. Claudeに「Phase 3の状況がわからなくなりました。ガイドに従って状況確認しました」と報告

### ファイルが破損した場合
```bash
# 最新のコミットから復旧
git checkout HEAD -- hameln_scraper/
git checkout HEAD -- test_*.py

# 最悪の場合は前のコミットに戻す
git reset --hard 2f05a97
```

---

**📅 作成日**: 2025-07-19  
**🎯 対象**: Phase 3 HTML解析モジュール分離  
**🔄 有効期間**: Phase 3 完了まで