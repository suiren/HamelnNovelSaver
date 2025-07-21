"""
レスポンス解凍処理クラス
"""

import gzip
import zlib
import brotli
from typing import Any


class ResponseDecompressor:
    """レスポンス解凍処理クラス"""
    
    @staticmethod
    def decompress_response(response: Any) -> str:
        """レスポンスを解凍して文字列として返す"""
        try:
            # CloudScraperは自動的に解凍を行うため、まずtextを試す
            if hasattr(response, 'text') and response.text:
                return response.text
            
            # 手動解凍が必要な場合
            content = response.content
            encoding = response.headers.get('Content-Encoding', '').lower()
            
            # 圧縮されている場合の解凍処理
            if encoding == 'gzip':
                content = gzip.decompress(content)
            elif encoding == 'deflate':
                content = zlib.decompress(content)
            elif encoding == 'br':
                content = brotli.decompress(content)
                
            # 文字列として返す
            return content.decode('utf-8')
            
        except Exception as e:
            # CloudScraperの自動解凍に失敗した場合の処理
            try:
                return response.text if hasattr(response, 'text') else ""
            except:
                return ""
    
    @staticmethod
    def is_compressed(response: Any) -> bool:
        """レスポンスが圧縮されているかチェック"""
        if not hasattr(response, 'headers'):
            return False
            
        encoding = response.headers.get('Content-Encoding', '').lower()
        return encoding in ['gzip', 'deflate', 'br']
    
    @staticmethod
    def get_compression_type(response: Any) -> str:
        """圧縮タイプを取得"""
        if not hasattr(response, 'headers'):
            return 'none'
            
        encoding = response.headers.get('Content-Encoding', '').lower()
        if encoding in ['gzip', 'deflate', 'br']:
            return encoding
        return 'none'