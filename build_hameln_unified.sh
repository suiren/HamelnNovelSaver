#!/bin/bash

echo "ハーメルン小説保存ツール - 統合ビルドスクリプト"
echo

show_menu() {
    echo "==========================================="
    echo "    ビルドオプション選択"
    echo "==========================================="
    echo "1. GUI版のみビルド (HamelnNovelArchiverGUI)"
    echo "2. CUI版のみビルド (HamelnNovelArchiverCUI)"
    echo "3. 両方をビルド (GUI + CUI)"
    echo "4. 従来版（後方互換性）"
    echo "5. 終了"
    echo "==========================================="
    echo -n "選択してください (1-5): "
}

install_deps() {
    echo "必要なモジュールをインストール中..."
    pip install pyinstaller brotli cloudscraper undetected-chromedriver selenium beautifulsoup4 lxml requests Pillow
}

check_modules() {
    if [ ! -d "hameln_scraper" ]; then
        echo "エラー: hameln_scraperモジュールが見つかりません"
        echo "リファクタリング版ブランチ（refactor/code-restructuring）にいることを確認してください"
        read -p "Press any key to continue..."
        exit 1
    fi
}

check_result() {
    if [ -f "$1" ]; then
        echo "✅ $2 ビルド完了！"
        echo "実行ファイル: $1"
        echo
        if [ "$2" == "GUI版" ]; then
            echo "✨ GUI版の特徴:"
            echo "- グラフィカルユーザーインターフェース"
            echo "- 使いやすい操作画面"
            echo "- リアルタイム進捗表示"
            echo "- ファイル選択ダイアログ"
        fi
        if [ "$2" == "CUI版" ]; then
            echo "✨ CUI版の特徴:"
            echo "- コマンドライン操作"
            echo "- 軽量で高速"
            echo "- バッチ処理に最適"
            echo "- サーバー環境対応"
        fi
    else
        echo "❌ $2 ビルド失敗"
        echo "$1 が作成されませんでした"
    fi
    echo
}

build_gui() {
    echo
    echo "GUI版をビルドしています..."
    install_deps
    check_modules
    pyinstaller --clean HamelnNovelArchiverGUI.spec
    check_result "dist/HamelnNovelArchiverGUI" "GUI版"
}

build_cui() {
    echo
    echo "CUI版をビルドしています..."
    install_deps
    check_modules
    pyinstaller --clean HamelnNovelArchiverCUI.spec
    check_result "dist/HamelnNovelArchiverCUI" "CUI版"
}

build_both() {
    echo
    echo "GUI版とCUI版の両方をビルドしています..."
    install_deps
    check_modules
    echo "GUI版をビルド中..."
    pyinstaller --clean HamelnNovelArchiverGUI.spec
    echo "CUI版をビルド中..."
    pyinstaller --clean HamelnNovelArchiverCUI.spec
    check_result "dist/HamelnNovelArchiverGUI" "GUI版"
    check_result "dist/HamelnNovelArchiverCUI" "CUI版"
}

build_legacy() {
    echo
    echo "従来版をビルドしています..."
    install_deps
    check_modules
    pyinstaller --clean HamelnNovelSaver.spec
    check_result "dist/HamelnNovelArchiver" "従来版"
}

# メインループ
while true; do
    show_menu
    read choice
    
    case $choice in
        1) build_gui ;;
        2) build_cui ;;
        3) build_both ;;
        4) build_legacy ;;
        5) echo "ビルドスクリプトを終了します。"; exit 0 ;;
        *) echo "無効な選択です。"; echo ;;
    esac
done