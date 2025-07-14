# 🚨 Cloudflare保護サイトに関する重要な注意事項

## 対象サイト
- **ハーメルン（syosetu.org）**：Cloudflareで保護されています

## 重要な制限事項

### ❌ 使用禁止の方法
```bash
# 直接的なHTTPリクエストは失敗します
curl https://syosetu.org/novel/378070/
wget https://syosetu.org/novel/378070/
```

```python
# 通常のrequestsライブラリも失敗します
import requests
response = requests.get("https://syosetu.org/novel/378070/")
# → 403 Forbidden または "Just a moment..." ページ
```

### ✅ 正しい方法

#### 1. CloudScraper（推奨）
```python
import cloudscraper
scraper = cloudscraper.create_scraper()
response = scraper.get("https://syosetu.org/novel/378070/")
```

#### 2. undetected-chromedriver
```python
import undetected_chromedriver as uc
driver = uc.Chrome()
driver.get("https://syosetu.org/novel/378070/")
```

## このプロジェクトでの実装

このプロジェクトは既にCloudflare保護に対応済みです：

```python
# hameln_scraper_final.py より
self.cloudscraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    },
    delay=10,
)
```

## 典型的な失敗パターン

### パターン1: "Just a moment..." ページ
```html
<!DOCTYPE html>
<html lang="en-US">
<head>
    <title>Just a moment...</title>
    <!-- Cloudflareの認証ページ -->
</head>
```

### パターン2: 403 Forbidden
```
HTTP/1.1 403 Forbidden
Server: cloudflare
```

## 開発・テスト時の注意

1. **直接テスト禁止**: curlやwgetでの動作確認は無意味です
2. **適切なツール使用**: 必ずCloudscraper/Seleniumでテストしてください
3. **レート制限**: 短時間に多数のリクエストを送らないでください

## 将来のセッションでの参照

この情報は以下のファイルに記録されています：
- `CLAUDE.md`: プロジェクト概要とCloudflare警告
- `TROUBLESHOOTING.md`: 具体的な対処法
- `CLOUDFLARE_NOTICE.md`: この詳細ガイド

新しいセッション開始時は、これらのファイルを確認してください。

---

**最終更新**: 2025-07-13  
**適用対象**: syosetu.org (ハーメルン)