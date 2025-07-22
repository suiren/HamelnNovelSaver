"""
ハーメルンスクレイパー統合クラス
Phase 1-4のモジュールを統合した新しいメインクラス
hameln_scraper_final.pyの完全なモジュール化版
"""

import os
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

# Phase 4: リソース管理
from ..resources.file_manager import FileManager as ResourceFileManager
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
        self.file_manager = ResourceFileManager()
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
            
            # Phase 3 URL抽出モジュールを使用（新しいget_chapter_linksメソッド）
            result = self.url_extractor.get_chapter_links(soup, base_url)
            
            # 新しい辞書形式の結果を処理
            if result and isinstance(result, dict):
                # エラーがある場合
                if 'error' in result:
                    self.debug_log(f"章リンク取得失敗: {result.get('error')}", "ERROR")
                    return {
                        'success': False,
                        'error': result.get('error'),
                        'base_url': base_url
                    }
                
                # 成功の場合
                chapter_links = result.get('chapter_links', [])
                index_page = result.get('index_page', None)
                
                # 章リンクをURL文字列に変換（後方互換性のため）
                chapter_urls = [link['url'] if isinstance(link, dict) else link for link in chapter_links]
                
                standardized_result = {
                    'success': True,
                    'chapter_links': chapter_urls,
                    'index_page': index_page,  # 目次ページ情報を追加
                    'count': len(chapter_urls),
                    'base_url': base_url
                }
                self.debug_log(f"章リンク取得成功: {len(chapter_urls)}個、目次ページ: {index_page['title'] if index_page else 'なし'}")
                return standardized_result
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
            index_page = chapter_links_result.get('index_page')
            total_chapters = len(chapter_links)
            
            # Phase 2.5: 目次ページ保存処理
            index_saved = False
            if index_page and index_page.get('url'):
                self.debug_log(f"目次ページ保存開始: {index_page['title']}")
                index_result = self.save_index_page(
                    index_page['url'], 
                    output_dir, 
                    index_page['title']
                )
                if index_result.get('success'):
                    index_saved = True
                    self.debug_log(f"目次ページ保存完了: index.html")
                else:
                    self.debug_log(f"目次ページ保存失敗: {index_result.get('error')}", "WARNING")
            
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
                # 目次ページから必要な情報を取得
                main_page_result = self.get_page(url)
                if main_page_result.get('success'):
                    from bs4 import BeautifulSoup
                    main_soup = BeautifulSoup(main_page_result['content'], 'html.parser')
                    
                    # ファイル名情報を準備（日本語ファイル名対応）
                    index_filename = "目次.html" if index_saved else None
                    comments_filename = None  # Phase 5で実装予定
                    
                    novel_info_result = self.save_novel_info_if_enabled(
                        url, 
                        output_dir, 
                        soup=main_soup, 
                        novel_title=title,
                        index_file_name=index_filename,
                        comments_file_name=comments_filename
                    )
                    if novel_info_result.get('success'):
                        additional_files.append(novel_info_result)
                        self.debug_log(f"📝 小説情報ページ保存完了: {novel_info_result.get('filename')}")
                    else:
                        self.debug_log(f"⚠️ 小説情報ページ保存失敗: {novel_info_result.get('error')}", "WARNING")
                else:
                    self.debug_log("目次ページの再取得に失敗しました", "WARNING")
            
            if self.enable_comments_saving:
                comments_result = self.save_comments_if_enabled(url, output_dir)
                if comments_result.get('success'):
                    additional_files.append(comments_result)
                    
                    # 感想ページのナビゲーション修正
                    self.debug_log("感想ページナビゲーション修正開始")
                    
                    # ページネーションリンク修正
                    pagination_result = self.fix_comments_pagination_links(output_dir)
                    if pagination_result.get('success'):
                        pagination_fixed = pagination_result.get('total_links_fixed', 0)
                        self.debug_log(f"感想ページネーション修正完了: {pagination_fixed}個のリンク")
                    else:
                        self.debug_log(f"感想ページネーション修正失敗: {pagination_result.get('reason', 'unknown')}", "WARNING")
                    
                    # 感想内章リンク修正
                    import re
                    novel_id_match = re.search(r'/novel/(\d+)', url)
                    if novel_id_match and saved_chapters:
                        novel_id = novel_id_match.group(1)
                        chapter_links_result = self.fix_comments_chapter_links(output_dir, novel_id, saved_chapters)
                        if chapter_links_result.get('success'):
                            chapter_links_fixed = chapter_links_result.get('total_links_fixed', 0)
                            self.debug_log(f"感想章リンク修正完了: {chapter_links_fixed}個のリンク")
                        else:
                            self.debug_log(f"感想章リンク修正失敗: {chapter_links_result.get('reason', 'unknown')}", "WARNING")
            
            # Phase 4: ローカルナビゲーションリンク修正
            if saved_chapters:
                self.debug_log("ローカルナビゲーションリンク修正開始")
                navigation_fixed = self.fix_local_navigation_for_all_chapters(
                    saved_chapters, output_dir
                )
                self.debug_log(f"ローカルナビゲーションリンク修正完了: {navigation_fixed}個のファイル")
                
                # 目次ページの章リンクも修正
                self.debug_log("目次ページ章リンク修正開始")
                index_link_result = self.fix_index_page_chapter_links(output_dir, saved_chapters)
                if index_link_result.get('success'):
                    links_fixed = index_link_result.get('links_fixed', 0)
                    self.debug_log(f"目次ページ章リンク修正完了: {links_fixed}個のリンクを変換")
                else:
                    reason = index_link_result.get('reason', 'unknown')
                    self.debug_log(f"目次ページ章リンク修正失敗: {reason}", "WARNING")
                
                # クロスページリンク修正（目次・小説情報・感想・章間の相互リンク）
                self.debug_log("クロスページリンク修正開始")
                cross_link_result = self.fix_cross_page_links(output_dir, url)
                if cross_link_result.get('success'):
                    total_cross_links = cross_link_result.get('total_links_fixed', 0)
                    self.debug_log(f"クロスページリンク修正完了: {total_cross_links}個のリンクを修正")
                else:
                    reason = cross_link_result.get('reason', 'unknown')
                    error = cross_link_result.get('error', '')
                    self.debug_log(f"クロスページリンク修正失敗: {reason} {error}", "WARNING")
            
            if progress_callback:
                progress_callback("完了", 100)
            
            result = {
                'success': True,
                'title': title,
                'output_dir': output_dir,
                'saved_chapters': len(saved_chapters),
                'total_chapters': total_chapters,
                'index_page_saved': index_saved,
                'additional_files': len(additional_files),
                'details': {
                    'chapters': saved_chapters,
                    'additional': additional_files,
                    'index_page': index_page if index_saved else None
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
    
    def extract_novel_info_url(self, soup) -> Optional[str]:
        """目次ページから小説情報ページのURLを抽出"""
        try:
            # topicPathから小説情報リンクを検索
            topic_path = soup.find('ol', class_='topicPath')
            if topic_path:
                info_link = topic_path.find('a', href=lambda x: x and 'mode=ss_detail' in x)
                if info_link:
                    href = info_link.get('href')
                    if href.startswith('?'):
                        # 相対URLを絶対URLに変換
                        return f"https://syosetu.org/{href}"
                    elif href.startswith('//'):
                        # プロトコル相対URLをHTTPS絶対URLに変換
                        return f"https:{href}"
                    elif href.startswith('/'):
                        # ルート相対URLを絶対URLに変換
                        return f"https://syosetu.org{href}"
                    return href
            
            self.debug_log("小説情報URLが見つかりませんでした", "WARNING")
            return None
        except Exception as e:
            self.debug_log(f"小説情報URL抽出エラー: {e}", "ERROR")
            return None

    def fix_novel_info_page_links(self, soup, index_file_name: Optional[str] = None, comments_file_name: Optional[str] = None):
        """小説情報ページのリンクを修正"""
        try:
            # 目次へのリンクを修正
            if index_file_name:
                index_links = soup.find_all('a', href=lambda x: x and 'novel/' in x and x.endswith('/'))
                for link in index_links:
                    link['href'] = index_file_name
                    self.debug_log(f"目次リンク修正: {link['href']} -> {index_file_name}")
            
            # 感想ページへのリンクを修正
            if comments_file_name:
                comments_links = soup.find_all('a', href=lambda x: x and 'mode=impression' in x)
                for link in comments_links:
                    link['href'] = comments_file_name
                    self.debug_log(f"感想リンク修正: {link['href']} -> {comments_file_name}")
            
            return soup
        except Exception as e:
            self.debug_log(f"小説情報ページリンク修正エラー: {e}", "ERROR")
            return soup

    def save_novel_info_page(self, info_url: str, output_dir: str, novel_title: str, 
                           index_file_name: Optional[str] = None, 
                           comments_file_name: Optional[str] = None) -> Optional[str]:
        """小説情報ページを取得・保存"""
        try:
            self.debug_log(f"小説情報ページを取得中: {info_url}")
            
            # 小説情報ページを取得
            page_result = self.get_page(info_url)
            if not page_result.get('success', False):
                self.debug_log("小説情報ページの取得に失敗しました", "ERROR")
                return None
            
            # BeautifulSoupオブジェクトを作成
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(page_result['content'], 'html.parser')
            
            # 保存前に小説情報ページのリンク修正
            soup = self.fix_novel_info_page_links(soup, index_file_name, comments_file_name)
            
            # ファイル名を生成
            safe_title = self.file_manager.sanitize_filename(novel_title)
            info_filename = f"{safe_title} - 小説情報.html"
            
            # 保存処理
            info_file_result = self.save_complete_page(
                html_content=str(soup),
                output_dir=output_dir,
                filename=info_filename,
                original_url=info_url,
                title=f"{novel_title} - 小説情報"
            )
            
            if info_file_result.get('success'):
                file_path = info_file_result.get('file_path')
                self.debug_log(f"小説情報ページ保存完了: {os.path.basename(file_path) if file_path else info_filename}")
                return file_path
            else:
                self.debug_log("小説情報ページの保存に失敗しました", "ERROR")
                return None
                
        except Exception as e:
            self.debug_log(f"小説情報ページ保存エラー: {e}", "ERROR")
            return None

    def save_novel_info_if_enabled(self, url: str, output_dir: str, soup = None, novel_title: str = "",
                                 index_file_name: Optional[str] = None,
                                 comments_file_name: Optional[str] = None) -> Dict[str, Any]:
        """小説情報保存（機能フラグによる制御）"""
        if not self.enable_novel_info_saving:
            return {'success': False, 'reason': 'disabled'}
        
        try:
            self.debug_log("小説情報ページを保存中...")
            
            # soupが提供されていない場合は取得
            if soup is None:
                page_result = self.get_page(url)
                if not page_result.get('success', False):
                    return {'success': False, 'error': '目次ページの取得失敗'}
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(page_result['content'], 'html.parser')
            
            # 小説情報URLを抽出
            info_url = self.extract_novel_info_url(soup)
            if not info_url:
                return {'success': False, 'error': '小説情報URLが見つかりません'}
            
            # 小説情報ページを保存
            info_file_path = self.save_novel_info_page(
                info_url, output_dir, novel_title, 
                index_file_name, comments_file_name
            )
            
            if info_file_path:
                return {
                    'success': True,
                    'file_path': info_file_path,
                    'filename': os.path.basename(info_file_path),
                    'url': info_url
                }
            else:
                return {'success': False, 'error': '小説情報ページの保存失敗'}
                
        except Exception as e:
            self.debug_log(f"小説情報保存エラー: {e}", "ERROR")
            return {'success': False, 'error': str(e)}
    
    def save_comments_if_enabled(self, url: str, output_dir: str) -> Dict[str, Any]:
        """感想保存（機能フラグによる制御）"""
        if not self.enable_comments_saving:
            return {'success': False, 'reason': 'disabled'}
        
        try:
            # 感想URLを抽出
            comments_url = self.extract_comments_url(url)
            if not comments_url:
                self.debug_log("感想URLが見つかりませんでした", "WARNING")
                return {'success': False, 'reason': 'no_comments_url'}
            
            # 小説タイトルを取得（フォルダ名用）
            novel_title = self.extract_novel_title_from_index(output_dir)
            if not novel_title:
                novel_title = "小説"  # フォールバック
                
            # 感想ページを保存
            result = self.save_comments_page(comments_url, output_dir, novel_title)
            
            if result:
                return {
                    'success': True,
                    'saved_files': result.get('saved_files', []),
                    'total_pages': result.get('total_pages', 0),
                    'comments_url': comments_url
                }
            else:
                return {'success': False, 'reason': 'save_failed'}
                
        except Exception as e:
            self.debug_log(f"感想保存エラー: {e}", "ERROR")
            return {'success': False, 'error': str(e)}
    
    def extract_comments_url(self, base_url: str) -> str:
        """目次ページから感想ページのURLを抽出"""
        try:
            # ベースURLから感想URLを構築
            if 'syosetu.org/novel/' in base_url:
                # 小説IDを抽出
                import re
                match = re.search(r'/novel/(\d+)', base_url)
                if match:
                    novel_id = match.group(1)
                    comments_url = f"https://syosetu.org/?mode=review&nid={novel_id}"
                    self.debug_log(f"感想URL構築: {comments_url}")
                    return comments_url
            
            self.debug_log("感想URLの構築に失敗しました", "WARNING")
            return ""
            
        except Exception as e:
            self.debug_log(f"感想URL抽出エラー: {e}", "ERROR")
            return ""
    
    def extract_novel_title_from_index(self, output_dir: str) -> str:
        """目次ファイルから小説タイトルを抽出"""
        try:
            index_file = os.path.join(output_dir, "目次.html")
            if os.path.exists(index_file):
                with open(index_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(content, 'html.parser')
                
                # タイトル抽出の優先順序
                title_selectors = [
                    'span[itemprop="name"]',
                    'title',
                    'h1',
                    '.ss span[style*="font-size:150%"]'
                ]
                
                for selector in title_selectors:
                    title_elem = soup.select_one(selector)
                    if title_elem:
                        title = title_elem.get_text().strip()
                        if title and title != "ハーメルン":
                            # "- ハーメルン"を除去
                            title = title.replace(" - ハーメルン", "").strip()
                            self.debug_log(f"小説タイトル抽出: {title}")
                            return title
            
            return ""
            
        except Exception as e:
            self.debug_log(f"小説タイトル抽出エラー: {e}", "ERROR")
            return ""
    
    def save_comments_page(self, comments_url: str, output_dir: str, novel_title: str) -> Dict[str, Any]:
        """感想ページを各ページ個別に保存"""
        try:
            self.debug_log(f"感想ページを取得中: {comments_url}")
            
            # 感想保存フォルダを作成
            import re
            safe_title = re.sub(r'[<>:"/\\|?*]', '_', novel_title)
            comments_dir = os.path.join(output_dir, "感想")
            os.makedirs(comments_dir, exist_ok=True)
            self.debug_log(f"感想保存フォルダ作成: {comments_dir}")
            
            # 最初のページを取得してページネーション検出
            first_page_soup = self.get_page_raw(comments_url)
            if not first_page_soup:
                self.debug_log("感想ページの取得に失敗しました", "ERROR")
                return {'success': False, 'reason': 'page_fetch_failed'}
            
            # ページネーションを検出
            page_links = self.detect_comments_pagination(first_page_soup, comments_url)
            if not page_links:
                # ページネーションが無い場合は1ページのみ
                page_links = [comments_url]
            
            self.debug_log(f"感想ページ数: {len(page_links)}ページ")
            
            saved_files = []
            
            # 各ページを個別に保存
            for page_num, page_url in enumerate(page_links, 1):
                self.debug_log(f"感想ページ {page_num}/{len(page_links)} を保存中: {page_url}")
                
                # ページを取得
                if page_num == 1:
                    page_soup = first_page_soup
                else:
                    import time
                    time.sleep(2)  # サーバー負荷軽減
                    page_soup = self.get_page_raw(page_url)
                    if not page_soup:
                        self.debug_log(f"感想ページ {page_num} の取得に失敗", "WARNING")
                        continue
                
                # ファイル名生成
                comments_filename = f"感想 - ページ{page_num}.html"
                page_file_path = os.path.join(comments_dir, comments_filename)
                
                # リソース処理とページ保存
                self.process_html_resources(page_soup, page_url, comments_dir)
                
                # HTMLを保存
                html_content = str(page_soup)
                with open(page_file_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                saved_files.append(page_file_path)
                self.debug_log(f"感想ページ {page_num} 保存完了: {page_file_path}")
            
            return {
                'success': True,
                'saved_files': saved_files,
                'total_pages': len(page_links),
                'comments_dir': comments_dir
            }
            
        except Exception as e:
            self.debug_log(f"感想ページ保存エラー: {e}", "ERROR")
            return {'success': False, 'error': str(e)}
    
    def fix_comments_pagination_links(self, output_dir: str) -> Dict[str, Any]:
        """
        感想ページのページネーションリンクを修正
        
        Args:
            output_dir: 出力ディレクトリ
            
        Returns:
            Dict[str, Any]: 修正結果
        """
        self.debug_log("感想ページネーションリンク修正開始")
        
        try:
            comments_dir = os.path.join(output_dir, "感想")
            if not os.path.exists(comments_dir):
                return {'success': False, 'reason': 'comments_dir_not_found'}
            
            total_links_fixed = 0
            files_processed = 0
            
            # 感想ページファイルを検索
            for filename in os.listdir(comments_dir):
                if filename.endswith('.html') and '感想 - ページ' in filename:
                    file_path = os.path.join(comments_dir, filename)
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    links_fixed = 0
                    
                    # ページネーションリンクを検索・修正
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        
                        # ページネーションパターンをチェック
                        if 'mode=review' in href and 'page=' in href:
                            # ページ番号を抽出
                            import re
                            page_match = re.search(r'page=(\d+)', href)
                            if page_match:
                                page_num = page_match.group(1)
                                local_filename = f"感想 - ページ{page_num}.html"
                                
                                # ローカルファイル名に置換
                                link['href'] = local_filename
                                links_fixed += 1
                                self.debug_log(f"感想ページネーション修正: {href} → {local_filename}")
                    
                    if links_fixed > 0:
                        # 修正された内容を保存
                        modified_content = str(soup)
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(modified_content)
                        
                    total_links_fixed += links_fixed
                    files_processed += 1
                    
                    if links_fixed > 0:
                        self.debug_log(f"感想ページ修正完了: {filename} ({links_fixed}個のリンク)")
            
            self.debug_log(f"感想ページネーションリンク修正完了: {total_links_fixed}個のリンク修正")
            
            return {
                'success': True,
                'total_links_fixed': total_links_fixed,
                'files_processed': files_processed
            }
            
        except Exception as e:
            self.debug_log(f"感想ページネーションリンク修正エラー: {e}", "ERROR")
            return {'success': False, 'error': str(e)}
    
    def fix_comments_chapter_links(self, output_dir: str, novel_id: str, saved_chapters: list) -> Dict[str, Any]:
        """
        感想ページ内の章リンクを相対パスに修正
        
        Args:
            output_dir: 出力ディレクトリ
            novel_id: 小説ID
            saved_chapters: 保存済み章リスト
            
        Returns:
            Dict[str, Any]: 修正結果
        """
        self.debug_log("感想ページ章リンク修正開始")
        
        try:
            comments_dir = os.path.join(output_dir, "感想")
            if not os.path.exists(comments_dir):
                return {'success': False, 'reason': 'comments_dir_not_found'}
            
            # 章マッピングを構築（URL → 相対パス）
            chapter_mapping = {}
            for chapter in saved_chapters:
                if chapter.get('success') and chapter.get('chapter_url') and chapter.get('filename'):
                    chapter_url = chapter['chapter_url']
                    # 感想フォルダからの相対パス
                    relative_path = f"../{chapter['filename']}"
                    chapter_mapping[chapter_url] = relative_path
            
            self.debug_log(f"章マッピング: {len(chapter_mapping)}個")
            
            total_links_fixed = 0
            files_processed = 0
            
            # 感想ページファイルを検索
            for filename in os.listdir(comments_dir):
                if filename.endswith('.html') and '感想 - ページ' in filename:
                    file_path = os.path.join(comments_dir, filename)
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    links_fixed = 0
                    
                    # 章リンクを検索・修正
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        
                        # 章リンクパターンをチェック
                        if href in chapter_mapping:
                            relative_path = chapter_mapping[href]
                            link['href'] = relative_path
                            links_fixed += 1
                            self.debug_log(f"感想章リンク修正: {href} → {relative_path}")
                    
                    if links_fixed > 0:
                        # 修正された内容を保存
                        modified_content = str(soup)
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(modified_content)
                        
                    total_links_fixed += links_fixed
                    files_processed += 1
                    
                    if links_fixed > 0:
                        self.debug_log(f"感想章リンク修正完了: {filename} ({links_fixed}個のリンク)")
            
            self.debug_log(f"感想章リンク修正完了: {total_links_fixed}個のリンク修正")
            
            return {
                'success': True,
                'total_links_fixed': total_links_fixed,
                'files_processed': files_processed
            }
            
        except Exception as e:
            self.debug_log(f"感想章リンク修正エラー: {e}", "ERROR")
            return {'success': False, 'error': str(e)}
    
    def detect_comments_pagination(self, soup, base_url=""):
        """感想ページのページネーションを検出"""
        try:
            page_links = []
            
            # ページネーション検出パターン
            pagination_selectors = [
                'div.pagination a',
                'div.pager a', 
                'div.page-nav a',
                'a[href*="mode=review"][href*="page="]',
                'a[href*="&page="]'
            ]
            
            for selector in pagination_selectors:
                pagination_links = soup.select(selector)
                if pagination_links:
                    self.debug_log(f"ページネーション発見: {selector} ({len(pagination_links)}個のリンク)")
                    
                    for link in pagination_links:
                        href = link.get('href')
                        if href and 'page=' in href:
                            # 相対URLを絶対URLに変換
                            if href.startswith('?'):
                                # ?page=2 形式
                                full_url = base_url.split('?')[0] + href
                            elif href.startswith('./'):
                                # ./?page=2 形式
                                full_url = base_url.replace(base_url.split('/')[-1], href[2:])
                            elif href.startswith('http'):
                                # 絶対URL
                                full_url = href
                            else:
                                # その他の相対URL
                                base_path = '/'.join(base_url.split('/')[:-1])
                                full_url = f"{base_path}/{href}"
                            
                            if full_url not in page_links:
                                page_links.append(full_url)
                    
                    if page_links:
                        break  # 最初に見つかったパターンを使用
            
            # ベースURLも含める（1ページ目として）
            if base_url not in page_links:
                page_links.insert(0, base_url)
            
            # ソートしてページ順序を確保
            page_links.sort()
            
            self.debug_log(f"感想ページネーション検出完了: {len(page_links)}ページ")
            return page_links
            
        except Exception as e:
            self.debug_log(f"ページネーション検出エラー: {e}", "ERROR")
            return [base_url] if base_url else []
    
    def extract_page_number(self, url):
        """URLからページ番号を抽出"""
        try:
            import re
            match = re.search(r'page=(\d+)', url)
            if match:
                return int(match.group(1))
            return 1  # デフォルトは1ページ目
        except:
            return 1
    
    def get_all_comments_pages(self, base_url, output_dir=None, title=None, index_file_name=None):
        """複数ページの感想を全て取得して統合"""
        # 現在は save_comments_page() で実装されているため、こちらは使用しない
        return []
    
    def extract_comments_content(self, soup):
        """感想コンテンツを抽出"""
        # 現在はページ全体を保存しているため、特別な抽出は不要
        return str(soup)
    
    
    def get_page_raw(self, url, **kwargs):
        """ページを取得（生のBeautifulSoupオブジェクト）"""
        return self.network_client.get_page(url, **kwargs)
    
    def download_resource(self, url, output_dir, **kwargs):
        """リソースをダウンロード"""
        return self.resource_processor.download_resource(url, output_dir, **kwargs)
    
    def process_html_resources(self, soup, base_url, output_dir, **kwargs):
        """HTMLリソースを処理"""
        return self.resource_processor.process_html_resources(soup, output_dir)
    
    # DUPLICATE REMOVED: def extract_novel_info(self, html_content, url):
    #         """小説情報を抽出"""
    #         from bs4 import BeautifulSoup
    #         if isinstance(html_content, str):
    #             soup = BeautifulSoup(html_content, 'html.parser')
    #         else:
    #             soup = html_content
        
    #         info = self.novel_processor.extract_novel_info(soup)
        
        # テストが期待する辞書形式で返す
    #         if info and isinstance(info, dict) and info.get('title'):
    #             return {
    #                 'success': True,
    #                 'title': info.get('title', ''),
    #                 'author': info.get('author', ''),
    #                 'genre': info.get('genre', ''),
    #                 'summary': info.get('summary', ''),
    #                 'tags': info.get('tags', []),
    #                 'url': url
    #             }
    #         else:
    #             return {
    #                 'success': False,
    #                 'title': '',
    #                 'author': '',
    #                 'genre': '',
    #                 'summary': '',
    #                 'tags': [],
    #                 'url': url,
    #                 'error': '小説情報を抽出できませんでした'
    #             }
    
    # DUPLICATE REMOVED: def get_chapter_links(self, html_content, base_url):
    #         """章リンクを取得"""
    #         from bs4 import BeautifulSoup
    #         if isinstance(html_content, str):
    #             soup = BeautifulSoup(html_content, 'html.parser')
    #         else:
    #             soup = html_content
        
    #         links = self.url_extractor.get_chapter_links(soup, base_url)
        
        # テストが期待する形式で返す
    #         return {
    #             'success': True,
    #             'chapter_links': [link['url'] if isinstance(link, dict) else link for link in links]
    #         }
    
    
    # DUPLICATE REMOVED: def save_complete_page(self, html_content=None, output_dir=None, filename=None, original_url=None, title=None, **kwargs):
    #         """完全なページを保存"""
    #         return self.page_saver.save_complete_page(
    #             html_content=html_content,
    #             output_dir=output_dir,
    #             filename=filename,
    #             original_url=original_url,
    #             title=title,
    #             **kwargs
    #         )
    
    def save_index_page(self, index_url: str, output_dir: str, title: str = "目次") -> Dict[str, Any]:
        """
        目次ページをindex.htmlとして保存
        
        Args:
            index_url: 目次ページのURL
            output_dir: 出力ディレクトリ
            title: ページタイトル
            
        Returns:
            Dict[str, Any]: 保存結果
        """
        self.debug_log(f"目次ページ保存開始: {index_url}")
        
        try:
            # 目次ページ取得
            page_result = self.get_page(index_url)
            if not page_result.get('success', False):
                error_msg = f"目次ページの取得失敗: {page_result.get('error', '不明なエラー')}"
                self.debug_log(error_msg, "ERROR")
                return {
                    'success': False,
                    'error': error_msg,
                    'url': index_url
                }
            
            # 日本語ファイル名で保存（ユーザビリティ向上）
            filename = "目次.html"
            save_result = self.save_complete_page(
                html_content=page_result['content'],
                output_dir=output_dir,
                filename=filename,
                original_url=index_url,
                title=title
            )
            
            if save_result.get('success', False):
                self.debug_log(f"目次ページ保存完了: {filename}")
                return {
                    'success': True,
                    'filename': filename,
                    'url': index_url,
                    'title': title,
                    'file_path': save_result.get('file_path')
                }
            else:
                error_msg = f"目次ページの保存失敗: {save_result.get('error', '不明なエラー')}"
                self.debug_log(error_msg, "ERROR")
                return {
                    'success': False,
                    'error': error_msg,
                    'url': index_url
                }
                
        except Exception as e:
            error_msg = f"目次ページ保存中の予期せぬエラー: {str(e)}"
            self.logger.error(f"目次ページ保存エラー ({index_url}): {e}")
            self.debug_log(error_msg, "ERROR")
            return {
                'success': False,
                'error': error_msg,
                'url': index_url,
                'exception_type': type(e).__name__
            }
    
    def fix_local_navigation_for_all_chapters(self, saved_chapters: list, output_dir: str) -> int:
        """
        すべての保存済み章ファイルでローカルナビゲーションリンクを修正
        
        Args:
            saved_chapters: 保存済み章リスト
            output_dir: 出力ディレクトリ
            
        Returns:
            int: 修正されたファイル数
        """
        self.debug_log("全章でのローカルナビゲーションリンク修正開始")
        
        try:
            # 章マッピングを構築（URL → ローカルファイル名）
            chapter_mapping = {}
            for chapter in saved_chapters:
                if chapter.get('success') and chapter.get('chapter_url') and chapter.get('filename'):
                    chapter_url = chapter['chapter_url']
                    filename = chapter['filename']
                    chapter_mapping[chapter_url] = filename
            
            # 目次ページのマッピングを明示的に追加
            # 目次ページURLを抽出（通常は最初の章URLからベースURLを推測）
            if saved_chapters and len(saved_chapters) > 0:
                first_chapter_url = saved_chapters[0].get('chapter_url', '')
                if first_chapter_url:
                    # 例: https://syosetu.org/novel/380014/1.html → https://syosetu.org/novel/380014/
                    import re
                    base_url_match = re.match(r'(https://syosetu\.org/novel/\d+/).*', first_chapter_url)
                    if base_url_match:
                        base_url = base_url_match.group(1)
                        chapter_mapping[base_url] = "目次.html"
                        self.debug_log(f"目次ページマッピング追加: {base_url} → 目次.html")
            
            self.debug_log(f"章マッピング構築完了: {len(chapter_mapping)}個のマッピング")
            
            # 各章ファイルを修正
            fixed_count = 0
            for chapter in saved_chapters:
                if not chapter.get('success'):
                    continue
                    
                filename = chapter.get('filename')
                if not filename:
                    continue
                
                file_path = os.path.join(output_dir, filename)
                if not os.path.exists(file_path):
                    self.debug_log(f"ファイルが見つかりません: {file_path}", "WARNING")
                    continue
                
                # ファイルを読み込み、リンクを修正
                try:
                    from bs4 import BeautifulSoup
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # ローカルナビゲーションリンク修正
                    modified_soup = self.file_manager.fix_local_navigation_links(
                        soup, 
                        chapter_mapping,
                        chapter.get('chapter_url'),
                        None
                    )
                    
                    # 修正済みファイルを保存
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(str(modified_soup))
                    
                    fixed_count += 1
                    self.debug_log(f"ローカルナビゲーション修正完了: {filename}")
                    
                except Exception as e:
                    self.debug_log(f"ファイル修正エラー ({filename}): {e}", "ERROR")
                    continue
            
            self.debug_log(f"全章ローカルナビゲーション修正完了: {fixed_count}/{len(saved_chapters)}ファイル")
            return fixed_count
            
        except Exception as e:
            self.logger.error(f"ローカルナビゲーション一括修正エラー: {e}")
            return 0
    
    def fix_local_navigation_links(self, soup, chapter_mapping):
        """ローカルナビゲーションリンクを修正"""
        return self.file_manager.fix_local_navigation_links(soup, chapter_mapping)

    def fix_index_page_chapter_links(self, output_dir: str, saved_chapters: list) -> Dict[str, Any]:
        """
        目次ページの章リンクを外部URL → ローカルファイル名に変換
        
        Args:
            output_dir: 出力ディレクトリ
            saved_chapters: 保存済み章リスト
            
        Returns:
            Dict[str, Any]: 修正結果
        """
        self.debug_log("目次ページの章リンク変換開始")
        
        try:
            # 目次ファイルパス
            index_file_path = os.path.join(output_dir, "目次.html")
            
            if not os.path.exists(index_file_path):
                return {'success': False, 'reason': 'index_file_not_found', 'path': index_file_path}
            
            # 章マッピングを構築（URL → ローカルファイル名）
            chapter_mapping = {}
            for chapter in saved_chapters:
                if chapter.get('success') and chapter.get('chapter_url') and chapter.get('filename'):
                    chapter_url = chapter['chapter_url']
                    filename = chapter['filename']
                    chapter_mapping[chapter_url] = filename
            
            if not chapter_mapping:
                self.debug_log("章マッピングが空です", "WARNING")
                return {'success': False, 'reason': 'no_chapter_mapping'}
            
            self.debug_log(f"章マッピング: {len(chapter_mapping)}個のリンク")
            
            # 目次ファイルを読み込み
            with open(index_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            # 章リンクを検索して置換
            links_fixed = 0
            for link in soup.find_all('a', href=True):
                href = link['href']
                
                # 外部の章URLをチェック
                if href in chapter_mapping:
                    # ローカルファイル名に置換
                    local_filename = chapter_mapping[href]
                    link['href'] = local_filename
                    links_fixed += 1
                    self.debug_log(f"リンク変換: {href} → {local_filename}")
            
            if links_fixed > 0:
                # 修正された内容を保存
                modified_content = str(soup)
                with open(index_file_path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
                
                self.debug_log(f"目次ページリンク修正完了: {links_fixed}個のリンクを変換")
                return {
                    'success': True, 
                    'links_fixed': links_fixed, 
                    'file_path': index_file_path,
                    'chapter_mapping_count': len(chapter_mapping)
                }
            else:
                self.debug_log("修正対象のリンクが見つかりませんでした", "WARNING")
                return {
                    'success': True, 
                    'links_fixed': 0, 
                    'file_path': index_file_path,
                    'reason': 'no_links_to_fix'
                }
                
        except Exception as e:
            self.debug_log(f"目次ページリンク修正エラー: {e}", "ERROR")
            return {'success': False, 'error': str(e)}

    def fix_cross_page_links(self, output_dir: str, base_url: str) -> Dict[str, Any]:
        """
        全ページタイプ間のクロスリンクを修正（目次・小説情報・感想・章間の相互リンク）
        
        Args:
            output_dir: 出力ディレクトリ
            base_url: ベースURL（小説ID抽出用）
            
        Returns:
            Dict[str, Any]: 修正結果
        """
        self.debug_log("クロスページリンク修正開始")
        
        try:
            # 小説IDを抽出してリンクマッピングを構築
            import re
            novel_id_match = re.search(r'/novel/(\d+)', base_url)
            if not novel_id_match:
                return {'success': False, 'reason': 'invalid_base_url'}
            
            novel_id = novel_id_match.group(1)
            
            # クロスリンクマッピング定義
            cross_link_mapping = {
                f'https://syosetu.org/novel/{novel_id}/': '目次.html',
                f'https://syosetu.org/?mode=ss_detail&nid={novel_id}': None,  # 小説情報ファイル名は動的に決定
                f'https://syosetu.org/?mode=review&nid={novel_id}': '感想/感想 - ページ1.html'
            }
            
            # 章別感想リンクも追加（volume パラメーター付き）
            for volume in range(1, 21):  # 最大20章まで対応
                volume_review_url = f'https://syosetu.org/?mode=review&nid={novel_id}&volume={volume}'
                cross_link_mapping[volume_review_url] = '感想/感想 - ページ1.html'
            
            # 小説情報ファイル名を検出
            novel_info_file = self.detect_novel_info_filename(output_dir)
            if novel_info_file:
                cross_link_mapping[f'https://syosetu.org/?mode=ss_detail&nid={novel_id}'] = novel_info_file
            
            self.debug_log(f"クロスリンクマッピング: {len(cross_link_mapping)}個のリンク")
            
            results = {}
            
            # 1. 目次ページのクロスリンク修正
            index_result = self.fix_index_cross_links(output_dir, cross_link_mapping)
            results['index'] = index_result
            
            # 2. 小説情報ページのクロスリンク修正
            if novel_info_file:
                novel_info_result = self.fix_novel_info_cross_links(output_dir, novel_info_file, cross_link_mapping)
                results['novel_info'] = novel_info_result
            
            # 3. 感想ページのクロスリンク修正
            comments_result = self.fix_comments_cross_links(output_dir, cross_link_mapping)
            results['comments'] = comments_result
            
            # 4. 章ページのクロスリンク修正
            chapters_result = self.fix_chapters_cross_links(output_dir, cross_link_mapping)
            results['chapters'] = chapters_result
            
            # 結果集計
            total_fixed = 0
            success_count = 0
            
            for page_type, result in results.items():
                if result.get('success'):
                    success_count += 1
                    total_fixed += result.get('links_fixed', 0)
            
            self.debug_log(f"クロスページリンク修正完了: {success_count}/{len(results)}ページタイプ, {total_fixed}個のリンク修正")
            
            return {
                'success': True,
                'total_links_fixed': total_fixed,
                'page_results': results,
                'cross_link_mapping': cross_link_mapping
            }
            
        except Exception as e:
            self.debug_log(f"クロスページリンク修正エラー: {e}", "ERROR")
            return {'success': False, 'error': str(e)}

    def detect_novel_info_filename(self, output_dir: str) -> str:
        """小説情報ファイル名を検出"""
        try:
            for filename in os.listdir(output_dir):
                if '小説情報' in filename and filename.endswith('.html'):
                    self.debug_log(f"小説情報ファイル検出: {filename}")
                    return filename
            return ""
        except Exception as e:
            self.debug_log(f"小説情報ファイル検出エラー: {e}", "ERROR")
            return ""

    def fix_index_cross_links(self, output_dir: str, cross_link_mapping: dict) -> Dict[str, Any]:
        """目次ページのクロスリンク修正"""
        try:
            index_file = os.path.join(output_dir, "目次.html")
            if not os.path.exists(index_file):
                return {'success': False, 'reason': 'index_file_not_found'}
            
            with open(index_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            links_fixed = 0
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href in cross_link_mapping and cross_link_mapping[href]:
                    local_path = cross_link_mapping[href]
                    link['href'] = local_path
                    links_fixed += 1
                    self.debug_log(f"目次クロスリンク修正: {href} → {local_path}")
            
            if links_fixed > 0:
                with open(index_file, 'w', encoding='utf-8') as f:
                    f.write(str(soup))
                
            return {'success': True, 'links_fixed': links_fixed, 'file': index_file}
            
        except Exception as e:
            self.debug_log(f"目次クロスリンク修正エラー: {e}", "ERROR")
            return {'success': False, 'error': str(e)}

    def fix_novel_info_cross_links(self, output_dir: str, novel_info_file: str, cross_link_mapping: dict) -> Dict[str, Any]:
        """小説情報ページのクロスリンク修正"""
        try:
            file_path = os.path.join(output_dir, novel_info_file)
            if not os.path.exists(file_path):
                return {'success': False, 'reason': 'file_not_found'}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            links_fixed = 0
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href in cross_link_mapping and cross_link_mapping[href]:
                    local_path = cross_link_mapping[href]
                    link['href'] = local_path
                    links_fixed += 1
                    self.debug_log(f"小説情報クロスリンク修正: {href} → {local_path}")
            
            if links_fixed > 0:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(str(soup))
                
            return {'success': True, 'links_fixed': links_fixed, 'file': file_path}
            
        except Exception as e:
            self.debug_log(f"小説情報クロスリンク修正エラー: {e}", "ERROR")
            return {'success': False, 'error': str(e)}

    def fix_comments_cross_links(self, output_dir: str, cross_link_mapping: dict) -> Dict[str, Any]:
        """感想ページのクロスリンク修正"""
        try:
            comments_dir = os.path.join(output_dir, "感想")
            if not os.path.exists(comments_dir):
                return {'success': False, 'reason': 'comments_dir_not_found'}
            
            total_links_fixed = 0
            files_processed = 0
            
            for filename in os.listdir(comments_dir):
                if filename.endswith('.html'):
                    file_path = os.path.join(comments_dir, filename)
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    links_fixed = 0
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        if href in cross_link_mapping and cross_link_mapping[href]:
                            # 感想フォルダからの相対パス調整
                            local_path = cross_link_mapping[href]
                            if not local_path.startswith('../'):
                                local_path = f"../{local_path}"
                            
                            link['href'] = local_path
                            links_fixed += 1
                            self.debug_log(f"感想クロスリンク修正: {href} → {local_path}")
                    
                    if links_fixed > 0:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(str(soup))
                        
                    total_links_fixed += links_fixed
                    files_processed += 1
            
            return {
                'success': True, 
                'links_fixed': total_links_fixed, 
                'files_processed': files_processed,
                'comments_dir': comments_dir
            }
            
        except Exception as e:
            self.debug_log(f"感想クロスリンク修正エラー: {e}", "ERROR")
            return {'success': False, 'error': str(e)}

    def fix_chapters_cross_links(self, output_dir: str, cross_link_mapping: dict) -> Dict[str, Any]:
        """章ページのクロスリンク修正"""
        try:
            total_links_fixed = 0
            files_processed = 0
            
            for filename in os.listdir(output_dir):
                if filename.startswith('第') and filename.endswith('.html'):
                    file_path = os.path.join(output_dir, filename)
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    links_fixed = 0
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        if href in cross_link_mapping and cross_link_mapping[href]:
                            local_path = cross_link_mapping[href]
                            link['href'] = local_path
                            links_fixed += 1
                            self.debug_log(f"章クロスリンク修正: {href} → {local_path}")
                    
                    if links_fixed > 0:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(str(soup))
                        
                    total_links_fixed += links_fixed
                    files_processed += 1
            
            return {
                'success': True, 
                'links_fixed': total_links_fixed, 
                'files_processed': files_processed
            }
            
        except Exception as e:
            self.debug_log(f"章クロスリンク修正エラー: {e}", "ERROR")
            return {'success': False, 'error': str(e)}

    
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

# 互換クラスは他ファイルで定義済み（hameln_scraper_final.py, hameln_scraper_modular_bridge.py）
# 重複定義を回避するため、このファイルでは定義しない
