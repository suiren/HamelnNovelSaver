"""
実ハーメルン構造HTMLサンプル
2024年実際のHTML構造を模擬した認証済みサンプル
"""

# 実際のハーメルン章ページHTMLサンプル（簡略化・匿名化済み）
REAL_HAMELN_CHAPTER_HTML = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <title>第1話 始まりの章 - テスト小説 - ハーメルン</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="./resources/main.css">
    <script src="./resources/common.js"></script>
</head>
<body>
    <div id="wrapper">
        <div class="header">
            <h1 class="site-title">ハーメルン</h1>
        </div>
        
        <div id="main">
            <div class="novel-info">
                <h1 class="p-novel-title">テスト小説</h1>
                <div class="novel-author">作者：テスト作者</div>
            </div>
            
            <div class="chapter-info">
                <h2 class="chapter-title">第1話 始まりの章</h2>
            </div>
            
            <div id="entry_box">
                <!-- 実際のハーメルン本文構造 -->
                <div id="honbun" class="section1">
                    <p>これは実際のハーメルン構造を模擬した章内容です。</p>
                    <p>主人公が新しい世界に転生し、不思議な力を手に入れる物語。</p>
                    <p>「なんだこの力は...まさか、これが異世界転生というやつなのか？」</p>
                    <p>彼は手のひらに浮かぶ青い光を見つめながら、運命の始まりを感じていた。</p>
                    <br>
                    <p>第1話では、主人公の覚醒と最初の試練が描かれる。</p>
                    <p>果たして彼は、この新しい世界で生き抜くことができるのだろうか。</p>
                </div>
            </div>
            
            <div class="chapter-nav">
                <a href="./index.html" class="nav-link">目次に戻る</a>
                <a href="./2.html" class="nav-link">次話へ</a>
            </div>
        </div>
        
        <div class="footer">
            <p>&copy; ハーメルン</p>
        </div>
    </div>
    
    <!-- リソース参照（実際の構造） -->
    <img src="./resources/character_image.jpg" alt="キャラクター" style="display:none;">
    <link rel="stylesheet" href="./resources/chapter.css">
</body>
</html>
"""

# 実際のハーメルン目次ページHTMLサンプル
REAL_HAMELN_INDEX_HTML = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <title>テスト小説 - ハーメルン</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
    <div id="wrapper">
        <div class="novel-header">
            <h1 class="p-novel-title">テスト小説</h1>
            <div class="novel-meta">
                <span class="author">作者：テスト作者</span>
                <span class="genre">ジャンル：異世界転生</span>
            </div>
            <div class="novel-summary">
                <p>平凡な高校生が異世界に転生し、特殊な能力を手に入れて冒険する物語。</p>
                <p>友情、成長、そして運命の出会いが待ち受ける壮大な冒険譚。</p>
            </div>
        </div>
        
        <div class="chapter-list">
            <h2>目次</h2>
            <ul class="chapters">
                <li><a href="/novel/123/1/" class="chapter-link">第1話 始まりの章</a></li>
                <li><a href="/novel/123/2/" class="chapter-link">第2話 新たな力</a></li>
                <li><a href="/novel/123/3/" class="chapter-link">第3話 仲間との出会い</a></li>
                <li><a href="/novel/123/4/" class="chapter-link">第4話 最初の試練</a></li>
                <li><a href="/novel/123/5/" class="chapter-link">第5話 覚醒</a></li>
            </ul>
        </div>
    </div>
</body>
</html>
"""

# section2クラス使用パターン（実際のハーメルンバリエーション）
REAL_HAMELN_SECTION2_HTML = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <title>第2話 新たな力 - テスト小説 - ハーメルン</title>
    <meta charset="UTF-8">
</head>
<body>
    <div id="wrapper">
        <div class="novel-info">
            <h1 class="novel-title">テスト小説</h1>
            <div class="chapter-title">第2話 新たな力</div>
        </div>
        
        <div id="entry_box">
            <!-- section2クラスパターン -->
            <div class="section2" id="content-area">
                <p>前話から一夜明け、主人公は自分の力について考えていた。</p>
                <p>「昨日のあの光は一体何だったのだろう。」</p>
                <br>
                <p>彼は再び手のひらに意識を集中した。すると...</p>
                <p>「うお！また光った！」</p>
                <br>
                <p>今度は青い光だけでなく、微かに暖かさも感じられた。</p>
                <p>これが魔法というものなのか、それとも別の何かなのか。</p>
                <p>主人公の新たな力の探求が始まる。</p>
            </div>
        </div>
    </div>
</body>
</html>
"""

# p-novel-textクラス使用パターン（最新のハーメルン構造）
REAL_HAMELN_MODERN_HTML = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <title>第3話 仲間との出会い - テスト小説 - ハーメルン</title>
    <meta charset="UTF-8">
</head>
<body>
    <div class="page-container">
        <div class="novel-header">
            <h1 class="p-novel-title">テスト小説</h1>
            <h2 class="p-chapter-title">第3話 仲間との出会い</h2>
        </div>
        
        <div class="novel-content">
            <!-- 最新のp-novel-textクラス -->
            <div class="p-novel-text">
                <p>森を歩いていると、突然声が聞こえてきた。</p>
                <p>「助けて！誰か助けて！」</p>
                <br>
                <p>主人公は急いで声のする方向へ向かった。</p>
                <p>そこには魔物に襲われている少女の姿が。</p>
                <br>
                <p>「大丈夫か！」</p>
                <p>主人公は迷わず新しく覚えた力を使った。</p>
                <p>青い光が魔物を包み、一瞬で消し去った。</p>
                <br>
                <p>「ありがとう...あなたは？」</p>
                <p>「俺は...」</p>
                <p>こうして主人公の最初の仲間との出会いが生まれた。</p>
            </div>
        </div>
    </div>
</body>
</html>
"""

# ContentExtractorテスト失敗用の短いコンテンツ
REAL_HAMELN_SHORT_CONTENT_HTML = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <title>短い章 - テスト小説 - ハーメルン</title>
</head>
<body>
    <div id="honbun" class="section1">
        <p>短い章です。</p>
    </div>
</body>
</html>
"""

# 複雑なネストした構造（実際のハーメルンでよくあるパターン）
REAL_HAMELN_COMPLEX_HTML = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <title>第4話 最初の試練 - テスト小説 - ハーメルン</title>
    <meta charset="UTF-8">
    <script>
        // JavaScript動的コンテンツ（実際のハーメルンによくある）
        window.onload = function() {
            console.log("ページ読み込み完了");
        };
    </script>
</head>
<body>
    <div id="app-root">
        <div class="layout-container">
            <div class="content-wrapper">
                <div id="entry_box" class="entry-container">
                    <div id="honbun" class="section1 content-main">
                        <div class="chapter-intro">
                            <p>ついに主人公に最初の本格的な試練が訪れる。</p>
                        </div>
                        
                        <div class="story-content">
                            <p>「お前の力を見せてもらおう。」</p>
                            <p>謎の老人は厳しい目で主人公を見つめた。</p>
                            <br>
                            <p>「これは...試験なのか？」</p>
                            <p>「そうだ。お前が真に力を制御できるかどうかを見極める。」</p>
                            <br>
                            <div class="action-scene">
                                <p>突然、周囲の景色が変わった。</p>
                                <p>見慣れた森が消え、荒涼とした大地が広がっている。</p>
                                <p>「これは...幻術か？」</p>
                            </div>
                            <br>
                            <p>主人公は手のひらに青い光を集中させた。</p>
                            <p>今度は昨日より遥かに強い力を感じる。</p>
                            <p>「よし...やってみる！」</p>
                            <br>
                            <div class="climax-scene">
                                <p>光が爆発的に広がり、幻術の世界を包み込んだ。</p>
                                <p>すると、周囲の景色が元に戻った。</p>
                                <p>「見事だ。お前は合格だ。」</p>
                            </div>
                        </div>
                        
                        <div class="chapter-outro">
                            <p>こうして主人公は最初の試練を乗り越えた。</p>
                            <p>しかし、これはまだ始まりに過ぎなかった。</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- 実際のリソース参照 -->
    <img src="./resources/bg_image.jpg" style="display:none;" alt="背景">
    <link rel="stylesheet" href="./resources/story.css">
</body>
</html>
"""

def get_all_real_samples():
    """全ての実ハーメルン構造サンプルを返す"""
    return {
        'chapter_basic': REAL_HAMELN_CHAPTER_HTML,
        'index_page': REAL_HAMELN_INDEX_HTML, 
        'section2_pattern': REAL_HAMELN_SECTION2_HTML,
        'modern_p_novel_text': REAL_HAMELN_MODERN_HTML,
        'short_content': REAL_HAMELN_SHORT_CONTENT_HTML,
        'complex_nested': REAL_HAMELN_COMPLEX_HTML
    }