#!/bin/bash
echo "ハーメルン小説保存ツールをビルドしています..."
echo

echo "必要なモジュールをインストール中..."
pip install pyinstaller brotli cloudscraper undetected-chromedriver selenium beautifulsoup4 lxml requests pillow

echo
echo "ビルド開始..."
pyinstaller --clean HamelnNovelSaver.spec

echo
echo "ビルド完了！"
echo "実行ファイルは dist/HamelnNovelSaver にあります。"
echo
read -p "Enterキーを押して終了..."