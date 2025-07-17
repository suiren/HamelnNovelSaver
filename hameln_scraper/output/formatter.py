"""
HTML出力フォーマッター
完全なHTMLファイルの生成と保存
"""

import os
import logging
from datetime import datetime
from bs4 import BeautifulSoup, Comment


class OutputFormatter:
    """HTML出力フォーマッタークラス"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def save_complete_html(self, content: str, output_file: str, title: str, author: str):
        """
        完全なHTMLファイルを保存
        
        Args:
            content: HTMLコンテンツ
            output_file: 出力ファイルパス
            title: タイトル
            author: 作者名
        """
        try:
            self.logger.debug(f"HTML保存開始: {output_file}")
            
            # HTMLの基本構造を作成
            html_template = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - {author}</title>
    <meta name="author" content="{author}">
    <meta name="save-date" content="{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}">
    <style>
        body {{
            font-family: 'Hiragino Sans', 'Yu Gothic', 'Meiryo', sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #fafafa;
        }}
        .header {{
            border-bottom: 2px solid #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
        }}
        .title {{
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .author {{
            color: #666;
            font-size: 14px;
        }}
        .content {{
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        p {{
            margin-bottom: 1em;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="title">{title}</div>
        <div class="author">作者: {author}</div>
    </div>
    <div class="content">
        {content}
    </div>
</body>
</html>"""
            
            # ディレクトリが存在しない場合は作成
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # ファイルに書き込み
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_template)
            
            self.logger.info(f"HTML保存完了: {output_file}")
            
        except Exception as e:
            self.logger.error(f"HTML保存エラー: {e}")
            raise
    
    def _sanitize_filename(self, filename: str) -> str:
        """ファイル名として使用できるよう文字列をサニタイズ"""
        import re
        # Windows/Linux/macOSで使用できない文字を除去
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        filename = filename.strip().strip('.')
        # 長すぎる場合は切り詰め
        if len(filename) > 100:
            filename = filename[:100]
        return filename or "untitled"