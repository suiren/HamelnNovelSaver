"""
ハーメルンスクレイパー統合クラス
Phase 1-4のモジュールを統合した新しいメインクラス
hameln_scraper_final.pyの完全なモジュール化版
"""

import logging
from datetime import datetime
from typing import Dict, Optional, Any, Callable

# Phase 1: 設定管理
from .config import HamelnConfig

# Phase 2: ネットワーク処理
from ..network.client import HamelnNetworkClient
from ..network.user_agent import UserAgentRotator
from ..network.compression import ResponseDecompressor

# Phase 3: HTML解析処理
from ..parsing.content_extractor import ContentExtractor
from ..parsing.url_extractor import UrlExtractor
from ..parsing.validator import PageValidator
from ..comments.handler import CommentsHandler
from ..resources.processor import ResourceProcessor
from ..novel.processor import NovelProcessor
from ..output.file_manager import FileManager

# Phase 4: リソース管理
from ..resources.file_manager import FileManager
from ..resources.downloader import ResourceDownloader
from ..resources.processor import ResourceProcessor
from ..resources.saver import PageSaver


class HamelnModularScraper:
    """
    ハーメルンスクレイパー統合クラス
    Phase 1-4で分離したモジュールを統合した新しいメインクラス
    
    従来のHamelnFinalScraperの機能を、モジュール化された構造で再実装
    hameln_scraper_final.pyと同等の機能をクリーンな構造で提供
    """
    
    def __init__(self, base_url: str = "https://syosetu.org"):
        """
        統合スクレイパー初期化
        
        Args:
            base_url: ハーメルンのベースURL
        """
        self.base_url = base_url
        self.debug_mode = True
        
        # Phase 1: 設定管理
        self.config = HamelnConfig(base_url=base_url)
        self.logger = self._setup_logging()
        
        # Phase 2: ネットワーク処理
        self.network_client = HamelnNetworkClient(base_url=base_url)
        self.user_agent_rotator = UserAgentRotator()
        self.response_decompressor = ResponseDecompressor()
        
        # Phase 3: HTML解析処理  
        self.content_extractor = ContentExtractor()
        self.url_extractor = UrlExtractor()
        self.page_validator = PageValidator()
        
        # NovelProcessorモジュール（missing属性修正）
        try:
            from ..novel.processor import NovelProcessor
            self.novel_processor = NovelProcessor(config=self.config, network_client=self.network_client)
        except ImportError:
            self.debug_log("NovelProcessorをインポートできませんでした", "WARNING")
        
        # Phase 4: リソース管理
        self.file_manager = FileManager()
        self.resource_downloader = ResourceDownloader(
            network_client=self.network_client.cloudscraper
        )
        self.resource_processor = ResourceProcessor(
            config=self.config,
            network_client=self.network_client
        )
        self.page_saver = PageSaver(
            processor=self.resource_processor
        )
        
        # 機能制御フラグ（hameln_scraper_final.pyとの互換性）
        self.enable_novel_info_saving = True   # 小説情報保存機能
        self.enable_comments_saving = True     # 感想保存機能
        
        self.logger.info("HamelnModularScraper初期化完了 - Phase 1-4モジュール統合版")
    
    def _setup_logging(self) -> logging.Logger:
        """ログ設定を初期化"""
        logging.basicConfig(
            level=logging.DEBUG if self.debug_mode else logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('hameln_modular_scraper.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def debug_log(self, message: str, level: str = "INFO"):
        """デバッグログ出力（hameln_scraper_final.pyとの互換性）"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {level}: {message}"
        print(formatted_message)
        
        # 外部ファイルにも出力
        try:
            log_file = "hameln_modular_debug.log"
            with open(log_file, 'a', encoding='utf-8') as f:
                full_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{full_timestamp}] {level}: {message}\\n")
        except Exception as e:
            print(f"ログファイル書き込みエラー: {e}")
        
        if level == "ERROR":
            self.logger.error(message)
        elif level == "WARNING":
            self.logger.warning(message)
        elif level == "DEBUG":
            self.logger.debug(message)
        else:
            self.logger.info(message)
    
    def get_page(self, url: str, timeout: int = 30) -> Dict[str, Any]:
        """
        ページ取得（Phase 2ネットワークモジュール活用）
        
        Args:
            url: 取得するURL
            timeout: タイムアウト秒数
            
        Returns:
            Dict[str, Any]: 取得結果
        """
        self.debug_log(f"ページ取得開始: {url}")
        
        try:
            # Phase 2ネットワークモジュールを使用
            # HamelnNetworkClient.get_page()はBeautifulSoupオブジェクトを返す
            soup = self.network_client.get_page(url, retry_count=3)
            
            if soup:
                # BeautifulSoupオブジェクトから文字列に変換
                html_content = str(soup)
                
                # Phase 3ページ検証モジュールを使用
                validation_result = self.page_validator.validate_page(soup, url)
                
                result = {
                    'success': True,
                    'content': html_content,
                    'soup': soup,
                    'url': url,
                    'validation': {
                        'is_valid': validation_result,
                        'content_length': len(html_content)
                    }
                }
                
                self.debug_log(f"ページ取得成功: {len(html_content)}文字")
                return result
            else:
                self.debug_log("ページ取得失敗: NoneまたはEmpty", "ERROR")
                return {
                    'success': False,
                    'error': 'ページ取得に失敗しました（レスポンスが空）',
                    'url': url
                }
            
        except Exception as e:
            self.logger.error(f"ページ取得エラー ({url}): {e}")
            return {
                'success': False,
                'error': str(e),
                'url': url
            }
    
    def extract_novel_info(self, html_content: str, url: str) -> Dict[str, Any]:
        """
        小説情報抽出（Phase 3解析モジュール活用）
        
        Args:
            html_content: HTMLコンテンツ
            url: ページURL
            
        Returns:
            Dict[str, Any]: 抽出された小説情報
        """
        self.debug_log("小説情報抽出開始")
        
        try:
            # HTMLコンテンツをBeautifulSoupオブジェクトに変換
            from bs4 import BeautifulSoup
            if isinstance(html_content, str):
                soup = BeautifulSoup(html_content, 'html.parser')
            else:
                soup = html_content
            
            # Phase 3コンテンツ抽出モジュールを使用（修正：正しい引数数）
            result = self.content_extractor.extract_novel_info(soup)
            
            # 結果を標準化された形式で返す
            if result and isinstance(result, dict):
                standardized_result = {
                    'success': True,
                    'title': result.get('title', ''),
                    'author': result.get('author', ''),
                    'summary': result.get('summary', ''),
                    'novel_info': result
                }
                self.debug_log(f"小説情報抽出成功: {standardized_result['title']}")
                return standardized_result
            else:
                self.debug_log("小説情報抽出失敗: 結果が空", "ERROR")
                return {
                    'success': False,
                    'error': '小説情報が見つかりませんでした'
                }
            
        except Exception as e:
            self.logger.error(f"小説情報抽出エラー: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def extract_chapter_content(self, html_content: str, url: str) -> Dict[str, Any]:
        """
        章内容抽出（Phase 3解析モジュール活用）
        
        Args:
            html_content: HTMLコンテンツ（文字列）
            url: ページURL
            
        Returns:
            Dict[str, Any]: 抽出された章内容
        """
        self.debug_log("章内容抽出開始")
        
        try:
            # HTMLコンテンツをBeautifulSoupオブジェクトに変換
            from bs4 import BeautifulSoup
            if isinstance(html_content, str):
                soup = BeautifulSoup(html_content, 'html.parser')
            else:
                soup = html_content
            
            # Phase 3コンテンツ抽出モジュールを使用（修正：正しい引数型）
            result = self.content_extractor.extract_chapter_content(soup, url)
            
            # 結果を標準化された形式で返す
            if result and isinstance(result, str):
                # ContentExtractorが文字列を返す場合
                standardized_result = {
                    'success': True,
                    'content': result,
                    'html': html_content,
                    'url': url,
                    'length': len(result)
                }
                self.debug_log(f"章内容抽出成功: {len(result)}文字")
                return standardized_result
            elif result and isinstance(result, dict):
                # 既に辞書形式の場合
                self.debug_log(f"章内容抽出成功: {len(result.get('content', ''))}文字")
                return result
            else:
                self.debug_log("章内容抽出失敗: 結果が空", "ERROR")
                return {
                    'success': False,
                    'error': '章内容が見つかりませんでした',
                    'url': url
                }
            
        except Exception as e:
            self.logger.error(f"章内容抽出エラー: {e}")
            return {
                'success': False,
                'error': str(e),
                'url': url
            }
    
    def get_chapter_links(self, html_content: str, base_url: str) -> Dict[str, Any]:
        """
        章リンク取得（Phase 3 URL抽出モジュール活用）
        
        Args:
            html_content: HTMLコンテンツ
            base_url: ベースURL
            
        Returns:
            Dict[str, Any]: 抽出された章リンク
        """
        self.debug_log("章リンク取得開始")
        
        try:
            # HTMLコンテンツをBeautifulSoupオブジェクトに変換
            from bs4 import BeautifulSoup
            if isinstance(html_content, str):
                soup = BeautifulSoup(html_content, 'html.parser')
            else:
                soup = html_content
            
            # Phase 3 URL抽出モジュールを使用
            result = self.url_extractor.extract_chapter_links(soup, base_url)
            
            # 結果を標準化
            if result and isinstance(result, list):
                # URLExtractorがリストを返す場合
                standardized_result = {
                    'success': True,
                    'chapter_links': result,
                    'count': len(result),
                    'base_url': base_url
                }
                self.debug_log(f"章リンク取得成功: {len(result)}個")
                return standardized_result
            elif result and isinstance(result, dict):
                # 既に辞書形式の場合
                if result.get('success'):
                    self.debug_log(f"章リンク取得成功: {len(result.get('chapter_links', []))}個")
                else:
                    self.debug_log(f"章リンク取得失敗: {result.get('error')}", "ERROR")
                return result
            else:
                self.debug_log("章リンク取得失敗: 結果が空", "ERROR")
                return {
                    'success': False,
                    'error': '章リンクが見つかりませんでした',
                    'base_url': base_url
                }
            
        except Exception as e:
            self.logger.error(f"章リンク取得エラー: {e}")
            return {
                'success': False,
                'error': str(e),
                'base_url': base_url
            }
    
    def save_complete_page(self, html_content: str, output_dir: str, 
                          filename: str, original_url: str, 
                          title: str = "") -> Dict[str, Any]:
        """
        完全ページ保存（Phase 4リソース管理モジュール活用）
        
        Args:
            html_content: HTMLコンテンツ
            output_dir: 出力ディレクトリ
            filename: ファイル名
            original_url: 元のURL
            title: ページタイトル
            
        Returns:
            Dict[str, Any]: 保存結果
        """
        self.debug_log(f"完全ページ保存開始: {filename}")
        
        try:
            # Phase 4ページ保存モジュールを使用
            result = self.page_saver.save_complete_page(
                html_content=html_content,
                output_dir=output_dir,
                filename=filename,
                original_url=original_url,
                title=title
            )
            
            if result['success']:
                self.debug_log(f"完全ページ保存成功: {result['filename']}")
            else:
                self.debug_log(f"完全ページ保存失敗: {result.get('error')}", "ERROR")
            
            return result
            
        except Exception as e:
            self.logger.error(f"完全ページ保存エラー: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def scrape_novel(self, url: str, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        小説スクレイピング統合処理（メイン機能）
        
        hameln_scraper_final.pyのscrape_novel()と互換性を保つ
        
        Args:
            url: 小説のURL
            progress_callback: 進捗コールバック関数（GUI用）
            
        Returns:
            Dict[str, Any]: スクレイピング結果
        """
        self.debug_log(f"小説スクレイピング開始: {url}")
        
        try:
            # Phase 1: 出力ディレクトリ作成
            novel_info = self.extract_novel_info_from_url(url)
            if not novel_info['success']:
                return novel_info
            
            title = novel_info.get('title', 'untitled')
            output_dir = self.file_manager.create_directory_structure(
                base_dir="./novels",
                novel_title=title
            )
            
            # Phase 2: 章リンク取得
            chapter_links_result = self.get_chapter_links_from_url(url)
            if not chapter_links_result['success']:
                return chapter_links_result
            
            chapter_links = chapter_links_result['chapter_links']
            total_chapters = len(chapter_links)
            
            # Phase 3: 各章の保存処理
            saved_chapters = []
            for i, chapter_url in enumerate(chapter_links):
                if progress_callback:
                    progress_callback(f"章 {i+1}/{total_chapters} 保存中...", 
                                    int((i / total_chapters) * 100))
                
                chapter_result = self.save_single_chapter(
                    chapter_url, 
                    output_dir, 
                    i + 1
                )
                
                if chapter_result['success']:
                    saved_chapters.append(chapter_result)
                else:
                    self.debug_log(f"章保存失敗: {chapter_url}", "WARNING")
            
            # Phase 4: 小説情報・感想保存（機能フラグ制御）
            additional_files = []
            if self.enable_novel_info_saving:
                novel_info_result = self.save_novel_info_if_enabled(url, output_dir)
                if novel_info_result.get('success'):
                    additional_files.append(novel_info_result)
            
            if self.enable_comments_saving:
                comments_result = self.save_comments_if_enabled(url, output_dir)
                if comments_result.get('success'):
                    additional_files.append(comments_result)
            
            if progress_callback:
                progress_callback("完了", 100)
            
            result = {
                'success': True,
                'title': title,
                'output_dir': output_dir,
                'saved_chapters': len(saved_chapters),
                'total_chapters': total_chapters,
                'additional_files': len(additional_files),
                'details': {
                    'chapters': saved_chapters,
                    'additional': additional_files
                }
            }
            
            self.debug_log(f"小説スクレイピング完了: {title} ({len(saved_chapters)}章)")
            return result
            
        except Exception as e:
            self.logger.error(f"小説スクレイピングエラー ({url}): {e}")
            return {
                'success': False,
                'error': str(e),
                'url': url
            }
    
    def extract_novel_info_from_url(self, url: str) -> Dict[str, Any]:
        """URLから小説情報を取得"""
        page_result = self.get_page(url)
        if not page_result['success']:
            return page_result
        
        return self.extract_novel_info(page_result['content'], url)
    
    def get_chapter_links_from_url(self, url: str) -> Dict[str, Any]:
        """URLから章リンクを取得"""
        page_result = self.get_page(url)
        if not page_result['success']:
            return page_result
        
        return self.get_chapter_links(page_result['content'], url)
    
    def save_single_chapter(self, chapter_url: str, output_dir: str, 
                           chapter_number: int) -> Dict[str, Any]:
        """
        単一章の保存処理（強化されたエラーハンドリング）
        
        Args:
            chapter_url: 章のURL
            output_dir: 出力ディレクトリ
            chapter_number: 章番号
            
        Returns:
            Dict[str, Any]: 保存結果
        """
        self.debug_log(f"第{chapter_number}話保存開始: {chapter_url}")
        
        try:
            # 章ページ取得（エラーハンドリング強化）
            page_result = self.get_page(chapter_url)
            if not page_result.get('success', False):
                error_msg = f"第{chapter_number}話のページ取得失敗: {page_result.get('error', '不明なエラー')}"
                self.debug_log(error_msg, "ERROR")
                return {
                    'success': False,
                    'error': error_msg,
                    'chapter_url': chapter_url,
                    'chapter_number': chapter_number,
                    'stage': 'page_fetch'
                }
            
            # 章内容抽出（エラーハンドリング強化）
            content_result = self.extract_chapter_content(
                page_result['content'], 
                chapter_url
            )
            if not content_result.get('success', False):
                error_msg = f"第{chapter_number}話の内容抽出失敗: {content_result.get('error', '不明なエラー')}"
                self.debug_log(error_msg, "ERROR")
                return {
                    'success': False,
                    'error': error_msg,
                    'chapter_url': chapter_url,
                    'chapter_number': chapter_number,
                    'stage': 'content_extraction'
                }
            
            # HTMLコンテンツの確認（フォールバック処理）
            html_content = content_result.get('html', page_result['content'])
            if not html_content:
                error_msg = f"第{chapter_number}話のHTMLコンテンツが空"
                self.debug_log(error_msg, "WARNING")
                # フォールバック: 元のページコンテンツを使用
                html_content = page_result['content']
            
            # 章ページ保存（エラーハンドリング強化）
            filename = f"第{chapter_number:03d}話.html"
            save_result = self.save_complete_page(
                html_content=html_content,
                output_dir=output_dir,
                filename=filename,
                original_url=chapter_url,
                title=content_result.get('title', f'第{chapter_number}話')
            )
            
            if save_result.get('success', False):
                self.debug_log(f"第{chapter_number}話保存完了: {filename}")
                return {
                    'success': True,
                    'filename': filename,
                    'chapter_number': chapter_number,
                    'chapter_url': chapter_url,
                    'title': content_result.get('title', f'第{chapter_number}話'),
                    'content_length': len(content_result.get('content', '')),
                    'file_path': save_result.get('file_path')
                }
            else:
                error_msg = f"第{chapter_number}話の保存失敗: {save_result.get('error', '不明なエラー')}"
                self.debug_log(error_msg, "ERROR")
                return {
                    'success': False,
                    'error': error_msg,
                    'chapter_url': chapter_url,
                    'chapter_number': chapter_number,
                    'stage': 'file_save'
                }
            
        except Exception as e:
            error_msg = f"第{chapter_number}話保存中の予期せぬエラー: {str(e)}"
            self.logger.error(f"単一章保存エラー ({chapter_url}): {e}")
            self.debug_log(error_msg, "ERROR")
            return {
                'success': False,
                'error': error_msg,
                'chapter_url': chapter_url,
                'chapter_number': chapter_number,
                'stage': 'unexpected_error',
                'exception_type': type(e).__name__
            }
    
    def save_novel_info_if_enabled(self, url: str, output_dir: str) -> Dict[str, Any]:
        """小説情報保存（機能フラグによる制御）"""
        if not self.enable_novel_info_saving:
            return {'success': False, 'reason': 'disabled'}
        
        # TODO: Phase 5で小説情報保存機能を実装
        self.debug_log("小説情報保存機能は Phase 5 で実装予定")
        return {'success': False, 'reason': 'not_implemented_yet'}
    
    def save_comments_if_enabled(self, url: str, output_dir: str) -> Dict[str, Any]:
        """感想保存（機能フラグによる制御）"""
        if not self.enable_comments_saving:
            return {'success': False, 'reason': 'disabled'}
        
        # TODO: Phase 5で感想保存機能を実装
        self.debug_log("感想保存機能は Phase 5 で実装予定")
        return {'success': False, 'reason': 'not_implemented_yet'}
    
    def detect_comments_pagination(self, soup, base_url=""):
        """感想ページのページネーションを検出"""
        return self.comments_handler.detect_comments_pagination(soup, base_url)
    
    def extract_page_number(self, url):
        """URLからページ番号を抽出"""
        return self.comments_handler.extract_page_number(url)
    
    def get_all_comments_pages(self, base_url, output_dir=None, title=None, index_file_name=None):
        """複数ページの感想を全て取得して統合"""
        return self.comments_handler.get_all_comments_pages(base_url)
    
    def extract_comments_content(self, soup):
        """感想コンテンツを抽出"""
        return self.comments_handler.extract_comments_content(soup)
    
    def save_comments_page(self, comments_url, output_dir, title, index_file_name=None):
        """感想ページを保存"""
        return self.comments_handler.save_comments_page(comments_url, output_dir, title, index_file_name)
    
    def get_page(self, url, **kwargs):
        """ページを取得"""
        return self.network_client.get_page(url, **kwargs)
    
    def download_resource(self, url, output_dir, **kwargs):
        """リソースをダウンロード"""
        return self.resource_processor.download_resource(url, output_dir, **kwargs)
    
    def process_html_resources(self, soup, base_url, output_dir, **kwargs):
        """HTMLリソースを処理"""
        return self.resource_processor.process_html_resources(soup, output_dir)
    
    def extract_novel_info(self, html_content, url):
        """小説情報を抽出"""
        from bs4 import BeautifulSoup
        if isinstance(html_content, str):
            soup = BeautifulSoup(html_content, 'html.parser')
        else:
            soup = html_content
        
        info = self.novel_processor.extract_novel_info(soup)
        
        # テストが期待する辞書形式で返す
        if info and isinstance(info, dict) and info.get('title'):
            return {
                'success': True,
                'title': info.get('title', ''),
                'author': info.get('author', ''),
                'genre': info.get('genre', ''),
                'summary': info.get('summary', ''),
                'tags': info.get('tags', []),
                'url': url
            }
        else:
            return {
                'success': False,
                'title': '',
                'author': '',
                'genre': '',
                'summary': '',
                'tags': [],
                'url': url,
                'error': '小説情報を抽出できませんでした'
            }
    
    def get_chapter_links(self, html_content, base_url):
        """章リンクを取得"""
        from bs4 import BeautifulSoup
        if isinstance(html_content, str):
            soup = BeautifulSoup(html_content, 'html.parser')
        else:
            soup = html_content
        
        links = self.url_extractor.get_chapter_links(soup, base_url)
        
        # テストが期待する形式で返す
        return {
            'success': True,
            'chapter_links': [link['url'] if isinstance(link, dict) else link for link in links]
        }
    
    
    def save_complete_page(self, html_content=None, output_dir=None, filename=None, original_url=None, title=None, **kwargs):
        """完全なページを保存"""
        return self.page_saver.save_complete_page(
            html_content=html_content,
            output_dir=output_dir,
            filename=filename,
            original_url=original_url,
            title=title,
            **kwargs
        )
    
    def fix_local_navigation_links(self, soup, chapter_mapping):
        """ローカルナビゲーションリンクを修正"""
        return self.file_manager.fix_local_navigation_links(soup, chapter_mapping)

    
    def close(self):
        """リソース解放（hameln_scraper_final.pyとの互換性）"""
        try:
            self.network_client.close()
            self.debug_log("HamelnModularScraper リソース解放完了")
        except Exception as e:
            self.logger.error(f"リソース解放エラー: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """キャッシュ統計取得（hameln_scraper_final.pyとの互換性）"""
        try:
            network_stats = self.network_client.get_status()
            resource_stats = self.resource_downloader.get_cache_stats()
            
            return {
                'network': network_stats,
                'resources': resource_stats,
                'modules': {
                    'phase1_config': True,
                    'phase2_network': True,
                    'phase3_parsing': True,
                    'phase4_resources': True
                }
            }
        except Exception as e:
            self.logger.error(f"キャッシュ統計取得エラー: {e}")
            return {'error': str(e)}


# 後方互換性のためのエイリアス
HamelnScraper = HamelnModularScraper

# 既存システムとの互換性確保
class HamelnFinalScraper(HamelnModularScraper):
    """
    hameln_scraper_final.pyとの完全互換性を保つラッパークラス
    既存のGUIアプリケーション（hameln_gui.py）との連携用
    """
    
    def __init__(self, base_url: str = "https://syosetu.org"):
        """hameln_scraper_final.pyと同じインターフェース"""
        super().__init__(base_url)
        self.debug_log("HamelnFinalScraper互換レイヤー初期化完了")
