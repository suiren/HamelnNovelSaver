#!/usr/bin/env python3
"""
ハーメルン小説保存アプリケーション - GUI版
使いやすいグラフィカルユーザーインターフェース
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
import time
from hameln_scraper.core.scraper import HamelnModularScraper
from hameln_scraper.core.config import HamelnConfig

class HamelnGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ハーメルン小説保存ツール")
        self.root.geometry("600x500")
        
        # スクレイピング用のインスタンス
        self.scraper = None
        
        # フラグ
        self.is_scraping = False
        
        self.create_widgets()
        
    def create_widgets(self):
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # タイトル
        title_label = ttk.Label(main_frame, text="ハーメルン小説保存ツール", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # URL入力
        url_label = ttk.Label(main_frame, text="小説のURL:")
        url_label.grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        self.url_entry = ttk.Entry(main_frame, width=60)
        self.url_entry.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # 🆕 新機能: 右クリックメニューの設定
        self.create_context_menu()
        self.url_entry.bind('<Button-3>', self.show_context_menu)
        
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
        
        self.save_path_var = tk.StringVar(value="./saved_novels")  # デフォルトパスを修正済み
        self.save_path_entry = ttk.Entry(save_frame, textvariable=self.save_path_var, width=45)
        self.save_path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.browse_button = ttk.Button(save_frame, text="参照", command=self.browse_folder)
        self.browse_button.grid(row=0, column=1, padx=(10, 0))
        
        # ボタンフレーム
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=(0, 20))
        
        self.download_button = ttk.Button(button_frame, text="ダウンロード開始", 
                                         command=self.start_download)
        self.download_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="停止", 
                                     command=self.stop_download, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1)
        
        # プログレスバー
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # ステータスラベル
        self.status_label = ttk.Label(main_frame, text="待機中...")
        self.status_label.grid(row=9, column=0, columnspan=2, pady=(0, 10))
        
        # ログテキストエリア
        log_label = ttk.Label(main_frame, text="ログ:")
        log_label.grid(row=10, column=0, sticky=tk.W, pady=(0, 5))
        
        # テキストエリアとスクロールバー
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=11, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.log_text = tk.Text(text_frame, height=10, width=70)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Grid設定
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(10, weight=1)
        save_frame.columnconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
    def create_context_menu(self):
        """🆕 新機能: URL入力欄用のコンテキストメニューを作成"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="貼り付け", command=self.paste_from_clipboard)
        
    def show_context_menu(self, event):
        """🆕 新機能: 右クリック時にコンテキストメニューを表示"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        except Exception as e:
            print(f"コンテキストメニュー表示エラー: {e}")
        finally:
            # メニューを非表示にする
            self.context_menu.grab_release()
    
    def paste_from_clipboard(self):
        """🆕 新機能: クリップボードからURL入力欄に貼り付け"""
        try:
            # クリップボードの内容を取得
            clipboard_text = self.root.clipboard_get()
            
            # 現在の入力欄をクリア
            self.url_entry.delete(0, tk.END)
            
            # クリップボードの内容を挿入
            self.url_entry.insert(0, clipboard_text)
            
            self.log(f"クリップボードから貼り付け: {clipboard_text[:50]}...")
            
        except tk.TclError:
            # クリップボードが空の場合
            messagebox.showwarning("警告", "クリップボードが空です")
        except Exception as e:
            # その他のエラー
            messagebox.showerror("エラー", f"貼り付けに失敗しました: {e}")
        
    def browse_folder(self):
        """保存先フォルダを選択"""
        folder = filedialog.askdirectory()
        if folder:
            self.save_path_var.set(folder)
            
    def log(self, message):
        """ログメッセージを追加（アプリ内表示＋外部ファイル出力）"""
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)
        self.root.update()
        
        # 外部ファイルにも出力
        try:
            from datetime import datetime
            log_file = "hameln_gui.log"
            with open(log_file, 'a', encoding='utf-8') as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{timestamp}] {message}\n")
        except Exception as e:
            print(f"ログファイル書き込みエラー: {e}")
        
    def update_status(self, message):
        """ステータスを更新"""
        self.status_label.config(text=message)
        self.root.update()
        
    def start_download(self):
        """ダウンロード開始"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("エラー", "URLを入力してください")
            return
            
        if not url.startswith('http'):
            messagebox.showerror("エラー", "有効なURLを入力してください")
            return
            
        # UI状態を更新
        self.is_scraping = True
        self.download_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress.start()
        self.log_text.delete(1.0, tk.END)
        
        # 別スレッドでダウンロード実行
        self.download_thread = threading.Thread(target=self.download_novel, args=(url,))
        self.download_thread.daemon = True
        self.download_thread.start()
        
    def stop_download(self):
        """ダウンロード停止"""
        self.is_scraping = False
        self.update_status("停止中...")
        self.log("ダウンロードを停止しました")
        self.reset_ui()
        
    def reset_ui(self):
        """UI状態をリセット"""
        self.download_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress.stop()
        if self.is_scraping:
            self.update_status("完了")
        else:
            self.update_status("停止")
        self.is_scraping = False
        
    def download_novel(self, url):
        """小説をダウンロード（別スレッド）"""
        try:
            self.update_status("小説情報を取得中...")
            self.log(f"開始: {url}")
            
            self.log("完全モード（CSS・画像・JavaScript含む完全保存）で実行します")
            
            # スクレイパーを初期化（GUIログ連携）
            self.scraper = HamelnModularScraper()
            
            # 機能設定
            self.scraper.config.enable_novel_info_saving = False
            self.scraper.config.enable_comments_saving = True
            
            # スクレイパーのデバッグログをGUIに転送
            original_debug_log = self.scraper.debug_log
            def gui_debug_log(message: str, level: str = "INFO"):
                self.log(f"[{level}] {message}")
                original_debug_log(message, level)
            self.scraper.debug_log = gui_debug_log
            
            
            # 統合された小説スクレイピングメソッドを使用（全話対応）
            self.update_status("小説を取得中...")
            self.log("小説取得を開始します...")
            self.log(f"URL: {url}")
            
            # 保存先フォルダ設定
            save_dir = self.save_path_var.get() or "./saved_novels"
            self.log(f"保存先: {save_dir}")
            
            # 保存先ディレクトリを作成・設定
            abs_save_dir = os.path.abspath(save_dir)
            os.makedirs(abs_save_dir, exist_ok=True)
            
            original_cwd = os.getcwd()
            os.chdir(abs_save_dir)
            
            try:
                # scrape_novelメソッドで全話取得を実行
                result = self.scraper.scrape_novel(url)
            finally:
                # 元のディレクトリに戻す
                os.chdir(original_cwd)
            
            if result and result.get('success') and self.is_scraping:
                self.log(f"✓ 保存完了: {result}")
                messagebox.showinfo("完了", f"小説の保存が完了しました\n{result}")
            elif not self.is_scraping:
                self.log("ダウンロードが停止されました")
            else:
                error_msg = result.get('error', '不明なエラー') if result else '不明なエラー'
                self.log(f"✗ 保存に失敗しました: {error_msg}")
                messagebox.showerror("エラー", f"小説の保存に失敗しました:\n{error_msg}")
                
        except Exception as e:
            self.log(f"エラーが発生しました: {e}")
            messagebox.showerror("エラー", f"エラーが発生しました:\n{e}")
            
        finally:
            if self.scraper:
                self.scraper.close()
            self.reset_ui()

def main():
    root = tk.Tk()
    app = HamelnGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
