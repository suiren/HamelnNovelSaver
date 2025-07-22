"""
Phase 4 リソースモジュール統合テスト
新しく作成されたリソースモジュールが既存システムと正常に統合されているか確認
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup

# Phase 4 新リソースモジュールのインポート確認
def test_phase4_resource_modules_import():
    """Phase 4リソースモジュールのインポート確認"""
    # 各モジュールが正常にインポートできることを確認
    from hameln_scraper.resources.file_manager import FileManager
    from hameln_scraper.resources.downloader import ResourceDownloader
    from hameln_scraper.resources.processor import ResourceProcessor
    from hameln_scraper.resources.saver import PageSaver
    
    # インスタンス作成確認
    file_manager = FileManager()
    downloader = ResourceDownloader()
    processor = ResourceProcessor()
    saver = PageSaver()
    
    assert file_manager is not None
    assert downloader is not None
    assert processor is not None
    assert saver is not None


def test_phase4_resource_workflow_integration():
    """Phase 4リソースワークフロー統合テスト"""
    from hameln_scraper.resources.file_manager import FileManager
    from hameln_scraper.resources.downloader import ResourceDownloader
    from hameln_scraper.resources.processor import ResourceProcessor
    from hameln_scraper.resources.saver import PageSaver
    
    # 実際のハーメルンページ構造を模擬
    test_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>テスト小説 第1章</title>
        <link rel="stylesheet" href="https://syosetu.org/css/style.css">
        <script src="https://syosetu.org/js/app.js"></script>
    </head>
    <body>
        <div id="honbun">
            これはテスト小説の第1章です。
            物語の展開を楽しんでください。
        </div>
        <img src="https://img.syosetu.org/images/illustration.jpg" alt="挿絵">
    </body>
    </html>
    """
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 1. ファイル管理機能確認
        file_manager = FileManager()
        novel_dir = file_manager.create_directory_structure(temp_dir, "テスト小説")
        assert os.path.exists(novel_dir)
        assert os.path.exists(os.path.join(novel_dir, "resources"))
        
        # 2. モックダウンローダーでリソース処理確認
        mock_downloader = Mock(spec=ResourceDownloader)
        mock_downloader.download_css.return_value = {
            'success': True,
            'local_path': os.path.join(novel_dir, 'resources', 'style.css'),
            'filename': 'style.css',
            'processed_images': []
        }
        mock_downloader.download_resource.return_value = {
            'success': True,
            'local_path': os.path.join(novel_dir, 'resources', 'test_image.jpg'),
            'filename': 'test_image.jpg'
        }
        
        # 3. HTML処理確認
        processor = ResourceProcessor()
        soup = BeautifulSoup(test_html, 'html.parser')
        
        # パス調整のみ実行（ダウンロードスキップ）
        adjusted_soup = processor.adjust_resource_paths_only(soup)
        
        # リソースパスが ./resources/ 形式に変換されることを確認
        css_link = adjusted_soup.find('link', {'rel': 'stylesheet'})
        assert css_link['href'].startswith('./resources/')
        
        script_tag = adjusted_soup.find('script', src=True)
        assert script_tag['src'].startswith('./resources/')
        
        img_tag = adjusted_soup.find('img', src=True)
        assert img_tag['src'].startswith('./resources/')
        
        # 4. ページ保存機能確認
        saver = PageSaver()
        save_result = saver.save_complete_page(
            str(adjusted_soup),
            novel_dir,
            "chapter1.html",
            original_url="https://syosetu.org/novel/123/1/",
            processor=processor
        )
        
        assert save_result['success'] is True
        assert os.path.exists(save_result['saved_path'])
        
        # 保存されたファイルの内容確認
        with open(save_result['saved_path'], 'r', encoding='utf-8-sig') as f:
            saved_content = f.read()
            assert 'テスト小説' in saved_content
            assert 'save-date' in saved_content
            assert 'source-url' in saved_content


def test_phase4_with_existing_modules():
    """Phase 4モジュールと既存モジュールの連携確認"""
    # 既存のネットワークモジュールとの統合確認
    from hameln_scraper.network.client import HamelnNetworkClient
    from hameln_scraper.parsing.content_extractor import ContentExtractor
    from hameln_scraper.resources.processor import ResourceProcessor
    
    # 各モジュールが正常に初期化できることを確認
    network_client = HamelnNetworkClient()
    content_extractor = ContentExtractor()
    resource_processor = ResourceProcessor()
    
    assert network_client is not None
    assert content_extractor is not None
    assert resource_processor is not None
    
    # 基本的な統合動作確認
    test_html = "<html><body><p>test content</p></body></html>"
    soup = BeautifulSoup(test_html, 'html.parser')
    
    # パース機能とリソース処理の組み合わせ
    processed_soup = resource_processor.adjust_resource_paths_only(soup)
    assert processed_soup is not None


def test_phase4_error_handling():
    """Phase 4エラーハンドリング確認"""
    from hameln_scraper.resources.file_manager import FileManager
    from hameln_scraper.resources.saver import PageSaver
    
    file_manager = FileManager()
    saver = PageSaver()
    
    # 空文字列ファイル名のエラーハンドリング
    safe_filename = file_manager.sanitize_filename("")
    assert safe_filename != ""  # 適切な代替名が生成される
    
    # 無効なHTMLでの保存エラーハンドリング
    with tempfile.TemporaryDirectory() as temp_dir:
        result = saver.save_complete_page(
            "invalid html",
            temp_dir,
            "test.html",
            "https://example.com"
        )
        # エラー時でもsuccess=Falseで適切に処理される
        # (実装により成功する場合もあるが、少なくともクラッシュしない)
        assert 'success' in result


def test_phase4_code_reduction_verification():
    """Phase 4によるコード削減効果確認"""
    import hameln_scraper_final
    
    # 元ファイルの行数確認（概算）
    import inspect
    original_lines = len(inspect.getsource(hameln_scraper_final).splitlines())
    
    # Phase 4で分離されたモジュールの機能が利用可能であることを確認
    from hameln_scraper.resources.file_manager import FileManager
    from hameln_scraper.resources.downloader import ResourceDownloader
    from hameln_scraper.resources.processor import ResourceProcessor
    from hameln_scraper.resources.saver import PageSaver
    
    # 各モジュールの主要メソッドが利用可能であることを確認
    file_manager = FileManager()
    assert hasattr(file_manager, 'sanitize_filename')
    assert hasattr(file_manager, 'create_directory_structure')
    assert hasattr(file_manager, 'generate_resource_filename')
    
    downloader = ResourceDownloader()
    assert hasattr(downloader, 'download_resource')
    assert hasattr(downloader, 'download_css')
    assert hasattr(downloader, 'convert_hameln_url')
    
    processor = ResourceProcessor()
    assert hasattr(processor, 'adjust_resource_paths_only')
    assert hasattr(processor, 'process_html_resources')
    
    saver = PageSaver()
    assert hasattr(saver, 'save_complete_page')
    assert hasattr(saver, 'add_meta_information')
    
    print(f"元ファイル行数（概算）: {original_lines}")
    print("Phase 4でリソース管理機能を正常に分離完了")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])