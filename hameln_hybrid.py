#!/usr/bin/env python3
"""
ハーメルン小説保存アプリケーション - ハイブリッド版
GUI環境があればGUI、なければCUIで動作
"""

import sys
import os

def main():
    """メイン実行関数"""
    print("ハーメルン小説保存ツール - ハイブリッド版")
    print("=" * 50)
    
    # PyInstaller環境の検出
    is_pyinstaller = getattr(sys, 'frozen', False)
    if is_pyinstaller:
        print("🔧 PyInstaller実行環境を検出")
    
    # GUI環境の確認（PyInstaller対応強化版）
    gui_available = False
    gui_error = None
    
    try:
        print("🔍 GUI環境をチェック中...")
        import tkinter as tk
        print("  ✅ tkinterモジュールのインポート成功")
        
        # ディスプレイが利用可能かテスト（PyInstaller対応）
        try:
            root = tk.Tk()
            print("  ✅ Tkルートウィンドウの作成成功")
            root.withdraw()  # ウィンドウを隠す
            
            # 簡単なウィジェットテスト
            test_label = tk.Label(root, text="test")
            print("  ✅ ウィジェットの作成成功")
            
            root.destroy()
            print("  ✅ ウィンドウの破棄成功")
            
            gui_available = True
            print("✅ GUI環境が完全に利用可能です")
            
        except tk.TclError as tcl_error:
            gui_error = f"Tcl/Tkエラー: {tcl_error}"
            print(f"  ❌ Tcl/Tkエラー: {tcl_error}")
        except Exception as display_error:
            gui_error = f"ディスプレイエラー: {display_error}"
            print(f"  ❌ ディスプレイエラー: {display_error}")
            
    except ImportError as import_error:
        gui_error = f"tkinterインポートエラー: {import_error}"
        print(f"  ❌ tkinterインポートエラー: {import_error}")
    except Exception as e:
        gui_error = f"予期しないエラー: {e}"
        print(f"  ❌ 予期しないエラー: {e}")
    
    if not gui_available:
        print(f"⚠️ GUI環境が利用できません: {gui_error}")
        print("CUIモードで動作します")
    
    # 実行モードの決定
    if gui_available:
        # GUI版を起動
        try:
            print("🖥️ GUIモードで起動中...")
            run_gui_mode()
        except Exception as e:
            print(f"❌ GUI起動エラー: {e}")
            print("CUIモードにフォールバック...")
            run_cui_mode()
    else:
        # CUI版を起動
        run_cui_mode()

def run_gui_mode():
    """GUIモードで実行（元のGUI版を再現）"""
    try:
        # 元のGUI版を直接インポートして実行
        from hameln_gui import HamelnGUI
        import tkinter as tk
        
        print("✅ 元のGUI版を起動中...")
        root = tk.Tk()
        app = HamelnGUI(root)
        root.mainloop()
        
    except ImportError as import_error:
        print(f"⚠️ 元のGUI版のインポートに失敗: {import_error}")
        print("簡易GUI版で起動します...")
        run_simple_gui_mode()
    except Exception as e:
        print(f"❌ GUI版の実行エラー: {e}")
        raise

def run_simple_gui_mode():
    """簡易GUIモードで実行（フォールバック用）"""
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox, filedialog, scrolledtext
        import threading
        
        # 元のGUI版に近いレイアウトを再現
        root = tk.Tk()
        root.title("ハーメルン小説保存ツール")
        root.geometry("600x500")
        
        # メインフレーム（gridレイアウトを使用）
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # グリッドの重みを設定
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # タイトル
        title_label = ttk.Label(main_frame, text="ハーメルン小説保存ツール", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # URL入力
        url_label = ttk.Label(main_frame, text="小説のURL:")
        url_label.grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        url_entry = ttk.Entry(main_frame, width=60)
        url_entry.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # 説明テキスト
        desc_label = ttk.Label(main_frame, text="ブラウザ互換モード（CSS・画像・JavaScript含む完全保存）", 
                              font=("Arial", 10), foreground="#666")
        desc_label.grid(row=3, column=0, columnspan=2, pady=(0, 5))
        
        # 全話取得機能の説明
        feature_label = ttk.Label(main_frame, 
                                 text="• 目次ページのURL → 全話を自動取得してローカルリンク化\n" +
                                      "• 各話ページのURL → 目次を特定し全話を自動取得", 
                                 font=("Arial", 9), foreground="#444")
        feature_label.grid(row=4, column=0, columnspan=2, pady=(0, 15))
        
        # 保存先選択
        save_label = ttk.Label(main_frame, text="保存先フォルダ:")
        save_label.grid(row=5, column=0, sticky=tk.W, pady=(0, 5))
        
        save_frame = ttk.Frame(main_frame)
        save_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        save_path_var = tk.StringVar(value="./saved_novels")
        save_path_entry = ttk.Entry(save_frame, textvariable=save_path_var, width=45)
        save_path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        save_frame.columnconfigure(0, weight=1)
        
        def browse_folder():
            folder = filedialog.askdirectory()
            if folder:
                save_path_var.set(folder)
        
        browse_button = ttk.Button(save_frame, text="参照", command=browse_folder)
        browse_button.grid(row=0, column=1, padx=(10, 0))
        
        # ボタンフレーム
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=(0, 20))
        
        # プログレスバー
        progress = ttk.Progressbar(main_frame, mode='indeterminate')
        progress.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # ステータスラベル
        status_label = ttk.Label(main_frame, text="待機中...")
        status_label.grid(row=9, column=0, columnspan=2, pady=(0, 10))
        
        # ログテキストエリア
        log_label = ttk.Label(main_frame, text="ログ:")
        log_label.grid(row=10, column=0, sticky=tk.W, pady=(0, 5))
        
        log_text = scrolledtext.ScrolledText(main_frame, height=8, width=70)
        log_text.grid(row=11, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        main_frame.rowconfigure(11, weight=1)
        
        # ダウンロード処理
        def start_download():
            url = url_entry.get().strip()
            save_path = save_path_var.get().strip()
            
            if not url:
                messagebox.showerror("エラー", "URLを入力してください")
                return
            
            if not url.startswith('http'):
                messagebox.showerror("エラー", "有効なURLを入力してください")
                return
            
            # UI状態を更新
            download_button.config(state=tk.DISABLED)
            stop_button.config(state=tk.NORMAL)
            progress.start()
            status_label.config(text="ダウンロード中...")
            log_text.delete(1.0, tk.END)
            log_text.insert(tk.END, f"ダウンロード開始: {url}\n")
            
            # ダウンロード処理を別スレッドで実行
            def download_thread():
                try:
                    from hameln_scraper.core.scraper import HamelnScraper
                    from hameln_scraper.core.config import ScraperConfig
                    config = ScraperConfig()
                    scraper = HamelnScraper(config)
                    
                    # ログ出力をGUIに反映
                    def log_callback(message):
                        log_text.insert(tk.END, f"{message}\n")
                        log_text.see(tk.END)
                        root.update_idletasks()
                    
                    result = scraper.scrape_novel(url)
                    
                    # UI状態をリセット
                    download_button.config(state=tk.NORMAL)
                    stop_button.config(state=tk.DISABLED)
                    progress.stop()
                    
                    if result:
                        status_label.config(text="ダウンロード完了")
                        log_text.insert(tk.END, f"✅ ダウンロード完了: {result}\n")
                        messagebox.showinfo("完了", f"ダウンロード完了: {result}")
                    else:
                        status_label.config(text="ダウンロード失敗")
                        log_text.insert(tk.END, "❌ ダウンロードに失敗しました\n")
                        messagebox.showerror("エラー", "ダウンロードに失敗しました")
                        
                except Exception as e:
                    download_button.config(state=tk.NORMAL)
                    stop_button.config(state=tk.DISABLED)
                    progress.stop()
                    status_label.config(text="エラー発生")
                    log_text.insert(tk.END, f"❌ エラー: {e}\n")
                    messagebox.showerror("エラー", f"エラーが発生しました: {e}")
            
            threading.Thread(target=download_thread, daemon=True).start()
        
        def stop_download():
            # 停止処理（実装は簡略化）
            download_button.config(state=tk.NORMAL)
            stop_button.config(state=tk.DISABLED)
            progress.stop()
            status_label.config(text="停止しました")
            log_text.insert(tk.END, "⏹️ ダウンロードを停止しました\n")
        
        download_button = ttk.Button(button_frame, text="ダウンロード開始", command=start_download)
        download_button.grid(row=0, column=0, padx=(0, 10))
        
        stop_button = ttk.Button(button_frame, text="停止", command=stop_download, state=tk.DISABLED)
        stop_button.grid(row=0, column=1)
        
        print("✅ 簡易GUI版が正常に起動しました")
        root.mainloop()
        
    except Exception as e:
        print(f"❌ 簡易GUI版の実行エラー: {e}")
        raise

def run_cui_mode():
    """CUIモードで実行"""
    print("\n📝 CUIモードで動作中...")
    
    try:
        # CUI版のスクレイパーを使用
        from hameln_scraper.core.scraper import HamelnScraper
        from hameln_scraper.core.config import ScraperConfig
        
        config = ScraperConfig()
        scraper = HamelnScraper(config)
        
        print("\n使用方法:")
        print("1. 小説のURLを入力してください")
        print("2. 保存先フォルダを指定してください")
        print("3. ダウンロードが開始されます")
        print("\n終了するには 'quit' または 'exit' を入力してください")
        
        while True:
            print("\n" + "=" * 50)
            
            # URL入力
            url = input("小説のURL: ").strip()
            
            if url.lower() in ['quit', 'exit', 'q']:
                print("プログラムを終了します。")
                break
            
            if not url:
                print("❌ URLを入力してください")
                continue
            
            if not url.startswith('http'):
                print("❌ 有効なURLを入力してください")
                continue
            
            # 保存先入力
            save_path = input("保存先フォルダ (デフォルト: ./saved_novels): ").strip()
            if not save_path:
                save_path = "./saved_novels"
            
            print(f"\n🚀 ダウンロード開始...")
            print(f"URL: {url}")
            print(f"保存先: {save_path}")
            
            try:
                # ダウンロード実行
                result = scraper.scrape_novel(url)
                
                if result:
                    print(f"✅ ダウンロード完了: {result}")
                else:
                    print("❌ ダウンロードに失敗しました")
                    
            except Exception as e:
                print(f"❌ エラーが発生しました: {e}")
                import traceback
                print(f"詳細: {traceback.format_exc()}")
    
    except ImportError as e:
        print(f"❌ 必要なモジュールが見つかりません: {e}")
        print("hameln_scraperパッケージが必要です")
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        import traceback
        print(f"詳細: {traceback.format_exc()}")

if __name__ == "__main__":
    main()