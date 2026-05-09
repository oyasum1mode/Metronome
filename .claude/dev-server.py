import http.server
import os

# スクリプト位置からプロジェクトルートに移動（iCloud パス上の getcwd PermissionError を回避）
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

http.server.test(
    http.server.SimpleHTTPRequestHandler,
    port=int(os.environ.get('PORT', 8080)),
    bind='',
)
