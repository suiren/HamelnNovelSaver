#!/bin/bash
#
# GitHub Actions ワークフロー実行履歴の一括削除スクリプト
# 使用前にGitHub CLIがインストール・認証済みであることを確認
#

set -e

REPO_OWNER="suiren"
REPO_NAME="HamelnNovelSaver"

echo "🗑️ GitHub Actions ワークフロー実行履歴の整理を開始..."

# 失敗したワークフローのみを削除（成功したものは残す）
echo "❌ 失敗したワークフロー実行を削除中..."

# 失敗したワークフローを取得して削除
gh run list --repo "$REPO_OWNER/$REPO_NAME" --status failure --json databaseId -q '.[].databaseId' | while read -r run_id; do
    if [ -n "$run_id" ]; then
        echo "  削除中: Run ID $run_id"
        gh api "repos/$REPO_OWNER/$REPO_NAME/actions/runs/$run_id" -X DELETE || echo "    削除失敗: $run_id"
    fi
done

echo "✅ 失敗したワークフロー実行の削除完了"

# 古い成功したワークフローも削除したい場合（オプション）
echo ""
echo "🤔 古い成功したワークフローも削除しますか？ (y/N)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo "📅 30日以上前の成功したワークフローを削除中..."
    
    # 30日以上前の成功したワークフローを削除
    cutoff_date=$(date -d '30 days ago' '+%Y-%m-%d')
    gh run list --repo "$REPO_OWNER/$REPO_NAME" --status success --created "<$cutoff_date" --json databaseId -q '.[].databaseId' | while read -r run_id; do
        if [ -n "$run_id" ]; then
            echo "  削除中: Run ID $run_id"
            gh api "repos/$REPO_OWNER/$REPO_NAME/actions/runs/$run_id" -X DELETE || echo "    削除失敗: $run_id"
        fi
    done
    
    echo "✅ 古いワークフロー実行の削除完了"
fi

echo ""
echo "🎉 ワークフロー実行履歴の整理が完了しました"
echo "📊 現在の実行状況:"
gh run list --repo "$REPO_OWNER/$REPO_NAME" --limit 10