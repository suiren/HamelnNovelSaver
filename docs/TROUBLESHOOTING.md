# ハーメルン小説保存ツール - トラブルシューティングガイド

## 開発プロセス改善のためのガイドライン

### 発生した問題と教訓

#### 問題1: 間違った作品の章を取得してしまう
**原因**: 
```python
('a', {'href': lambda x: x and '/novel/' in x and len(x.split('/')) >= 4})
```
このセレクターが広すぎて、目次ページにある他の作品のリンクも取得してしまった。

**修正**: 
```python
('a', {'href': lambda x: x and f'/novel/{novel_id}/' in x and x.count('/') >= 4 and x.endswith('.html')})
```
特定の作品IDのみを対象とするように限定。

**教訓**: 
- セレクターは可能な限り具体的に
- 実際のHTMLページで他の要素が混入しないかを確認

#### 問題2: ページ再現が壊れる
**原因**: 
`save_complete_page`の引数で`base_url`を`self.base_url`（"https://syosetu.org"）に変更したため、相対パス解決が正しく動作しなくなった。

**修正**: 
`base_url`には実際のページのURLを渡す必要がある。

**教訓**: 
- メソッドの引数の意味を正確に理解する
- 引数変更時は、そのメソッド内でどう使われているかを確認

#### 問題3: 相対パス形式の章リンクが検出されない
**原因**: 
```python
# 従来のセレクター（絶対パスのみ想定）
('a', {'href': lambda x: x and f'/novel/{novel_id}/' in x and x.count('/') >= 4 and x.endswith('.html')})
```
ハーメルンの実際のリンクが `./1.html`, `./2.html` という相対パス形式だったため検出失敗。

**修正**: 
```python
# 相対パス形式のセレクターを追加
('a', {'href': lambda x: x and re.match(r'\./\d+\.html$', x)})
```
相対パスを絶対パスに変換する処理も追加。

**教訓**: 
- 実際のHTML構造を詳細に調査してからセレクターを設計する
- 絶対パスと相対パスの両方を考慮する
- 仮定ではなく実際のデータで検証する

#### 問題4: CSS文字化けとリソース重複処理
**原因**: 
各章の処理で`process_html_resources`が重複実行され、CSSファイルが何度も上書きされてエンコーディングが破損。

**修正**: 
```python
# ❌ 各章で重複処理（CSSが破損する）
for chapter_url in chapter_links:
    chapter_soup = self.get_page(chapter_url)
    chapter_soup = self.process_html_resources(chapter_soup, output_dir)  # 重複！

# ✅ 目次ページで1回のみ + 各章はパス調整のみ
index_soup = self.process_html_resources(soup, output_dir)  # 1回のみ
for chapter_url in chapter_links:
    chapter_soup = self.get_page(chapter_url)
    chapter_soup = self.adjust_resource_paths_only(chapter_soup, output_dir)  # パスのみ
```

**保護機能追加**:
```python
# 既存ファイルの上書き防止
if os.path.exists(local_path):
    print(f"既存ファイルを使用（上書き防止）: {filename}")
    return filename
```

**教訓**: 
- リソース処理は1回のみ実行する
- 既存ファイルの保護機能を実装する
- 重複処理によるエンコーディング破損に注意

#### 問題5: 不要なファイル生成（副作用）
**原因**: 
CSS問題の修正時に、関係ない目次ページ保存処理も同時に変更したため、不要な目次ファイルが生成された。

**修正**: 
```python
# ❌ 不必要な変更（目次ページを保存）
index_file_path = self.save_complete_page(...)

# ✅ 最小限の修正（リソースダウンロードのみ）
self.process_html_resources(soup, output_dir)  # ページ保存は削除
```

**根本原因**: 
指摘された問題以外の「ついでに」修正による副作用

**教訓**: 
- **最小変更の法則**: 指摘された問題のみを修正する
- **副作用防止**: 修正対象外の処理は変更しない
- **段階的修正**: 一度に複数の問題を修正しない
- **事前確認**: 修正前に現在の動作を詳細に把握する

### 今後の開発プロセス

#### 1. 段階的開発・テスト
```
変更 → ビルド → テスト → 確認 → 次の変更
```
一度に複数の変更をしない。

#### 2. 実際のテストの実施
- 机上の空論ではなく、実際にビルドして動作確認
- 複数のテストケースで確認

#### 3. デバッグログの活用
実装前に以下のログを追加：
```python
print(f"=== 処理開始: {function_name} ===")
print(f"入力パラメータ: {params}")
print(f"中間結果: {intermediate_result}")
print(f"最終結果: {final_result}")
```

#### 4. コードレビューチェックリスト
- [ ] セレクターが広すぎないか？
- [ ] 引数の意味は正しいか？
- [ ] エラーハンドリングは適切か？
- [ ] ログ出力は十分か？

### よくある問題と対処法

#### 問題: 章リンクが取得できない
**確認項目**:
1. 作品IDの抽出は正しいか？
2. セレクターは適切か？
3. ページ構造に変更はないか？

**デバッグ方法**:
```python
# test_chapter_extraction.py を実行
python test_chapter_extraction.py
```

#### 問題: ページの保存が失敗する
**確認項目**:
1. `save_complete_page`の引数は正しいか？
2. 保存先ディレクトリは存在するか？
3. ファイル名に不正文字はないか？

**デバッグ方法**:
```python
# ログファイルを確認
tail -f hameln_debug.log
```

#### 問題: 直接的なHTTPアクセスが失敗する
🚨 **CRITICAL**: ハーメルン（syosetu.org）はCloudflareで保護されています 🚨

**症状**:
- `curl`、`requests`でのアクセスが失敗
- 「Just a moment...」メッセージ
- 403 Forbidden エラー

**原因**:
Cloudflareのbot検知により、直接的なHTTPリクエストが拒否される

**対処法**:
```python
# ❌ 直接的なrequests（失敗します）
import requests
response = requests.get("https://syosetu.org/novel/378070/")

# ✅ CloudScraperを使用（成功します）
import cloudscraper
scraper = cloudscraper.create_scraper()
response = scraper.get("https://syosetu.org/novel/378070/")

# ✅ undetected-chromedriverを使用（成功します）
import undetected_chromedriver as uc
driver = uc.Chrome()
driver.get("https://syosetu.org/novel/378070/")
```

**重要**:
- bashコマンドでの直接アクセス（curl等）は避ける
- 必ずCloudscraper或いはSeleniumを使用する
- このプロジェクトは既に適切な実装済み

#### 問題: CSSが正しく保存されない
**確認項目**:
1. エンコーディング設定は適切か？
2. URL置換処理は正確か？
3. 相対パスの解決は正しいか？

### 緊急時の対処法

#### 機能が完全に壊れた場合
1. 直前の動作していたコミット/バージョンに戻す
2. 一つずつ変更を適用して問題箇所を特定
3. 小さな修正から段階的に適用

#### 原因が分からない場合
1. デバッグログを最大レベルで出力
2. テストファイルで単純なケースから確認
3. 各処理段階での中間データを確認

### テストケース一覧

#### 基本テスト
- [ ] 目次ページからの全話取得
- [ ] 各話ページからの全話取得
- [ ] 単話のみの保存
- [ ] CSS・画像の正常保存

#### エッジケース
- [ ] 作品IDが含まれた他作品リンクが目次にある場合
- [ ] 非常に長いタイトルの作品
- [ ] 特殊文字を含むタイトル

### 定期メンテナンス

#### 月次チェック
- [ ] ハーメルンのHTML構造変更確認
- [ ] 主要な作品での動作確認
- [ ] エラーログの確認

#### 機能追加時
- [ ] 既存機能への影響確認
- [ ] 新機能のテストケース作成
- [ ] ドキュメント更新

---

**重要**: このガイドは実際に発生した問題を基に作成されています。新しい問題が発生した場合は、必ずこのガイドを更新してください。