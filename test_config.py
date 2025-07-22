#!/usr/bin/env python3
"""
設定管理クラスのテスト
"""

import unittest
import sys
import os

# テスト対象のインポート
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hameln_scraper.core.config import HamelnConfig


class TestHamelnConfig(unittest.TestCase):
    """設定管理クラスのテスト"""
    
    def setUp(self):
        self.config = HamelnConfig()
        
    def test_initialization(self):
        """初期化テスト"""
        self.assertEqual(self.config.base_url, "https://syosetu.org")
        self.assertTrue(self.config.debug_mode)
        self.assertTrue(self.config.enable_novel_info_saving)
        self.assertTrue(self.config.enable_comments_saving)
        self.assertEqual(len(self.config.user_agents), 5)
        self.assertEqual(self.config.current_ua_index, 0)
        
    def test_user_agent_rotation(self):
        """User-Agentローテーションテスト"""
        initial_ua = self.config.get_current_user_agent()
        rotated_ua = self.config.rotate_user_agent()
        
        self.assertNotEqual(initial_ua, rotated_ua)
        self.assertEqual(self.config.current_ua_index, 1)
        
        # 全てのUser-Agentを循環
        for i in range(4):
            self.config.rotate_user_agent()
            
        # 最初に戻る
        final_ua = self.config.get_current_user_agent()
        self.assertEqual(initial_ua, final_ua)
        self.assertEqual(self.config.current_ua_index, 0)
        
    def test_config_validation(self):
        """設定妥当性チェックテスト"""
        # 正常な設定
        self.assertTrue(self.config.validate_config())
        
        # 異常な設定
        self.config.base_url = ""
        self.assertFalse(self.config.validate_config())
        
        # 設定復元
        self.config.base_url = "https://syosetu.org"
        self.assertTrue(self.config.validate_config())
        
        # User-Agentが空の場合
        self.config.user_agents = []
        self.assertFalse(self.config.validate_config())
        
    def test_config_dict(self):
        """設定辞書取得テスト"""
        config_dict = self.config.get_config_dict()
        
        self.assertIsInstance(config_dict, dict)
        self.assertIn('base_url', config_dict)
        self.assertIn('debug_mode', config_dict)
        self.assertIn('enable_novel_info_saving', config_dict)
        self.assertIn('enable_comments_saving', config_dict)
        self.assertEqual(config_dict['user_agents_count'], 5)
        self.assertEqual(config_dict['current_ua_index'], 0)
        
    def test_content_selectors(self):
        """コンテンツセレクターテスト"""
        selectors = self.config.content_selectors
        
        self.assertIsInstance(selectors, list)
        self.assertGreater(len(selectors), 0)
        
        # 重要なセレクターが含まれているかチェック
        selector_classes = [sel.get('class') for sel in selectors if 'class' in sel]
        self.assertIn('section1', selector_classes)
        self.assertIn('section3', selector_classes)
        self.assertIn('p-novel-text', selector_classes)
        
    def test_exclude_keywords(self):
        """除外キーワードテスト"""
        keywords = self.config.exclude_keywords
        
        self.assertIsInstance(keywords, list)
        self.assertGreater(len(keywords), 0)
        
        # 重要なキーワードが含まれているかチェック
        self.assertIn('ナビゲーション', keywords)
        self.assertIn('前の話', keywords)
        self.assertIn('次の話', keywords)
        self.assertIn('目次', keywords)
        self.assertIn('感想', keywords)


if __name__ == '__main__':
    unittest.main(verbosity=2)