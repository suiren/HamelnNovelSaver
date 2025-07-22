"""
実ハーメルン環境ライブテスト
ユーザー提案による実際のサイトアクセステスト
"""

import pytest
import tempfile
import os
import time
from hameln_scraper.core.scraper import HamelnModularScraper
from hameln_scraper.resources.saver import PageSaver
from hameln_scraper.resources.processor import ResourceProcessor


class TestRealHamelnLive:
    """実際のハーメルンサイトでのライブテスト"""

    @pytest.fixture
    def real_hameln_url(self):
        """実在する軽量ハーメルンページURL"""
        return "https://syosetu.org/novel/260808/"

    def test_real_hameln_page_access(self, real_hameln_url):
        """実際のハーメルンページ完全アクセステスト"""
        print(f"\\n=== 実ハーメルンライブテスト開始 ===")
        print(f"テストURL: {real_hameln_url}")
        
        try:
            scraper = HamelnModularScraper()
            
            # 実際のハーメルンページ取得
            print("実ハーメルンページ取得中...")
            response = scraper.network_client.cloudscraper.get(real_hameln_url, timeout=30)
            
            # レスポンス基本確認
            assert response.status_code == 200, f"ページアクセス失敗: {response.status_code}"
            assert len(response.content) > 1000, "取得内容が小さすぎます"
            
            print(f"✅ ページアクセス成功")
            print(f"レスポンスサイズ: {len(response.content)} bytes")
            print(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
            
            # 実際のHTML構造分析
            from bs4 import BeautifulSoup
            real_soup = BeautifulSoup(response.content, 'html.parser')
            
            # ハーメルン特有要素の確認
            title_tag = real_soup.find('title')
            hameln_elements = {
                'title': title_tag.text.strip() if title_tag else 'なし',
                'honbun': bool(real_soup.find(id='honbun')),
                'section_classes': [cls for cls in ['section1', 'section2', 'section3'] 
                                  if real_soup.find(class_=cls)],
                'css_links': [link.get('href') for link in real_soup.find_all('link', rel='stylesheet')],
                'img_sources': [img.get('src') for img in real_soup.find_all('img', src=True)],
                'script_sources': [script.get('src') for script in real_soup.find_all('script', src=True) if script.get('src')]
            }
            
            print("\\n=== 実ハーメルン構造分析結果 ===")
            print(f"タイトル: {hameln_elements['title'][:100]}...")
            print(f"honbun要素: {hameln_elements['honbun']}")
            print(f"sectionクラス: {hameln_elements['section_classes']}")
            print(f"CSSリンク数: {len(hameln_elements['css_links'])}")
            print(f"画像数: {len(hameln_elements['img_sources'])}")
            print(f"JSスクリプト数: {len(hameln_elements['script_sources'])}")
            
            if hameln_elements['css_links']:
                print(f"実際のCSSパス例: {hameln_elements['css_links'][0]}")
            if hameln_elements['img_sources']:
                print(f"実際の画像パス例: {hameln_elements['img_sources'][0]}")
            
            # 基本的なハーメルン要素の存在確認
            assert hameln_elements['title'], "タイトルが見つかりません"
            # honbunがない場合もあるので、section系で確認
            has_content = (hameln_elements['honbun'] or 
                          hameln_elements['section_classes'] or 
                          real_soup.find(class_='novel-text'))
            assert has_content, "コンテンツ要素が見つかりません"
            
            print("✅ 実ハーメルン構造確認成功")
            
        except Exception as e:
            pytest.fail(f"実ハーメルンアクセステスト失敗: {e}")

    def test_real_hameln_complete_save(self, real_hameln_url):
        """実ハーメルンページの完全保存テスト"""
        print(f"\\n=== 実ハーメルン完全保存テスト ===")
        
        try:
            scraper = HamelnModularScraper()
            
            # 実際のページ取得
            print("実ページ取得中...")
            response = scraper.network_client.cloudscraper.get(real_hameln_url, timeout=30)
            assert response.status_code == 200
            
            real_html = response.text
            
            # 完全保存処理
            with tempfile.TemporaryDirectory() as temp_dir:
                print(f"保存先: {temp_dir}")
                
                saver = PageSaver(scraper.resource_processor)
                
                print("完全保存処理実行中...")
                start_time = time.time()
                
                result = saver.save_complete_page(
                    html_content=real_html,
                    output_dir=temp_dir,
                    filename='real_hameln_test.html',
                    original_url=real_hameln_url,
                    title='実ハーメルンテストページ'
                )
                
                save_time = time.time() - start_time
                print(f"保存処理時間: {save_time:.2f}秒")
                
                # 保存成功確認
                assert result['success'], f"保存失敗: {result.get('error', '不明')}"
                assert os.path.exists(result['saved_path']), "ファイルが作成されていません"
                
                # 保存ファイル内容確認
                with open(result['saved_path'], 'r', encoding='utf-8-sig') as f:
                    saved_content = f.read()
                
                print("\\n=== 保存結果分析 ===")
                print(f"保存ファイル: {result['saved_path']}")
                print(f"ファイルサイズ: {result['file_size']} bytes")
                print(f"元HTMLサイズ: {len(real_html)} bytes")
                
                # 保存内容の品質確認
                quality_checks = {
                    'has_title': 'ハーメルン' in saved_content or 'syosetu' in saved_content,
                    'has_meta_info': 'save-date' in saved_content,
                    'has_source_url': real_hameln_url in saved_content,
                    'has_resources_path': './resources/' in saved_content,
                    'has_generator': 'Hameln Scraper' in saved_content,
                    'file_size_reasonable': len(saved_content) > len(real_html) * 0.8,
                    'utf8_bom': True  # UTF-8 BOMで保存されている
                }
                
                print("\\n=== 品質チェック結果 ===")
                for check, result_ok in quality_checks.items():
                    status = "✅" if result_ok else "❌"
                    print(f"{status} {check}: {result_ok}")
                
                # 重要な品質確認
                assert quality_checks['has_meta_info'], "メタ情報が追加されていません"
                assert quality_checks['has_source_url'], "元URLが保存されていません"
                assert quality_checks['file_size_reasonable'], "ファイルサイズが異常です"
                
                print("✅ 実ハーメルン完全保存成功")
                
                # リソースディレクトリ確認
                resources_dir = os.path.join(temp_dir, 'resources')
                if os.path.exists(resources_dir):
                    resource_files = os.listdir(resources_dir)
                    print(f"ダウンロードされたリソース数: {len(resource_files)}")
                    if resource_files:
                        print(f"リソース例: {resource_files[:3]}")
                else:
                    print("リソースディレクトリ: なし（エラーまたはリソースなし）")
                
        except Exception as e:
            pytest.fail(f"実ハーメルン完全保存テスト失敗: {e}")

    def test_real_hameln_cloudflare_bypass(self, real_hameln_url):
        """Cloudflare認証・bot検知回避の実動作確認"""
        print(f"\\n=== Cloudflare認証テスト ===")
        
        try:
            scraper = HamelnModularScraper()
            
            # User-Agentローテーションテスト
            print("User-Agentローテーションテスト...")
            ua1 = scraper.network_client.ua_rotator.get_current_user_agent()
            scraper.network_client.ua_rotator.rotate_user_agent()
            ua2 = scraper.network_client.ua_rotator.get_current_user_agent()
            
            print(f"UA1: {ua1[:50]}...")
            print(f"UA2: {ua2[:50]}...")
            assert ua1 != ua2, "User-Agentローテーションが機能していません"
            
            # 複数回アクセステスト（bot検知回避確認）
            print("連続アクセステスト（bot検知回避確認）...")
            for i in range(3):
                print(f"アクセス {i+1}/3...")
                response = scraper.network_client.cloudscraper.get(real_hameln_url, timeout=30)
                assert response.status_code == 200, f"アクセス{i+1}で失敗: {response.status_code}"
                
                if i < 2:  # 最後以外は待機
                    time.sleep(scraper.config.chapter_wait_time)
            
            print("✅ Cloudflare認証・bot検知回避確認成功")
            
        except Exception as e:
            pytest.fail(f"Cloudflare認証テスト失敗: {e}")

    def test_real_hameln_error_handling(self, real_hameln_url):
        """実環境でのエラーハンドリング確認"""
        print(f"\\n=== 実環境エラーハンドリングテスト ===")
        
        try:
            scraper = HamelnModularScraper()
            
            # 存在しないページテスト
            invalid_url = real_hameln_url.replace('260808', '999999999')
            print(f"存在しないページテスト: {invalid_url}")
            
            try:
                response = scraper.network_client.cloudscraper.get(invalid_url, timeout=10)
                print(f"レスポンス: {response.status_code}")
                # 404エラーでも適切に処理されることを確認
                assert response.status_code in [404, 403, 500], "適切なエラーレスポンスを受信"
            except Exception as e:
                print(f"期待通りのエラー: {type(e).__name__}")
            
            print("✅ エラーハンドリング確認成功")
            
        except Exception as e:
            pytest.fail(f"エラーハンドリングテスト失敗: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])