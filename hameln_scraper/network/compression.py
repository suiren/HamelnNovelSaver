"""
レスポンス圧縮解除処理
"""

import gzip
import zlib
import brotli
from typing import Union


class ResponseDecompressor:
    """レスポンス圧縮解除クラス"""
    
    @staticmethod
    def decompress(response) -> str:
        """
        レスポンスの圧縮を解除
        
        Args:
            response: HTTPレスポンスオブジェクト
            
        Returns:
            str: 解凍されたテキスト
        """
        content_encoding = response.headers.get('content-encoding', '').lower()
        content = response.content
        
        try:
            if content_encoding == 'br':
                # Brotli圧縮
                decompressed = brotli.decompress(content)
                return decompressed.decode('utf-8')
            elif content_encoding == 'gzip':
                # Gzip圧縮
                decompressed = gzip.decompress(content)
                return decompressed.decode('utf-8')
            elif content_encoding == 'deflate':
                # Deflate圧縮
                decompressed = zlib.decompress(content)
                return decompressed.decode('utf-8')
            else:
                # 圧縮なし
                return response.text
                
        except Exception as e:
            # 解凍失敗時はテキストとして取得
            try:
                return response.text
            except Exception:
                return content.decode('utf-8', errors='ignore')