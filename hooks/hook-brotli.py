from PyInstaller.utils.hooks import collect_all

# brotliモジュールの全てのファイルを収集
datas, binaries, hiddenimports = collect_all('brotli')