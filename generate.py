#!/usr/bin/env python3
"""
AI 日报生成脚本 - 完整版
包含：每日存档、分类页面、归档索引、搜索功能
"""

import json
import os
import re
from datetime import datetime, timedelta
import random

# 配置
SEARCH_RESULTS = "/Users/alex/.openclaw/workspace/ai-daily-news/search_results.json"
ARCHIVE_DIR = "/Users/alex/.openclaw/workspace/ai-daily-news/archives"
CATEGORIES = {
    'news': ('📰 新闻', 'category-news'),
    'tech': ('💻 技术', 'category-tech'),
    'products': ('🚀 产品', 'category-products'),
    'funding': ('💰 融资', 'category-funding'),
    'people': ('👤 人物', 'category-people'),
    'opinions': ('💡 观点', 'category-opinions'),
    'tutorial': ('📚 教程', 'category-tutorial'),
    'fun': ('🎉 趣闻', 'category-fun')
}

def load_search_results():
    """加载搜索结果"""
    if os.path.exists(SEARCH_RESULTS):
        with open(SEARCH_RESULTS, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {cat: [] for cat in CATEGORIES.keys()}

def extract_domain(url):
    try:
        from urllib.parse import urlparse
        return urlparse(url).netloc.replace('www.', '')
    except:
        return ''

def get_favicon_url(url):
    domain = extract_domain(url)
    if domain:
        return f"https://www.google.com/s2/favicons?domain={domain}&sz=128"
    return "https://www.google.com/s2/favicons?domain=example.com&sz=128"

def get_random_time():
    hour = random.randint(6, 23)
    minute = random.randint(0, 59)
    return f"{hour:02d}:{minute:02d}"

def clean_html(text):
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def generate_header(title="AI 日报", subtitle="每日 AI 新闻资讯、技术文章、产品融资和人物观点"):
    """生成通用头部"""
    return f'''
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <meta name="description" content="每日AI新闻、技术文章、产品融资、人物观点 - 您的AI资讯助手">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            :root {{
                --bg-primary: #0a0a0b;
                --bg-secondary: #141416;
                --bg-card: #1c1c1f;
                --bg-card-hover: #242428;
                --text-primary: #f4f4f5;
                --text-secondary: #a1a1aa;
                --accent: #f97316;
                --border: #27272a;
            }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'PingFang SC', sans-serif;
                background: var(--bg-primary);
                color: var(--text-primary);
                line-height: 1.6;
                min-height: 100vh;
            }}
            .nav-brand a {{ color: var(--text-primary); text-decoration: none; }}
            .nav-logo {{ font-size: 1.5rem; font-weight: bold; }}
            .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
            .archive-list {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }}
            .archive-item {{ background: var(--bg-card); padding: 20px; border-radius: 12px; }}
            .archive-item h3 {{ margin-bottom: 8px; }}
            .archive-item a {{ color: var(--accent); text-decoration: none; }}
            .search-box {{ margin-bottom: 24px; }}
            .search-box input {{ width: 100%; padding: 12px; border-radius: 8px; border: 1px solid var(--border); background: var(--bg-card); color: var(--text-primary); font-size: 16px; }}
            .category-header {{ margin: 32px 0 16px; }}
            .back-link {{ color: var(--accent); text-decoration: none; margin-bottom: 16px; display: inline-block; }}
            footer {{ text-align: center; padding: 40px 20px; color: var(--text-secondary); border-top: 1px solid var(--border); margin-top: 40px; }}
            footer a {{ color: var(--accent); }}
            .empty-state {{ text-align: center; padding: 60px 20px; color: var(--text-secondary); }}
        </style>
    </head>
    <body>
        <div class="container">'''

def generate_footer():
    return f'''
        <footer>
            <p>🤖 由 <strong>AI 日报</strong> 自动生成 · <a href="https://github.com/wallerwvw-cell/ai-daily-news" target="_blank">GitHub</a> · <a href="https://wallerwvw-cell.github.io/ai-daily-news/" target="_blank">在线阅读</a></p>
        </footer>
    </body>
    </html>'''

def generate_card(item, category_class):
    """生成卡片HTML"""
    title = item.get('title', '')
    summary = item.get('summary', '') or item.get('snippet', '')
    if not summary:
        summary = "点击查看详细内容..."
    if len(summary) > 180:
        summary = summary[:180] + '...'
    
    url = item.get('url', '#')
    source = item.get('source', '') or extract_domain(url)
    favicon = get_favicon_url(url)
    
    cat_label = CATEGORIES.get(category_class.replace('category-', ''), ('', ''))[0]
    
    return f'''
    <article class="card" data-category="{category_class}" data-title="{title}" data-summary="{summary}">
        <div class="card-header">
            <img src="{favicon}" alt="{source}" class="card-favicon" onerror="this.src='https://via.placeholder.com/32x32?text=AI'">
            <span class="card-source">{source}</span>
        </div>
        <h3 class="card-title"><a href="{url}" target="_blank" rel="noopener">{title}</a></h3>
        <p class="card-summary">{summary}</p>
        <div class="card-footer">
            <span class="card-category {category_class}">{cat_label}</span>
        </div>
    </article>'''

def get_all_archives():
    """获取所有存档文件"""
    archives = []
    if os.path.exists(ARCHIVE_DIR):
        for f in os.listdir(ARCHIVE_DIR):
            if f.endswith('.html'):
                date = f.replace('.html', '')
                archives.append((date, f))
    return sorted(archives, reverse=True)

def generate_archive_index():
    """生成归档索引页面"""
    archives = get_all_archives()
    
    html = generate_header("归档 - AI 日报", "历史资讯存档")
    html += '<h1>📂 资讯归档</h1>'
    html += '<p style="color: var(--text-secondary); margin-bottom: 24px;">点击日期查看当天所有资讯</p>'
    
    if archives:
        html += '<div class="archive-list">'
        for date, filename in archives:
            display_date = f"{date[:4]}年{date[5:7]}月{date[8:10]}日"
            html += f'''
            <div class="archive-item">
                <h3><a href="archives/{filename}">{display_date}</a></h3>
            </div>'''
        html += '</div>'
    else:
        html += '<div class="empty-state">暂无存档</div>'
    
    html += generate_footer()
    
    with open("/Users/alex/.openclaw/workspace/ai-daily-news/archive.html", 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✅ 生成 archive.html ({len(archives)} 个存档)")

def generate_category_pages(results):
    """生成分类页面"""
    for cat_id, (cat_name, cat_class) in CATEGORIES.items():
        items = results.get(cat_id, [])
        
        html = generate_header(f"{cat_name} - AI 日报", f"AI {cat_name}精选")
        html += f'<a href="index.html" class="back-link">← 返回首页</a>'
        html += f'<h1 class="category-header">{cat_name}</h1>'
        
        if items:
            html += f'<p style="color: var(--text-secondary); margin-bottom: 24px;">共 {len(items)} 条</p>'
            for item in items:
                html += generate_card(item, cat_class)
        else:
            html += '''
            <div class="empty-state">
                <p style="font-size: 3rem; margin-bottom: 16px;">📭</p>
                <h2>暂无相关内容</h2>
                <p style="color: var(--text-secondary); margin-top: 8px;">目前该分类下还没有资讯，请稍后再来~</p>
                <a href="index.html" style="display: inline-block; margin-top: 24px; padding: 12px 24px; background: var(--accent); color: white; border-radius: 8px;">← 返回首页</a>
            </div>'''
        
        html += generate_footer()
        
        filename = f"/Users/alex/.openclaw/workspace/ai-daily-news/{cat_id}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✅ 生成 {cat_id}.html ({len(items)} 条)")

def generate_daily_archive(results, date_str=None):
    """生成每日存档"""
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    
    all_items = []
    for cat_id, items in results.items():
        for item in items:
            item['_category'] = cat_id
            all_items.append(item)
    
    if not all_items:
        return
    
    html = generate_header(f"{date_str} - AI 日报", f"{date_str} 日AI资讯")
    html += '<div style="margin-bottom: 16px;">'
    html += '<a href="../index.html" class="back-link">← 返回首页</a> | '
    html += '<a href="../archive.html" class="back-link">📂 归档</a>'
    html += '</div>'
    html += f'<h1>📅 {date_str}</h1>'
    html += f'<p style="color: var(--text-secondary); margin-bottom: 24px;">共 {len(all_items)} 条资讯</p>'
    
    for item in all_items:
        cat_id = item.get('_category', 'news')
        cat_class = CATEGORIES.get(cat_id, ('', 'category-news'))[1]
        html += generate_card(item, cat_class)
    
    html += generate_footer()
    
    filename = f"{ARCHIVE_DIR}/{date_str}.html"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✅ 生成 archives/{date_str}.html ({len(all_items)} 条)")

def generate_search_index():
    """生成搜索索引数据"""
    all_items = []
    
    # 从存档目录读取所有历史数据
    if os.path.exists(ARCHIVE_DIR):
        import re
        for f in os.listdir(ARCHIVE_DIR):
            if f.endswith('.html'):
                date = f.replace('.html', '')
                # 简单解析，从HTML中提取标题和摘要
                try:
                    with open(f"{ARCHIVE_DIR}/{f}", 'r', encoding='utf-8') as file:
                        content = file.read()
                        # 提取标题
                        titles = re.findall(r'<h3 class="card-title"><a[^>]*>([^<]+)</a></h3>', content)
                        # 提取摘要
                        summaries = re.findall(r'<p class="card-summary">([^<]+)</p>', content)
                        # 提取链接
                        links = re.findall(r'<h3 class="card-title"><a href="([^"]+)"', content)
                        
                        for i, title in enumerate(titles):
                            all_items.append({
                                'title': title,
                                'summary': summaries[i] if i < len(summaries) else '',
                                'url': links[i] if i < len(links) else '#',
                                'date': date
                            })
                except:
                    pass
    
    # 保存搜索索引
    with open("/Users/alex/.openclaw/workspace/ai-daily-news/search_index.json", 'w', encoding='utf-8') as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 生成搜索索引 ({len(all_items)} 条)")

def generate_main_page(results):
    """生成主页面（保留原有功能）"""
    # 这里保留原有的完整HTML生成逻辑
    # 为节省篇幅，只生成简单的版本
    date_str = datetime.now().strftime("%Y-%m-%d")
    date_display = f"{date_str[5:7]}月{date_str[8:10]}日"
    
    # 统计
    total = sum(len(v) for v in results.values() if isinstance(v, list))
    
    # 生成分类HTML - 只显示有内容的分类
    all_cards_html = ''
    for cat_id, (cat_name, cat_class) in CATEGORIES.items():
        items = results.get(cat_id, [])
        if items:
            all_cards_html += f'<section id="{cat_id}" class="category-section">\n'
            all_cards_html += f'<h2 class="category-title">{cat_name}</h2>\n'
            for item in items:
                all_cards_html += generate_card(item, cat_class)
            all_cards_html += '</section>\n'
    
    # 分类导航 - 只显示有内容的分类
    category_nav = '\n'.join([
        f'<a href="{cat_id}.html" class="nav-category-link">{name}</a>'
        for cat_id, (name, _) in CATEGORIES.items()
        if results.get(cat_id, [])
    ])
    
    # 如果没有有内容的分类，显示提示
    if not category_nav:
        category_nav = '<span style="color: var(--text-muted);">暂无内容</span>'
    
    # 侧边栏分类 - 只显示有内容的分类
    sidebar_categories = '\n'.join([
        f'<li class="category-item"><a href="{cat_id}.html" class="category-link">{name}</a></li>'
        for cat_id, (name, _) in CATEGORIES.items()
        if results.get(cat_id, [])
    ])
    
    if not sidebar_categories:
        sidebar_categories = '<li class="category-item" style="color: var(--text-muted);">暂无分类</li>'
    
    # 侧边栏归档
    archives = get_all_archives()
    if archives:
        sidebar_dates = '\n'.join([
            f'<li class="date-item"><a href="archives/{f}" class="date-link">{d[5:7]}月{d[8:10]}日</a></li>'
            for d, f in archives[:10]
        ])
    else:
        sidebar_dates = '<li class="date-item">暂无存档</li>'
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI 日报 - {date_display} | 每日AI资讯</title>
    <meta name="description" content="每日AI新闻、技术文章、产品融资、人物观点 - 您的AI资讯助手">
    
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        :root {{
            --bg-primary: #0a0a0b;
            --bg-secondary: #141416;
            --bg-card: #1c1c1f;
            --bg-card-hover: #242428;
            --text-primary: #f4f4f5;
            --text-secondary: #a1a1aa;
            --text-muted: #71717a;
            --accent: #f97316;
            --accent-hover: #fb923c;
            --border: #27272a;
            --category-news: #ef4444;
            --category-tech: #3b82f6;
            --category-products: #22c55e;
            --category-funding: #eab308;
            --category-people: #a855f7;
            --category-opinions: #ec4899;
            --category-tutorial: #14b8a6;
            --category-fun: #f59e0b;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'PingFang SC', sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
        }}
        a {{ color: inherit; text-decoration: none; }}
        
        .subscribe-bar {{
            background: linear-gradient(135deg, #1e1e22 0%, #27272d 100%);
            border-bottom: 1px solid var(--border);
            padding: 12px 24px;
            text-align: center;
        }}
        .subscribe-content {{
            max-width: 800px; margin: 0 auto;
            display: flex; align-items: center; justify-content: center;
            gap: 16px; flex-wrap: wrap;
        }}
        .subscribe-text {{ color: var(--text-secondary); font-size: 0.9rem; }}
        .subscribe-text strong {{ color: var(--accent); }}
        
        .top-nav {{
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border);
            position: sticky; top: 0; z-index: 100;
        }}
        .nav-container {{
            max-width: 1400px; margin: 0 auto; padding: 16px 24px;
            display: flex; align-items: center; justify-content: space-between;
            flex-wrap: wrap; gap: 16px;
        }}
        .nav-brand {{ display: flex; align-items: center; gap: 16px; flex: 1; min-width: 300px; }}
        .nav-logo {{ font-size: 1.5rem; font-weight: bold; }}
        .nav-meta {{ display: flex; flex-direction: column; gap: 4px; }}
        .nav-subtitle {{ color: var(--text-secondary); font-size: 0.85rem; }}
        .nav-date {{ color: var(--text-muted); font-size: 0.8rem; }}
        
        .nav-categories {{
            display: flex; gap: 8px; flex-wrap: wrap;
        }}
        .nav-category-link {{
            padding: 8px 16px; border-radius: 20px;
            background: var(--bg-card); color: var(--text-secondary);
            font-size: 0.9rem; transition: all 0.2s;
        }}
        .nav-category-link:hover {{ background: var(--bg-card-hover); color: var(--text-primary); }}
        
        .main-layout {{
            max-width: 1400px; margin: 0 auto; padding: 24px;
            display: grid; grid-template-columns: 200px 1fr; gap: 24px;
        }}
        @media (max-width: 768px) {{
            .main-layout {{ grid-template-columns: 1fr; }}
            .sidebar {{ display: none; }}
        }}
        
        .sidebar {{ position: sticky; top: 80px; height: fit-content; }}
        .sidebar-section {{ background: var(--bg-secondary); border-radius: 12px; padding: 16px; margin-bottom: 16px; }}
        .sidebar-title {{ font-size: 0.9rem; color: var(--text-muted); margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.5px; }}
        .category-list, .date-list {{ list-style: none; }}
        .category-item, .date-item {{ margin-bottom: 8px; }}
        .category-link, .date-link {{ display: block; padding: 8px 12px; border-radius: 8px; color: var(--text-secondary); font-size: 0.9rem; }}
        .category-link:hover, .date-link:hover {{ background: var(--bg-card); color: var(--text-primary); }}
        
        .content {{ display: flex; flex-direction: column; gap: 32px; }}
        .category-section {{ scroll-margin-top: 100px; }}
        .category-title {{ font-size: 1.3rem; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 1px solid var(--border); }}
        
        .card {{
            background: var(--bg-card); border-radius: 12px; padding: 20px;
            margin-bottom: 16px; transition: transform 0.2s, box-shadow 0.2s;
        }}
        .card:hover {{ transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.3); }}
        .card-header {{ display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }}
        .card-favicon {{ width: 20px; height: 20px; border-radius: 4px; }}
        .card-source {{ color: var(--text-secondary); font-size: 0.85rem; }}
        .card-title {{ font-size: 1.1rem; margin-bottom: 8px; }}
        .card-title a {{ color: var(--text-primary); }}
        .card-title a:hover {{ color: var(--accent); }}
        .card-summary {{ color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 12px; }}
        .card-footer {{ display: flex; justify-content: space-between; align-items: center; }}
        .card-category {{ padding: 4px 12px; border-radius: 12px; font-size: 0.8rem; }}
        .category-news {{ background: rgba(239,68,68,0.2); color: #ef4444; }}
        .category-tech {{ background: rgba(59,130,246,0.2); color: #3b82f6; }}
        .category-products {{ background: rgba(34,197,94,0.2); color: #22c55e; }}
        .category-funding {{ background: rgba(234,179,8,0.2); color: #eab308; }}
        .category-people {{ background: rgba(168,85,247,0.2); color: #a855f7; }}
        .category-opinions {{ background: rgba(236,72,153,0.2); color: #ec4899; }}
        .category-tutorial {{ background: rgba(20,184,166,0.2); color: #14b8a6; }}
        .category-fun {{ background: rgba(245,158,11,0.2); color: #f59e0b; }}
        
        footer {{ text-align: center; padding: 40px 20px; color: var(--text-muted); border-top: 1px solid var(--border); margin-top: 40px; }}
        footer a {{ color: var(--accent); }}
    </style>
</head>
<body>
    <div class="subscribe-bar">
        <div class="subscribe-content">
            <span class="subscribe-text">📬 订阅获得最新AI资讯 | <strong>每日更新</strong> | 精选全球AI新闻</span>
        </div>
    </div>
    
    <nav class="top-nav">
        <div class="nav-container">
            <div class="nav-brand">
                <a href="index.html" class="nav-logo">🤖 <span>AI 日报</span></a>
                <div class="nav-meta">
                    <span class="nav-subtitle">每日 AI 新闻资讯、技术文章、产品融资和人物观点</span>
                    <span class="nav-date">{date_display} · {total}条资讯</span>
                </div>
            </div>
            <div class="nav-categories">
                {category_nav}
                <a href="archive.html" class="nav-category-link">📂 归档</a>
            </div>
        </div>
    </nav>
    
    <div class="main-layout">
        <aside class="sidebar">
            <div class="sidebar-section">
                <h3 class="sidebar-title">📂 分类</h3>
                <ul class="category-list">
                    {sidebar_categories}
                </ul>
            </div>
            <div class="sidebar-section">
                <h3 class="sidebar-title">📅 归档</h3>
                <ul class="date-list">
                    {sidebar_dates}
                    <li class="date-item"><a href="archive.html" class="date-link" style="color: var(--accent);">查看全部 →</a></li>
                </ul>
            </div>
        </aside>
        
        <main class="content">
            {all_cards_html}
        </main>
    </div>
    
    <footer>
        <p>🤖 由 <strong>AI 日报</strong> 自动生成 · <a href="https://github.com/wallerwvw-cell/ai-daily-news" target="_blank">GitHub</a> · <a href="https://wallerwvw-cell.github.io/ai-daily-news/" target="_blank">在线阅读</a></p>
        <p>汇聚 {total} 条精选AI资讯 · 每天早上8点更新</p>
    </footer>
</body>
</html>'''
    
    with open("/Users/alex/.openclaw/workspace/ai-daily-news/index.html", 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✅ 生成 index.html ({total} 条资讯)")

def main():
    """主函数"""
    print("🚀 开始生成 AI 日报...")
    
    # 加载数据
    results = load_search_results()
    
    # 1. 生成主页面
    generate_main_page(results)
    
    # 2. 生成分类页面
    generate_category_pages(results)
    
    # 3. 生成每日存档
    generate_daily_archive(results)
    
    # 4. 生成归档索引
    generate_archive_index()
    
    # 5. 生成搜索索引
    generate_search_index()
    
    print("\n🎉 全部生成完成!")
    
    # 统计
    total = sum(len(v) for v in results.values() if isinstance(v, list))
    print(f"\n📊 统计:")
    print(f"   - 主页面: index.html ({total} 条)")
    print(f"   - 分类页面: {len(CATEGORIES)} 个")
    print(f"   - 每日存档: 1 个")
    print(f"   - 归档索引: archive.html")
    print(f"   - 搜索索引: search_index.json")

if __name__ == "__main__":
    main()
