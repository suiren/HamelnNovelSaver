"""
User-Agentローテーション管理
"""

from typing import List
import random


class UserAgentRotator:
    """User-Agentローテーション管理クラス"""
    
    def __init__(self, user_agents: List[str]):
        self.user_agents = user_agents
        self.current_index = 0
    
    def get_current(self) -> str:
        """現在のUser-Agentを取得"""
        return self.user_agents[self.current_index]
    
    def rotate(self) -> str:
        """次のUser-Agentにローテーション"""
        self.current_index = (self.current_index + 1) % len(self.user_agents)
        return self.get_current()
    
    def get_random(self) -> str:
        """ランダムなUser-Agentを取得"""
        return random.choice(self.user_agents)