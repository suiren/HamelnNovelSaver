#!/bin/bash
#
# GitHub Actions ワークフロー実行履歴の整理スクリプト
# 
# 削除方針:
# - 失敗したワークフロー: 削除推奨（ノイズ除去）
# - 成功したワークフロー: 保持推奨（貴重な履歴情報）
# - GitHubが90日後に自動削除するため、手動削除は通常不要
#
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

# 注意：成功したワークフローは貴重な履歴情報のため通常は削除不要
# GitHubが90日後に自動削除するため、手動削除は推奨しません
echo ""
echo "ℹ️ 成功したワークフローは貴重な履歴のため保持を推奨"
echo "ℹ️ GitHubが90日後に自動削除するため手動削除は通常不要"

echo ""
echo "🎉 ワークフロー実行履歴の整理が完了しました"
echo "📊 現在の実行状況:"
gh run list --repo "$REPO_OWNER/$REPO_NAME" --limit 10