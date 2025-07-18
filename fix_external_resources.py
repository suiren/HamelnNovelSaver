#!/usr/bin/env python3
"""
外部リソース参照をローカル化する修正パッチ
hameln_scraper_final.pyに追加する関数
"""

def fix_external_resources(self, soup):
    """外部リソースの参照をローカル化（ハーメルン完全対応）"""
    print("=== 外部リソースのローカル化開始 ===")
    
    # 1. CSSファイル内の外部参照を修正
    for style_tag in soup.find_all('style'):
        if style_tag.string:
            css_content = style_tag.string
            
            # url()参照をローカルファイルに変更
            import re
            urls = re.findall(r'url\([\'"]?([^\'"]+)[\'"]?\)', css_content)
            for url in urls:
                if url.startswith(('http', '//')):
                    # 外部URLをローカルファイル名に変更
                    filename = os.path.basename(urlparse(url).path)
                    if filename:
                        css_content = css_content.replace(url, f"./resources/{filename}")
                        print(f"CSS内URL修正: {url} -> ./resources/{filename}")
            
            style_tag.string = css_content
    
    # 2. link要素のhref属性を修正
    for link in soup.find_all('link', href=True):
        href = link.get('href')
        if href and href.startswith(('http', '//')):
            filename = os.path.basename(urlparse(href).path)
            if filename:
                link['href'] = f"./resources/{filename}"
                print(f"Link href修正: {href} -> ./resources/{filename}")
    
    # 3. script要素のsrc属性を修正
    for script in soup.find_all('script', src=True):
        src = script.get('src')
        if src and src.startswith(('http', '//')):
            filename = os.path.basename(urlparse(src).path)
            if filename:
                script['src'] = f"./resources/{filename}"
                print(f"Script src修正: {src} -> ./resources/{filename}")
    
    # 4. img要素のsrc属性を修正
    for img in soup.find_all('img', src=True):
        src = img.get('src')
        if src and src.startswith(('http', '//')):
            filename = os.path.basename(urlparse(src).path)
            if filename:
                img['src'] = f"./resources/{filename}"
                print(f"Image src修正: {src} -> ./resources/{filename}")
    
    # 5. ハーメルン特有のリソース参照を修正
    hameln_resources = [
        '/css/blank.css',
        '/image/hor_menu8_off.gif',
        '/image/menu_line_gray.gif'
    ]
    
    for resource_path in hameln_resources:
        filename = os.path.basename(resource_path)
        
        # CSSリンクを修正
        for link in soup.find_all('link', href=lambda x: x and resource_path in x):
            link['href'] = f"./resources/{filename}"
            print(f"ハーメルンCSS修正: {resource_path} -> ./resources/{filename}")
        
        # 画像参照を修正
        for img in soup.find_all('img', src=lambda x: x and resource_path in x):
            img['src'] = f"./resources/{filename}"
            print(f"ハーメルン画像修正: {resource_path} -> ./resources/{filename}")
    
    print("=== 外部リソースのローカル化完了 ===")
    return soup

def fix_comments_page_navigation(self, soup, current_page_num, total_pages, base_filename):
    """感想ページのページネーション修正"""
    print(f"=== 感想ページナビゲーション修正開始 (ページ{current_page_num}/{total_pages}) ===")
    
    # ページネーションリンクを検索
    pagination_links = soup.find_all('a', href=True)
    
    for link in pagination_links:
        href = link.get('href')
        text = link.get_text().strip()
        
        # ページ番号リンクを検出
        if href and ('page=' in href or text.isdigit()):
            try:
                # ページ番号を抽出
                if 'page=' in href:
                    import re
                    page_match = re.search(r'page=(\d+)', href)
                    if page_match:
                        page_num = int(page_match.group(1))
                    else:
                        continue
                elif text.isdigit():
                    page_num = int(text)
                else:
                    continue
                
                # ローカルファイル名を生成
                if page_num == 1:
                    local_filename = f"{base_filename}.html"
                else:
                    local_filename = f"{base_filename}_page{page_num}.html"
                
                # リンクを修正
                if page_num <= total_pages:
                    link['href'] = local_filename
                    print(f"感想ページリンク修正: ページ{page_num} -> {local_filename}")
                else:
                    # 存在しないページへのリンクは無効化
                    link['href'] = "#"
                    print(f"無効ページリンク無効化: ページ{page_num}")
                    
            except (ValueError, AttributeError):
                continue
        
        # 「次へ」「前へ」リンクを修正
        elif href and any(keyword in text for keyword in ['次', '前', 'Next', 'Prev']):
            if '次' in text or 'Next' in text:
                next_page = current_page_num + 1
                if next_page <= total_pages:
                    if next_page == 1:
                        local_filename = f"{base_filename}.html"
                    else:
                        local_filename = f"{base_filename}_page{next_page}.html"
                    link['href'] = local_filename
                    print(f"「次へ」リンク修正: -> {local_filename}")
                else:
                    link['href'] = "#"
                    print("「次へ」リンク無効化（最終ページ）")
            
            elif '前' in text or 'Prev' in text:
                prev_page = current_page_num - 1
                if prev_page >= 1:
                    if prev_page == 1:
                        local_filename = f"{base_filename}.html"
                    else:
                        local_filename = f"{base_filename}_page{prev_page}.html"
                    link['href'] = local_filename
                    print(f"「前へ」リンク修正: -> {local_filename}")
                else:
                    link['href'] = "#"
                    print("「前へ」リンク無効化（最初のページ）")
    
    print("=== 感想ページナビゲーション修正完了 ===")
    return soup

if __name__ == "__main__":
    print("外部リソース修正パッチ - hameln_scraper_final.pyに追加してください")