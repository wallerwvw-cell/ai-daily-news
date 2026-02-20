#!/usr/bin/env python3
"""
AI 日报生成脚本
自动抓取 AI 新闻、技术文章、教程和趣闻，生成 HTML 页面
"""

import json
import os
from datetime import datetime

# 读取搜索结果（由 agent 调用 web_search 获取）
SEARCH_RESULTS_FILE = "/Users/alex/.openclaw/workspace/ai-daily-news/search_results.json"

def load_search_results():
    """加载搜索结果"""
    if os.path.exists(SEARCH_RESULTS_FILE):
        with open(SEARCH_RESULTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "news": [],
        "tech": [],
        "tutorial": [],
        "fun": []
    }

def generate_card(item, category_class):
    """生成卡片 HTML"""
    title = item.get('title', '')
    snippet = item.get('snippet', '')[:150] + '...' if item.get('snippet') else ''
    url = item.get('url', '#')
    source = item.get('source', '') or extract_domain(url)
    
    return f'''
        <div class="card">
            <span class="card-category {category_class}">{get_category_label(category_class)}</span>
            <h3><a href="{url}" target="_blank">{title}</a></h3>
            <p>{snippet}</p>
            <span class="card-source">{source}</span>
        </div>'''

def extract_domain(url):
    """提取域名"""
    try:
        from urllib.parse import urlparse
        return urlparse(url).netloc.replace('www.', '')
    except:
        return ''

def get_category_label(cat_class):
    """获取分类标签"""
    labels = {
        'category-news': '新闻',
        'category-tech': '技术',
        'category-tutorial': '教程',
        'category-fun': '趣闻'
    }
    return labels.get(cat_class, '')

def generate_html(news, tech, tutorial, fun):
    """生成完整 HTML"""
    date = datetime.now()
    date_str = date.strftime('%Y年%m月%d日 %A')
    
    news_cards = '\n'.join([generate_card(item, 'category-news') for item in news])
    tech_cards = '\n'.join([generate_card(item, 'category-tech') for item in tech])
    tutorial_cards = '\n'.join([generate_card(item, 'category-tutorial') for item in tutorial])
    fun_cards = '\n'.join([generate_card(item, 'category-fun') for item in fun])
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI 日报 - {date.strftime('%Y年%m月%d日')}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        header {{ text-align: center; padding: 40px 0; color: #fff; }}
        header h1 {{
            font-size: 2.5rem; margin-bottom: 10px;
            background: linear-gradient(90deg, #00d4ff, #7c3aed);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }}
        header p {{ color: #94a3b8; font-size: 1.1rem; }}
        .date {{ text-align: center; color: #64748b; margin-bottom: 30px; font-size: 1.1rem; }}
        .section {{ margin-bottom: 40px; }}
        .section-title {{
            color: #fff; font-size: 1.5rem; margin-bottom: 20px;
            padding-left: 15px; border-left: 4px solid #00d4ff;
        }}
        .cards {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 20px; }}
        .card {{
            background: rgba(255, 255, 255, 0.05); border-radius: 16px; padding: 24px;
            border: 1px solid rgba(255, 255, 255, 0.1); transition: transform 0.3s, box-shadow 0.3s;
            backdrop-filter: blur(10px);
        }}
        .card:hover {{ transform: translateY(-5px); box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3); }}
        .card-category {{
            display: inline-block; padding: 4px 12px; border-radius: 20px;
            font-size: 0.75rem; font-weight: 600; margin-bottom: 12px;
        }}
        .category-news {{ background: linear-gradient(90deg, #ff6b6b, #ee5a24); }}
        .category-tech {{ background: linear-gradient(90deg, #00d4ff, #0984e3); }}
        .category-tutorial {{ background: linear-gradient(90deg, #00b894, #00cec9); }}
        .category-fun {{ background: linear-gradient(90deg, #a29bfe, #6c5ce7); }}
        .card h3 {{ color: #fff; font-size: 1.2rem; margin-bottom: 12px; line-height: 1.4; }}
        .card h3 a {{ color: inherit; text-decoration: none; }}
        .card h3 a:hover {{ color: #00d4ff; }}
        .card p {{ color: #94a3b8; font-size: 0.9rem; line-height: 1.6; margin-bottom: 16px; }}
        .card-source {{ color: #64748b; font-size: 0.8rem; }}
        footer {{ text-align: center; padding: 40px 0; color: #64748b; font-size: 0.9rem; }}
        footer a {{ color: #00d4ff; text-decoration: none; }}
        @media (max-width: 768px) {{ .cards {{ grid-template-columns: 1fr; }} header h1 {{ font-size: 2rem; }} }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🐟 AI 日报</h1>
            <p>每日 AI 新闻资讯、技术文章、教程和趣闻</p>
        </header>
        <p class="date">{date_str}</p>
        
        <div class="section">
            <h2 class="section-title">📰 AI 新闻</h2>
            <div class="cards">{news_cards if news_cards else '<p style="color:#64748b;">暂无新闻</p>'}</div>
        </div>
        
        <div class="section">
            <h2 class="section-title">💻 技术文章</h2>
            <div class="cards">{tech_cards if tech_cards else '<p style="color:#64748b;">暂无文章</p>'}</div>
        </div>
        
        <div class="section">
            <h2 class="section-title">📚 教程</h2>
            <div class="cards">{tutorial_cards if tutorial_cards else '<p style="color:#64748b;">暂无教程</p>'}</div>
        </div>
        
        <div class="section">
            <h2 class="section-title">🎉 趣闻</h2>
            <div class="cards">{fun_cards if fun_cards else '<p style="color:#64748b;">暂无趣闻</p>'}</div>
        </div>
        
        <footer>
            <p>由 🐟 小鱼 自动生成 | <a href="https://github.com/wallerwvw-cell/ai-daily-news">GitHub</a></p>
        </footer>
    </div>
</body>
</html>'''
    return html

def main():
    """主函数"""
    results = load_search_results()
    
    html = generate_html(
        results.get('news', []),
        results.get('tech', []),
        results.get('tutorial', []),
        results.get('fun', [])
    )
    
    output_path = "/Users/alex/.openclaw/workspace/ai-daily-news/index.html"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"HTML 生成完成: {output_path}")

if __name__ == "__main__":
    main()
