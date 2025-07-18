"""
User-Agent管理クラス
"""

from typing import List


class UserAgentRotator:
    """User-Agentローテーション管理クラス"""
    
    def __init__(self, user_agents: List[str] = None):
        if user_agents is None:
            self.user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]
        else:
            self.user_agents = user_agents
            
        self.current_index = 0
        
    def get_current_user_agent(self) -> str:
        """現在のUser-Agentを取得"""
        return self.user_agents[self.current_index]
        
    def rotate_user_agent(self) -> str:
        """User-Agentをローテーション"""
        self.current_index = (self.current_index + 1) % len(self.user_agents)
        return self.get_current_user_agent()
        
    def get_user_agent_count(self) -> int:
        """User-Agentの数を取得"""
        return len(self.user_agents)
        
    def reset_rotation(self):
        """ローテーションをリセット"""
        self.current_index = 0