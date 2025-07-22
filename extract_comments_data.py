#!/usr/bin/env python3
"""
感想データ解析・JSON構造化スクリプト
"""

import sys
import os
import json
import re
from datetime import datetime
sys.path.append('/home/suiren/ClaudeTest')

from bs4 import BeautifulSoup

def extract_comments_data():
    """感想データをHTMLから抽出してJSON構造化"""
    
    novel_dir = "/home/suiren/ClaudeTest/novels/片田舎の剣聖 錬鉄の英霊"
    comments_dir = os.path.join(novel_dir, "感想")
    
    all_comments = []
    
    # 感想ページ1と2を解析
    pages = ["感想 - ページ1.html", "感想 - ページ2.html"]
    
    for page_file in pages:
        page_path = os.path.join(comments_dir, page_file)
        
        if not os.path.exists(page_path):
            print(f"ファイルが見つかりません: {page_path}")
            continue
            
        print(f"解析中: {page_file}")
        
        with open(page_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # 各感想ブロック（div.section3）を解析
        comment_blocks = soup.find_all('div', class_='section3')
        
        for block in comment_blocks:
            comment_data = extract_single_comment(block, page_file)
            if comment_data:
                all_comments.append(comment_data)
    
    # JSONファイルとして保存
    output_path = os.path.join(comments_dir, "comments_data.json")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            'comments': all_comments,
            'total_count': len(all_comments),
            'generated_at': datetime.now().isoformat()
        }, f, ensure_ascii=False, indent=2)
    
    print(f"感想データ構造化完了: {len(all_comments)}件")
    print(f"保存先: {output_path}")
    
    return all_comments

def extract_single_comment(block, page_file):
    """単一感想ブロックからデータ抽出"""
    
    try:
        # ヘッダー情報（ユーザー名と日時）
        h3_tag = block.find('h3')
        if not h3_tag:
            return None
            
        # ユーザー名リンク
        user_link = h3_tag.find('a', href=True)
        username = user_link.text.strip() if user_link else "匿名"
        user_url = user_link['href'] if user_link else ""
        
        # 投稿日時
        date_span = h3_tag.find('span', class_='date')
        date_text = date_span.text.strip() if date_span else ""
        
        # 感想本文（最初のpタグ）
        comment_p = block.find('p')
        comment_text = ""
        if comment_p:
            comment_text = comment_p.get_text(separator='\n').strip()
        
        # Good/Bad投票数とレビューID
        vote_info = extract_vote_info(block)
        
        # 対象話数
        chapter_info = extract_chapter_info(block)
        
        # コメントID（レビューIDから取得）
        comment_id = vote_info.get('review_id', '')
        
        # 隠しコメントかどうか
        is_hidden = check_if_hidden_comment(block)
        
        return {
            'comment_id': comment_id,
            'username': username,
            'user_url': user_url,
            'date_text': date_text,
            'comment_text': comment_text,
            'good_count': vote_info.get('good_count', 0),
            'bad_count': vote_info.get('bad_count', 0),
            'chapter_number': chapter_info.get('chapter_number', 0),
            'chapter_title': chapter_info.get('chapter_title', ''),
            'chapter_link': chapter_info.get('chapter_link', ''),
            'is_hidden': is_hidden,
            'page_source': page_file,
            'good_rate': calculate_good_rate(vote_info.get('good_count', 0), vote_info.get('bad_count', 0))
        }
    except Exception as e:
        print(f"感想抽出エラー: {e}")
        return None

def extract_vote_info(block):
    """Good/Bad投票情報を抽出"""
    
    vote_info = {'good_count': 0, 'bad_count': 0, 'review_id': ''}
    
    try:
        # Good/Badカウントのspanタグを探す
        good_span = block.find('span', id=re.compile(r'rid_\d+_g'))
        bad_span = block.find('span', id=re.compile(r'rid_\d+_b'))
        
        if good_span:
            vote_info['good_count'] = int(good_span.text.strip())
            # レビューIDを抽出
            match = re.search(r'rid_(\d+)_g', good_span['id'])
            if match:
                vote_info['review_id'] = match.group(1)
        
        if bad_span:
            vote_info['bad_count'] = int(bad_span.text.strip())
            
    except Exception as e:
        print(f"投票情報抽出エラー: {e}")
    
    return vote_info

def extract_chapter_info(block):
    """対象章情報を抽出"""
    
    chapter_info = {'chapter_number': 0, 'chapter_title': '', 'chapter_link': ''}
    
    try:
        # 章リンクを探す（../第XXX話.html形式）
        chapter_link = block.find('a', href=re.compile(r'../第\d+話\.html'))
        
        if chapter_link:
            chapter_info['chapter_link'] = chapter_link['href']
            chapter_text = chapter_link.text.strip()
            
            # 話数を抽出
            match = re.search(r'(\d+)話', chapter_text)
            if match:
                chapter_info['chapter_number'] = int(match.group(1))
            
            chapter_info['chapter_title'] = chapter_text
            
    except Exception as e:
        print(f"章情報抽出エラー: {e}")
    
    return chapter_info

def check_if_hidden_comment(block):
    """隠しコメントかどうかを判定"""
    
    # 隠しコメントは▼このコメントは隠されています。のテキストを含む
    hidden_link = block.find('a', href=re.compile(r'JavaScript:ot_hiraku'))
    return hidden_link is not None

def calculate_good_rate(good_count, bad_count):
    """Good率を計算"""
    
    total = good_count + bad_count
    if total == 0:
        return 0
    return round((good_count / total) * 100, 1)

if __name__ == "__main__":
    extract_comments_data()