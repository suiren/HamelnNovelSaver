# 🌟 **ハーメルン小説保存アプリケーション**

> ハーメルン（https://syosetu.org）の小説をローカルに完全保存するWebスクレイピングツール

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://github.com/)

## 📋 **概要**

**ハーメルン小説保存アプリケーション**は、ハーメルンで公開されている小説を、**完全なオフライン閲覧環境**として保存するためのツールです。

### 🎯 **主な機能**

- 📖 **完全な小説保存**: HTML形式で元の見た目を完全再現
- 🔗 **ローカルナビゲーション**: 目次・章・感想・小説情報間の完全リンク
- 💬 **感想システム**: 動的ソート・フィルタリング機能付き
- 🛡️ **Cloudflare対応**: bot検知システムを安全に回避
- ⚡ **高速・軽量**: 効率的なリソース管理

### ✨ **特徴**

- **見た目完全再現**: CSS、JavaScript、画像を含む完全保存
- **インタラクティブ感想**: 14種類のソート・検索機能
- **安全な取得**: User-Agentローテーション、適応的待機時間
- **GUI/CUI両対応**: 用途に応じた使いやすいインターフェース

---

## 🚀 **インストール**

### **必要環境**
- Python 3.8以上
- インターネット接続（初回取得時）

### **1. リポジトリのクローン**
```bash
git clone https://github.com/your-username/hameln-novel-scraper.git
cd hameln-novel-scraper
```

### **2. 依存関係のインストール**
```bash
pip install -r requirements.txt
```

### **3. 動作確認**
```bash
python hameln_gui.py
```

---

## 📖 **使用方法**

### **GUI版（推奨）**
```bash
python hameln_gui.py
```
1. **小説URL入力**: ハーメルンの小説URLを貼り付け
2. **保存先選択**: 出力フォルダを指定
3. **実行**: 「保存開始」ボタンクリック

### **コマンドライン版**
```bash
python hameln_scraper_final.py
```
対話式でURL・保存先を入力

---

## 🎮 **オフライン閲覧**

保存完了後、**完全なオフライン環境**で小説をお楽しみいただけます：

### **基本ナビゲーション**
1. **`目次.html`**を開く
2. **各章へジャンプ**: 章タイトルクリック
3. **感想閲覧**: 「感想」リンククリック
4. **小説情報確認**: 「小説情報」リンククリック

### **感想システム（Phase3新機能）**
- 🔍 **キーワード検索**: 感想内容・投稿者名で検索
- 📊 **14種類ソート**: 投稿日↕、Good数↕、話数↕等
- 🎯 **話数フィルター**: 特定の話の感想のみ表示
- ⚡ **リアルタイム更新**: 瞬時のフィルタリング

---

## 🛠️ **技術仕様**

### **対応サイト**
- [ハーメルン](https://syosetu.org) - 二次創作小説投稿サイト

### **保存形式**
- **HTML**: 元の見た目を完全再現
- **リソース**: CSS、JavaScript、画像を含む
- **構造**: 章別ファイル + 目次 + 感想 + 小説情報

### **技術スタック**
- **言語**: Python 3.8+
- **Webスクレイピング**: cloudscraper, BeautifulSoup4, undetected-chromedriver
- **GUI**: tkinter
- **動的機能**: JavaScript (感想フィルタリング)

---

## ⚠️ **重要な注意事項**

### **ハーメルンアクセスについて**
- ハーメルンは**Cloudflare保護**されています
- 本アプリは適切な回避機能を実装済み
- **過度なアクセスは避けてください**（推奨: 章間3-8秒間隔）

### **法的注意事項**
- **個人使用の範囲内**での利用を想定
- 著作権法および利用規約を遵守すること
- 再配布・商用利用は禁止

---

## 📚 **ドキュメント**

### **ユーザーガイド**
- [最終ブラウザテスト手順](FINAL_BROWSER_TEST_GUIDE.md)
- [Phase3実装成果](PHASE3_IMPLEMENTATION_SUMMARY.md)
- [メンテナンス・運用ガイド](MAINTENANCE_GUIDE.md)

### **開発者向け**
- [プロジェクト設計](PROJECT.md)
- [開発ルール](CLAUDE.md)
- [実装履歴](CHANGELOG.md)

---

## 🔧 **トラブルシューティング**

### **よくある問題**

#### **❌ 「メインページの取得に失敗しました」**
- **原因**: bot検知による拒否
- **対策**: 時間をおいて再試行

#### **❌ 感想が表示されない**
- **原因**: JavaScript実行エラー
- **対策**: ブラウザの開発者ツール(F12)でエラー確認

#### **❌ 章リンクが機能しない**
- **原因**: ローカルナビゲーション未修正
- **対策**: [メンテナンスガイド](MAINTENANCE_GUIDE.md)参照

### **詳細なトラブルシューティング**
[メンテナンス・運用ガイド](MAINTENANCE_GUIDE.md)を参照してください。

---

## 🎉 **バージョン履歴**

### **Phase 3 (v2.0) - 2025年7月**
- ✅ **感想動的フィルタリング機能**: 14種類ソート・検索機能
- ✅ **完全ローカルナビゲーション**: 全ページ間の双方向リンク
- ✅ **安全なフォールバック機能**: JavaScript失敗時の表示保護

### **Phase 2 (v1.5) - 2025年7月**
- ✅ **モジュール構造改革**: 70%コード削減
- ✅ **小説情報・感想保存機能**: 包括的情報取得

### **Phase 1 (v1.0) - 2025年7月**
- ✅ **基本スクレイピング機能**: HTML形式での小説保存
- ✅ **Cloudflare対応**: 安全な取得機能

詳細は[CHANGELOG.md](CHANGELOG.md)を参照

---

## 🤝 **コントリビューション**

プロジェクトへの貢献を歓迎します！

1. **Fork** このリポジトリ
2. **Feature Branch** 作成 (`git checkout -b feature/amazing-feature`)
3. **Commit** 変更 (`git commit -m 'Add amazing feature'`)
4. **Push** ブランチ (`git push origin feature/amazing-feature`)
5. **Pull Request** 作成

詳細は[CONTRIBUTING.md](CONTRIBUTING.md)を参照

---

## 📄 **ライセンス**

このプロジェクトは[MITライセンス](LICENSE)の下で配布されています。

---

## 🌟 **サポート**

- **Issues**: [GitHub Issues](https://github.com/your-username/hameln-novel-scraper/issues)
- **ドキュメント**: [プロジェクトWiki](https://github.com/your-username/hameln-novel-scraper/wiki)

---

**🎊 Happy Novel Reading! オフライン読書をお楽しみください！ 🎊**