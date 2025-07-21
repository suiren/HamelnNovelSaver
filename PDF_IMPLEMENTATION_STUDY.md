# PDF動的生成機能の実装検討

## 現状分析

ハーメルンのPDFリンクは「処理待ち：1件...」表示後にサーバーサイドでPDFを生成する仕組みになっています。

## 実装アプローチ

### アプローチA: 現状維持（推奨）
**概要**: PDFリンクをそのまま保持し、ユーザーが手動でクリックして生成・ダウンロード

**メリット**:
- 実装が簡単
- ハーメルンの仕様変更に左右されない
- 技術的リスクが低い
- 現在の実装で既に動作している

**デメリット**:
- ユーザーがPDFを取得するには手動操作が必要

### アプローチB: Selenium自動化（将来的な拡張）
**概要**: Selenium + ChromeDriverを使用してPDF生成・ダウンロードを自動化

**技術要件**:
```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def download_pdf_automatically(pdf_url, output_dir):
    options = Options()
    options.add_experimental_option("prefs", {
        "download.default_directory": output_dir,
        "plugins.always_open_pdf_externally": True,
        "download.prompt_for_download": False
    })
    
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(pdf_url)
        
        # 「処理待ち」表示を待機
        wait = WebDriverWait(driver, 60)
        
        # PDFが生成されるまで待機
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "embed")))
        
        # PDFダウンロード
        # (実際の実装はサイトの構造に依存)
        
    finally:
        driver.quit()
```

**メリット**:
- 完全自動化
- ユーザーの手動操作が不要

**デメリット**:
- 技術的複雑性が高い
- ChromeDriverの依存関係
- ハーメルンの仕様変更に脆弱
- 実行時間が長い（生成待機）
- bot検知に引っかかる可能性

### アプローチC: ハイブリッド方式（中間案）
**概要**: 基本は現状維持、オプションでSelenium自動化を提供

**実装方針**:
- デフォルトはPDFリンクを保持
- 設定で自動化機能を有効化可能
- 自動化失敗時は元のリンクにフォールバック

## 推奨実装

**現時点での推奨**: アプローチA（現状維持）

**理由**:
1. 技術的リスクが低い
2. 実装が安定している
3. ユーザーの手動操作は実際のハーメルンと同じ
4. 将来的にアプローチBの実装も可能

## 実装済み機能（現在）

```python
def download_and_localize_pdf_links(self, soup, output_dir, novel_title):
    """PDFリンクを適切に処理する（サーバーサイド生成対応）"""
    # PDFリンクを検出
    pdf_links = self.extract_pdf_links_from_vertical_page(soup)
    
    # 各リンクを処理
    for link in soup.find_all('a', href=True):
        href = link.get('href')
        if href in pdf_links:
            # 絶対URLに変換
            if href.startswith('/'):
                full_url = self.base_url + href
                link['href'] = full_url
            
            # 外部リンクとして設定
            link['target'] = '_blank'
            link['rel'] = 'noopener noreferrer'
            link['title'] = f"PDFファイル生成: {link.get_text(strip=True)}"
```

## 将来的な拡張可能性

設定ファイルでの制御:
```python
# config.py
ENABLE_PDF_AUTO_DOWNLOAD = False  # デフォルト: False
PDF_DOWNLOAD_TIMEOUT = 60  # 秒
PDF_DOWNLOAD_RETRY = 3  # 再試行回数
```

この設計により、現在は安定した実装を提供し、将来的にユーザーの要望に応じて自動化機能を追加できます。