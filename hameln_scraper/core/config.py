"""
ハーメルンスクレイパー設定管理
"""

import logging
from datetime import datetime
from typing import List, Dict, Any


class HamelnConfig:
    """ハーメルンスクレイパーの設定管理クラス"""
    
    def __init__(self, base_url: str = "https://syosetu.org"):
        self.base_url = base_url
        self.debug_mode = True
        
        # 機能制御フラグ（Norton検出問題解決により、新機能を有効化）
        self.enable_novel_info_saving = True   # 小説情報保存機能
        self.enable_comments_saving = True     # 感想保存機能
        
        # User-Agentローテーション用のリスト
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        self.current_ua_index = 0
        
        # タイムアウト設定
        self.request_timeout = 30
        self.selenium_timeout = 10
        
        # 待機時間設定
        self.chapter_wait_time = 3
        self.error_wait_time = 5
        self.max_retries = 3
        
        # ログ設定
        self.log_level = logging.DEBUG if self.debug_mode else logging.INFO
        self.log_handlers = [
            logging.FileHandler('hameln_scraper.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
        
        # ファイル命名設定
        self.max_filename_length = 100
        self.invalid_filename_chars = r'[<>:"/\\|?*]'
        
        # HTML解析設定
        self.html_parser = 'html.parser'
        
        # 本文抽出用セレクター（優先順位順）
        self.content_selectors = [
            {'id': 'honbun'},
            {'id': 'entry_box'},
            {'class': 'section3'},
            {'class': 'section1'},
            {'class': 'section2'},
            {'class': 'section4'},
            {'class': 'section5'},
            {'class': 'section6'},
            {'class': 'section7'},
            {'class': 'section8'},
            {'class': 'section9'},
            {'class': 'p-novel-text'},
            {'class': 'novel-text'},
            {'class': 'novel_text'},
            {'class': 'text'},
            {'class': 'body'},
            {'class': 'main'},
            {'class': 'content'}
        ]
        
        # 除外キーワード（本文ではない要素の除外）
        self.exclude_keywords = [
            'ナビゲーション', 'メニュー', 'サイドバー', 'フッター',
            'ヘッダー', '広告', 'コメント', 'お知らせ', 'ランキング',
            'オススメ', 'おすすめ', 'タグ', 'ブックマーク', 'いいね',
            'ツイート', 'シェア', 'コピー', 'リンク', '設定', '検索',
            '更新', '投稿', '編集', '削除', '非表示', '表示', '切り替え',
            '前の話', '次の話', '目次', '感想', '小説情報', '作者',
            '評価', '★', '☆', '※', '更新日', '文字数', '読了時間',
            'R-18', 'R18', 'R-15', 'R15', 'BL', 'GL', 'NL',
            'ページトップ', 'トップページ', 'ホーム', 'サイトマップ',
            'プライバシー', '利用規約', 'FAQ', 'お問い合わせ',
            'ログイン', 'ログアウト', '会員登録', '新規登録',
            'パスワード', 'ID', 'メールアドレス', 'twitter', 'pixiv'
        ]
        
        # 最小文字数設定
        self.min_content_length = 50
        self.min_chapter_length = 20
        
    def get_current_user_agent(self) -> str:
        """現在のUser-Agentを取得"""
        return self.user_agents[self.current_ua_index]
        
    def rotate_user_agent(self) -> str:
        """User-Agentをローテーション"""
        self.current_ua_index = (self.current_ua_index + 1) % len(self.user_agents)
        return self.get_current_user_agent()
        
    def setup_logging(self) -> logging.Logger:
        """ログ設定を初期化"""
        logging.basicConfig(
            level=self.log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=self.log_handlers
        )
        logger = logging.getLogger(__name__)
        logger.info("ハーメルンスクレイパー設定初期化完了")
        return logger
        
    def debug_log(self, message: str, level: str = "INFO"):
        """デバッグログ出力（アプリ内表示＋外部ファイル出力）"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {level}: {message}"
        print(formatted_message)
        
        # 外部ファイルにも出力
        try:
            log_file = "hameln_debug.log"
            with open(log_file, 'a', encoding='utf-8') as f:
                full_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{full_timestamp}] {level}: {message}\\n")
        except Exception as e:
            print(f"ログファイル書き込みエラー: {e}")
            
    def get_config_dict(self) -> Dict[str, Any]:
        """設定を辞書形式で取得"""
        return {
            'base_url': self.base_url,
            'debug_mode': self.debug_mode,
            'enable_novel_info_saving': self.enable_novel_info_saving,
            'enable_comments_saving': self.enable_comments_saving,
            'user_agents_count': len(self.user_agents),
            'current_ua_index': self.current_ua_index,
            'request_timeout': self.request_timeout,
            'selenium_timeout': self.selenium_timeout,
            'chapter_wait_time': self.chapter_wait_time,
            'error_wait_time': self.error_wait_time,
            'max_retries': self.max_retries,
            'min_content_length': self.min_content_length,
            'min_chapter_length': self.min_chapter_length,
            'content_selectors_count': len(self.content_selectors),
            'exclude_keywords_count': len(self.exclude_keywords)
        }
        
    def validate_config(self) -> bool:
        """設定の妥当性をチェック"""
        if not self.base_url:
            return False
            
        if not self.user_agents:
            return False
            
        if self.current_ua_index >= len(self.user_agents):
            return False
            
        if self.request_timeout <= 0:
            return False
            
        if self.min_content_length < 0:
            return False
            
        return True