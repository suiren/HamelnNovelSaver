#!/bin/bash
echo "ハーメルン小説保存ツール - 統合ビルド（リファクタリング版対応）"
echo

echo "必要なモジュールをインストール中..."
pip install pyinstaller brotli cloudscraper undetected-chromedriver selenium beautifulsoup4 lxml requests pillow

echo
echo "リファクタリング版モジュール確認中..."
if [ ! -d "hameln_scraper" ]; then
    echo "エラー: hameln_scraperモジュールが見つかりません"
    echo "リファクタリング版ブランチ（refactor/code-restructuring）にいることを確認してください"
    read -p "Enterキーを押して終了..."
    exit 1
fi

echo
echo "ビルド開始（リファクタリング版含む）..."
pyinstaller --clean HamelnNovelSaver.spec

echo
if [ -f "dist/HamelnNovelArchiver" ]; then
    echo "✅ ビルド完了！"
    echo "実行ファイル: dist/HamelnNovelArchiver"
    echo
    echo "✨ 新機能:"
    echo "- モジュール分割による保守性向上"
    echo "- テスト駆動開発による品質保証" 
    echo "- 段階的フォールバック機能"
else
    echo "❌ ビルド失敗"
    echo "dist/HamelnNovelArchiver が作成されませんでした"
fi
echo
read -p "Enterキーを押して終了..."