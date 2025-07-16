"""
リソース処理モジュール
CSS、画像、JavaScriptなどのWebリソースのダウンロードと処理
"""

import os
import re
import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import logging


class ResourceProcessor:
    """リソース処理クラス"""
    
    def __init__(self, config, network_client):
        self.config = config
        self.network_client = network_client
        self.logger = logging.getLogger(__name__)
        self.resource_cache = {}
        self.base_url = config.base_url
        
    def download_resource(self, url, resources_dir):
        """リソースをダウンロード（キャッシュ機能付き）"""
        if url in self.resource_cache:
            return self.resource_cache[url]
        
        try:
            if not url.startswith('http'):
                url = urljoin(self.base_url, url)
            
            parsed = urlparse(url)
            filename = os.path.basename(parsed.path)
            if not filename or '.' not in filename:
                ext = self._get_extension_from_url(url)
                filename = f"resource_{hash(url) % 10000}{ext}"
            
            local_path = os.path.join(resources_dir, filename)
            
            if os.path.exists(local_path):
                self.resource_cache[url] = filename
                return filename
            
            os.makedirs(resources_dir, exist_ok=True)
            
            response = self.network_client.cloudscraper.get(url, timeout=10)
            response.raise_for_status()
            
            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            self.resource_cache[url] = filename
            self.logger.debug(f"リソースダウンロード完了: {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"リソースダウンロードエラー ({url}): {e}")
            return url
    
    def _get_extension_from_url(self, url):
        """URLから拡張子を推測"""
        if 'css' in url.lower():
            return '.css'
        elif any(ext in url.lower() for ext in ['jpg', 'jpeg']):
            return '.jpg'
        elif 'png' in url.lower():
            return '.png'
        elif 'gif' in url.lower():
            return '.gif'
        elif 'js' in url.lower():
            return '.js'
        return '.bin'
    
    def process_html_resources(self, soup, base_path):
        """HTMLのリソースを処理してローカル保存"""
        resources_dir_name = getattr(self, 'browser_compatible_name', 'resources')
        resources_dir = os.path.join(base_path, resources_dir_name)
        
        self.logger.info("リソース処理開始")
        
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href')
            if href:
                local_css = self.download_and_process_css(href, resources_dir)
                if local_css != href:
                    link['href'] = f"./{resources_dir_name}/{local_css}"
        
        for img in soup.find_all('img', src=True):
            src = img.get('src')
            if src and not src.startswith('data:'):
                local_img = self.download_resource(src, resources_dir)
                if local_img != src:
                    img['src'] = f"./{resources_dir_name}/{local_img}"
        
        for script in soup.find_all('script', src=True):
            src = script.get('src')
            if src:
                local_js = self.download_resource(src, resources_dir)
                if local_js != src:
                    script['src'] = f"./{resources_dir_name}/{local_js}"
        
        self.logger.info("リソース処理完了")
        return soup
    
    def download_and_process_css(self, url, resources_dir):
        """CSSファイルをダウンロードして内部の画像参照も処理"""
        try:
            if not url.startswith('http'):
                url = urljoin(self.base_url, url)
            
            parsed = urlparse(url)
            filename = os.path.basename(parsed.path)
            if not filename or '.' not in filename:
                filename = f"style_{hash(url) % 10000}.css"
            
            self.logger.debug(f"CSS詳細処理中: {url}")
            
            response = self.network_client.cloudscraper.get(url, timeout=10)
            response.raise_for_status()
            
            response.encoding = 'utf-8'
            css_content = response.text
            
            def replace_url_func(match):
                full_match = match.group(0)
                img_url = match.group(1)
                
                if img_url.startswith('data:'):
                    return full_match
                
                original_img_url = img_url
                
                if not img_url.startswith('http'):
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    elif img_url.startswith('/'):
                        base_domain = '/'.join(url.split('/')[:3])
                        img_url = base_domain + img_url
                    else:
                        base_css_url = '/'.join(url.split('/')[:-1])
                        img_url = urljoin(base_css_url + '/', img_url)
                
                cleaned_url = img_url.split(')')[0]
                if '?' in cleaned_url:
                    cleaned_url = cleaned_url.split('?')[0]
                
                local_img = self.download_resource(cleaned_url, resources_dir)
                if local_img != cleaned_url:
                    browser_compatible_path = f"./{local_img}"
                    return full_match.replace(original_img_url, browser_compatible_path)
                else:
                    return full_match
            
            css_content = re.sub(r'url\([\'"]?([^\'"]+?)[\'"]?\)', replace_url_func, css_content)
            
            # @import文を処理
            imports = re.findall(r'@import\s+[\'"]([^\'"]+)[\'"]', css_content)
            for import_url in imports:
                if not import_url.startswith('http'):
                    if import_url.startswith('//'):
                        import_url = 'https:' + import_url
                    elif import_url.startswith('/'):
                        base_domain = '/'.join(url.split('/')[:3])
                        import_url = base_domain + import_url
                    else:
                        base_css_url = '/'.join(url.split('/')[:-1])
                        import_url = urljoin(base_css_url + '/', import_url)
                
                local_css = self.download_and_process_css(import_url, resources_dir)
                if local_css != import_url:
                    browser_compatible_css = f"./{local_css}"
                    css_content = css_content.replace(f'@import "{import_url}"', f'@import "{browser_compatible_css}"')
                    css_content = css_content.replace(f"@import '{import_url}'", f"@import '{browser_compatible_css}'")
            
            local_path = os.path.join(resources_dir, filename)
            with open(local_path, 'w', encoding='utf-8') as f:
                f.write(css_content)
            
            self.logger.debug(f"CSS処理完了: {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"CSS処理エラー ({url}): {e}")
            return self.download_resource(url, resources_dir)
    
    def adjust_resource_paths_only(self, soup, base_path):
        """リソースパスのみを調整（ダウンロードは行わない）"""
        resources_dir_name = getattr(self, 'browser_compatible_name', 'resources')
        
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href')
            if href and href.startswith('./'):
                continue
        
        for img in soup.find_all('img', src=True):
            src = img.get('src')
            if src and src.startswith('./'):
                continue
        
        for script in soup.find_all('script', src=True):
            src = script.get('src')
            if src and src.startswith('./'):
                continue
        
        return soup
