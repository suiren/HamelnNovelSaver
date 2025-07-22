#!/usr/bin/env python3
"""
ネットワークモジュールのテスト
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch

# テスト対象のインポート
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hameln_scraper.network.user_agent import UserAgentRotator
from hameln_scraper.network.compression import ResponseDecompressor
from hameln_scraper.network.client import HamelnNetworkClient


class TestUserAgentRotator(unittest.TestCase):
    """User-Agentローテーションテスト"""
    
    def setUp(self):
        self.rotator = UserAgentRotator()
        
    def test_initialization(self):
        """初期化テスト"""
        self.assertEqual(self.rotator.get_user_agent_count(), 5)
        self.assertEqual(self.rotator.current_index, 0)
        
    def test_rotation(self):
        """ローテーションテスト"""
        initial_ua = self.rotator.get_current_user_agent()
        rotated_ua = self.rotator.rotate_user_agent()
        
        self.assertNotEqual(initial_ua, rotated_ua)
        self.assertEqual(self.rotator.current_index, 1)
        
    def test_full_rotation(self):
        """全体ローテーションテスト"""
        initial_ua = self.rotator.get_current_user_agent()
        
        # 5回ローテーション
        for i in range(5):
            self.rotator.rotate_user_agent()
            
        # 最初に戻る
        final_ua = self.rotator.get_current_user_agent()
        self.assertEqual(initial_ua, final_ua)
        self.assertEqual(self.rotator.current_index, 0)
        
    def test_reset_rotation(self):
        """ローテーションリセットテスト"""
        # 数回ローテーション
        for i in range(3):
            self.rotator.rotate_user_agent()
            
        self.assertEqual(self.rotator.current_index, 3)
        
        # リセット
        self.rotator.reset_rotation()
        self.assertEqual(self.rotator.current_index, 0)
        
    def test_custom_user_agents(self):
        """カスタムUser-Agentテスト"""
        custom_uas = ['UA1', 'UA2', 'UA3']
        rotator = UserAgentRotator(custom_uas)
        
        self.assertEqual(rotator.get_user_agent_count(), 3)
        self.assertEqual(rotator.get_current_user_agent(), 'UA1')
        
        rotator.rotate_user_agent()
        self.assertEqual(rotator.get_current_user_agent(), 'UA2')


class TestResponseDecompressor(unittest.TestCase):
    """レスポンス解凍テスト"""
    
    def test_decompress_response(self):
        """レスポンス解凍テスト"""
        # 通常のレスポンス
        mock_response = Mock()
        mock_response.text = "<html><body>test</body></html>"
        mock_response.content = b"<html><body>test</body></html>"
        mock_response.headers = {}
        
        result = ResponseDecompressor.decompress_response(mock_response)
        self.assertEqual(result, "<html><body>test</body></html>")
        
    def test_is_compressed(self):
        """圧縮判定テスト"""
        # 圧縮されていないレスポンス
        mock_response = Mock()
        mock_response.headers = {}
        self.assertFalse(ResponseDecompressor.is_compressed(mock_response))
        
        # gzip圧縮されたレスポンス
        mock_response.headers = {'Content-Encoding': 'gzip'}
        self.assertTrue(ResponseDecompressor.is_compressed(mock_response))
        
        # brotli圧縮されたレスポンス
        mock_response.headers = {'Content-Encoding': 'br'}
        self.assertTrue(ResponseDecompressor.is_compressed(mock_response))
        
    def test_get_compression_type(self):
        """圧縮タイプ取得テスト"""
        # 圧縮なし
        mock_response = Mock()
        mock_response.headers = {}
        self.assertEqual(ResponseDecompressor.get_compression_type(mock_response), 'none')
        
        # gzip圧縮
        mock_response.headers = {'Content-Encoding': 'gzip'}
        self.assertEqual(ResponseDecompressor.get_compression_type(mock_response), 'gzip')
        
        # brotli圧縮
        mock_response.headers = {'Content-Encoding': 'br'}
        self.assertEqual(ResponseDecompressor.get_compression_type(mock_response), 'br')


class TestHamelnNetworkClient(unittest.TestCase):
    """ハーメルンネットワーククライアントテスト"""
    
    def setUp(self):
        self.client = HamelnNetworkClient()
        
    def test_initialization(self):
        """初期化テスト"""
        self.assertEqual(self.client.base_url, "https://syosetu.org")
        self.assertTrue(self.client.debug_mode)
        self.assertIsNotNone(self.client.ua_rotator)
        self.assertIsNotNone(self.client.decompressor)
        self.assertIsNotNone(self.client.cloudscraper)
        
    def test_get_status(self):
        """ステータス取得テスト"""
        status = self.client.get_status()
        
        self.assertIsInstance(status, dict)
        self.assertIn('base_url', status)
        self.assertIn('user_agent_count', status)
        self.assertIn('current_user_agent', status)
        self.assertIn('cloudscraper_initialized', status)
        self.assertIn('debug_mode', status)
        
        self.assertEqual(status['base_url'], "https://syosetu.org")
        self.assertEqual(status['user_agent_count'], 5)
        self.assertTrue(status['cloudscraper_initialized'])
        self.assertTrue(status['debug_mode'])
        
    def test_rotate_user_agent(self):
        """User-Agentローテーションテスト"""
        initial_ua = self.client.ua_rotator.get_current_user_agent()
        new_ua = self.client.rotate_user_agent()
        
        self.assertNotEqual(initial_ua, new_ua)
        self.assertEqual(self.client.ua_rotator.current_index, 1)
        
    def test_close(self):
        """リソース解放テスト"""
        # close()メソッドが呼び出せることを確認
        try:
            self.client.close()
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"close()メソッドが失敗: {e}")


if __name__ == '__main__':
    unittest.main(verbosity=2)