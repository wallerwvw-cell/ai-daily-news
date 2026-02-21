#!/usr/bin/env python3
"""
AI 日报生成脚本 - 单语言版本
参考 orangedatamining.com/blog/ 排版风格
"""

import json
import os
import re
from datetime import datetime
import random

# 搜索结果文件路径
SEARCH_RESULTS = "/Users/alex/.openclaw/workspace/ai-daily-news/search_results.json"

def load_search_results():
    """加载搜索结果"""
    if os.path.exists(SEARCH_RESULTS):
        with open(SEARCH_RESULTS, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"news": [], "tech": [], "tutorial": [], "fun": []}

def extract_domain(url):
    """提取域名"""
    try:
        from urllib.parse import urlparse
        return urlparse(url).netloc.replace('www.', '')
    except:
        return ''

def get_favicon_url(url):
    """获取 favicon URL"""
    domain = extract_domain(url)
    if domain:
        return f"https://www.google.com/s2/favicons?domain={domain}&sz=128"
    return "https://www.google.com/s2/favicons?domain=example.com&sz=128"

def get_random_time():
    """生成随机时间（当天内的随机时间）"""
    hour = random.randint(6, 23)
    minute = random.randint(0, 59)
    return f"{hour:02d}:{minute:02d}"

def clean_html(text):
    """清理 HTML 标签"""
    if not text:
        return ""
    # 移除 HTML 标签
    text = re.sub(r'<[^>]+>', '', text)
    # 移除多余空白
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def generate_card(item, category_class, date_str=''):
    """生成卡片 HTML - 带摘要和源链接"""
    title = item.get('title', '')
    # 优先使用提取的摘要，否则使用 snippet
    summary = item.get('summary', '') or item.get('snippet', '')
    if not summary:
        summary = "点击查看详细内容..."
    # 限制摘要长度
    if len(summary) > 200:
        summary = summary[:200] + '...'
    
    url = item.get('url', '#')
    source = item.get('source', '') or extract_domain(url)
    favicon = get_favicon_url(url)
    time_str = item.get('time', get_random_time())
    
    return f'''
        <article class="card">
            <div class="card-image">
                <img src="{favicon}" alt="{source}" onerror="this.src='https://via.placeholder.com/120x80?text=AI'">
            </div>
            <div class="card-content">
                <span class="card-category {category_class}">{get_category_label(category_class)}</span>
                <h3><a href="{url}" target="_blank" rel="noopener">{title}</a></h3>
                <p class="card-summary">{summary}</p>
                <div class="card-meta">
                    <span class="card-source">📌 {source}</span>
                    <span class="card-date">📅 {date_str} {time_str}</span>
                </div>
                <div class="card-source-link">
                    <a href="{url}" target="_blank" rel="noopener">🔗 查看原文 →</a>
                </div>
            </div>
        </article>'''

def get_category_label(cat_class):
    """获取分类标签"""
    labels = {
        'category-news': '📰 新闻',
        'category-tech': '💻 技术',
        'category-tutorial': '📚 教程',
        'category-fun': '🎉 趣闻'
    }
    return labels.get(cat_class, '')

def generate_sidebar_datelist(dates):
    """生成左侧边栏日期导航"""
    date_labels = {d: f"{d.split('-')[1]}月{d.split('-')[2]}日" for d in dates}
    
    items = []
    for date in dates:
        items.append(f'''
            <li class="date-item">
                <a href="#date-{date}" class="date-link">
                    <span class="date-label">{date_labels[date]}</span>
                </a>
            </li>''')
    
    return '\n'.join(items)

def generate_category_nav():
    """生成顶部分类导航"""
    categories = [
        ('news', '📰 新闻', '#news'),
        ('tech', '💻 技术', '#tech'),
        ('tutorial', '📚 教程', '#tutorial'),
        ('fun', '🎉 趣闻', '#fun')
    ]
    
    items = []
    for cat_id, cat_name, cat_href in categories:
        items.append(f'''
            <a href="{cat_href}" class="nav-category-link" data-category="{cat_id}">{cat_name}</a>''')
    
    return '\n'.join(items)

def generate_sidebar_category_nav():
    """生成左侧分类导航"""
    categories = [
        ('all', '📋 全部', '#'),
        ('category-news', '📰 新闻', '#news'),
        ('category-tech', '💻 技术', '#tech'),
        ('category-tutorial', '📚 教程', '#tutorial'),
        ('category-fun', '🎉 趣闻', '#fun')
    ]
    
    items = []
    for cat_class, cat_name, cat_href in categories:
        items.append(f'''
            <li class="category-item">
                <a href="{cat_href}" class="category-link {cat_class}" data-filter="{cat_class}">
                    {cat_name}
                </a>
            </li>''')
    
    return '\n'.join(items)

def generate_html(news, tech, tutorial, fun):
    """生成完整 HTML - 单语言版本，参考 orangedatamining.com 排版风格"""
    date = datetime.now()
    date_str = date.strftime('%Y-%m-%d')
    date_display = date.strftime('%Y年%m月%d日 %A')
    title = "AI 日报"
    subtitle = "每日 AI 新闻资讯、技术文章、教程和趣闻"
    
    # 生成所有卡片并按日期和分类分组
    all_items = []
    for item in news:
        item['_category'] = 'category-news'
        item['_date'] = date_str
        all_items.append(item)
    for item in tech:
        item['_category'] = 'category-tech'
        item['_date'] = date_str
        all_items.append(item)
    for item in tutorial:
        item['_category'] = 'category-tutorial'
        item['_date'] = date_str
        all_items.append(item)
    for item in fun:
        item['_category'] = 'category-fun'
        item['_date'] = date_str
        all_items.append(item)
    
    # 按日期分组
    dates = [date_str]
    date_groups = {date_str: all_items}
    
    # 生成侧边栏
    sidebar_dates = generate_sidebar_datelist(dates)
    sidebar_categories = generate_sidebar_category_nav()
    
    # 按分类生成卡片
    sections_html = []
    
    # 新闻 section
    if news:
        news_cards = [generate_card(item, 'category-news', date_str) for item in news]
        sections_html.append(f'''
        <section class="category-section" id="news">
            <div class="category-header">
                <h2 class="category-title">📰 AI 新闻</h2>
            </div>
            <div class="cards-grid">
                {' '.join(news_cards)}
            </div>
        </section>''')
    
    # 技术 section
    if tech:
        tech_cards = [generate_card(item, 'category-tech', date_str) for item in tech]
        sections_html.append(f'''
        <section class="category-section" id="tech">
            <div class="category-header">
                <h2 class="category-title">💻 技术文章</h2>
            </div>
            <div class="cards-grid">
                {' '.join(tech_cards)}
            </div>
        </section>''')
    
    # 教程 section
    if tutorial:
        tutorial_cards = [generate_card(item, 'category-tutorial', date_str) for item in tutorial]
        sections_html.append(f'''
        <section class="category-section" id="tutorial">
            <div class="category-header">
                <h2 class="category-title">📚 教程</h2>
            </div>
            <div class="cards-grid">
                {' '.join(tutorial_cards)}
            </div>
        </section>''')
    
    # 趣闻 section
    if fun:
        fun_cards = [generate_card(item, 'category-fun', date_str) for item in fun]
        sections_html.append(f'''
        <section class="category-section" id="fun">
            <div class="category-header">
                <h2 class="category-title">🎉 趣闻</h2>
            </div>
            <div class="cards-grid">
                {' '.join(fun_cards)}
            </div>
        </section>''')
    
    all_cards_html = '\n'.join(sections_html)
    category_nav = generate_category_nav()
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - {date.strftime('%Y-%m-%d')}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        :root {{
            --bg-primary: #0f0f0f;
            --bg-secondary: #1a1a1a;
            --bg-card: #242424;
            --text-primary: #f5f5f5;
            --text-secondary: #a0a0a0;
            --text-muted: #666666;
            --accent: #ff6b35;
            --accent-hover: #ff8c5a;
            --border: #333333;
            --category-news: #e74c3c;
            --category-tech: #3498db;
            --category-tutorial: #2ecc71;
            --category-fun: #9b59b6;
            --sidebar-width: 120px;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            min-height: 100vh;
        }}
        
        /* 顶部导航 */
        .top-nav {{
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border);
            padding: 12px 24px;
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        
        .nav-container {{
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 12px;
        }}
        
        .nav-brand {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        
        .nav-logo {{
            font-size: 1.3rem;
            font-weight: 700;
            color: var(--text-primary);
            text-decoration: none;
        }}
        
        .nav-logo span {{
            color: var(--accent);
        }}
        
        .nav-subtitle {{
            color: var(--text-secondary);
            font-size: 0.85rem;
        }}
        
        .nav-categories {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }}
        
        .nav-category-link {{
            padding: 8px 16px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 500;
            font-size: 0.9rem;
            transition: all 0.2s;
            background: var(--bg-card);
            color: var(--text-secondary);
        }}
        
        .nav-category-link:hover {{
            background: var(--border);
            color: var(--text-primary);
        }}
        
        /* 主布局 */
        .main-layout {{
            max-width: 1400px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: var(--sidebar-width) 1fr;
            gap: 24px;
            padding: 24px;
        }}
        
        @media (max-width: 900px) {{
            .main-layout {{
                grid-template-columns: 1fr;
            }}
        }}
        
        /* 左侧边栏 - 缩小宽度 */
        .sidebar {{
            position: sticky;
            top: 80px;
            height: fit-content;
        }}
        
        .sidebar-section {{
            background: var(--bg-secondary);
            border-radius: 12px;
            padding: 16px 12px;
            border: 1px solid var(--border);
            margin-bottom: 16px;
        }}
        
        .sidebar-title {{
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-muted);
            margin-bottom: 12px;
            font-weight: 600;
            text-align: center;
        }}
        
        .category-list, .date-list {{
            list-style: none;
        }}
        
        .category-item, .date-item {{
            margin-bottom: 6px;
        }}
        
        .category-link, .date-link {{
            display: block;
            padding: 8px 10px;
            border-radius: 6px;
            text-decoration: none;
            color: var(--text-secondary);
            transition: all 0.2s;
            font-weight: 500;
            font-size: 0.85rem;
            text-align: center;
        }}
        
        .category-link:hover, .date-link:hover {{
            background: var(--bg-card);
            color: var(--accent);
        }}
        
        .category-link.active {{
            background: var(--accent);
            color: #fff;
        }}
        
        /* 右侧内容 */
        .content {{
            min-width: 0;
        }}
        
        /* 分类区块 */
        .category-section {{
            margin-bottom: 40px;
        }}
        
        .category-header {{
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 2px solid var(--border);
        }}
        
        .category-title {{
            font-size: 1.3rem;
            font-weight: 600;
            color: var(--text-primary);
        }}
        
        /* 卡片网格 */
        .cards-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 16px;
        }}
        
        /* 卡片样式 */
        .card {{
            background: var(--bg-secondary);
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid var(--border);
            transition: all 0.3s ease;
            display: flex;
            flex-direction: column;
        }}
        
        .card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.4);
            border-color: var(--accent);
        }}
        
        .card-image {{
            height: 70px;
            background: var(--bg-card);
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 10px;
            border-bottom: 1px solid var(--border);
        }}
        
        .card-image img {{
            width: 56px;
            height: 56px;
            object-fit: contain;
            border-radius: 8px;
        }}
        
        .card-content {{
            padding: 16px;
            display: flex;
            flex-direction: column;
            flex: 1;
        }}
        
        .card-category {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 10px;
            width: fit-content;
        }}
        
        .category-news {{ background: var(--category-news); color: #fff; }}
        .category-tech {{ background: var(--category-tech); color: #fff; }}
        .category-tutorial {{ background: var(--category-tutorial); color: #fff; }}
        .category-fun {{ background: var(--category-fun); color: #fff; }}
        
        .card h3 {{
            font-size: 1rem;
            margin-bottom: 8px;
            line-height: 1.4;
        }}
        
        .card h3 a {{
            color: var(--text-primary);
            text-decoration: none;
            transition: color 0.2s;
        }}
        
        .card h3 a:hover {{
            color: var(--accent);
        }}
        
        .card-summary {{
            color: var(--text-secondary);
            font-size: 0.85rem;
            line-height: 1.5;
            margin-bottom: 12px;
            flex: 1;
        }}
        
        .card-meta {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 6px;
            font-size: 0.75rem;
            color: var(--text-muted);
            padding-top: 10px;
            border-top: 1px solid var(--border);
        }}
        
        .card-source, .card-date {{
            display: flex;
            align-items: center;
            gap: 4px;
        }}
        
        .card-source-link {{
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid var(--border);
        }}
        
        .card-source-link a {{
            color: var(--accent);
            text-decoration: none;
            font-size: 0.85rem;
            font-weight: 500;
            transition: color 0.2s;
        }}
        
        .card-source-link a:hover {{
            color: var(--accent-hover);
            text-decoration: underline;
        }}
        
        /* 空状态 */
        .empty-msg {{
            color: var(--text-muted);
            text-align: center;
            padding: 40px;
            grid-column: 1 / -1;
        }}
        
        /* 页脚 */
        footer {{
            text-align: center;
            padding: 24px;
            color: var(--text-muted);
            font-size: 0.8rem;
            border-top: 1px solid var(--border);
            margin-top: 24px;
        }}
        
        footer a {{
            color: var(--accent);
            text-decoration: none;
        }}
        
        footer a:hover {{
            text-decoration: underline;
        }}
        
        /* 响应式 */
        @media (max-width: 768px) {{
            .nav-container {{
                flex-direction: column;
                text-align: center;
            }}
            
            .cards-grid {{
                grid-template-columns: 1fr;
            }}
            
            .sidebar {{
                position: static;
            }}
            
            .nav-categories {{
                justify-content: center;
            }}
        }}
    </style>
</head>
<body>
    <!-- 顶部导航 -->
    <nav class="top-nav">
        <div class="nav-container">
            <div class="nav-brand">
                <a href="#" class="nav-logo">🐟 <span>AI</span> {title}</a>
                <span class="nav-subtitle">{date_display}</span>
            </div>
            <div class="nav-categories">
                {category_nav}
            </div>
        </div>
    </nav>
    
    <!-- 主布局 -->
    <div class="main-layout">
        <!-- 左侧边栏 - 窄版 -->
        <aside class="sidebar">
            <div class="sidebar-section">
                <h3 class="sidebar-title">📂 分类</h3>
                <ul class="category-list">
                    {sidebar_categories}
                </ul>
            </div>
            <div class="sidebar-section">
                <h3 class="sidebar-title">📅 日期</h3>
                <ul class="date-list">
                    {sidebar_dates}
                </ul>
            </div>
        </aside>
        
        <!-- 右侧内容 -->
        <main class="content">
            {all_cards_html}
        </main>
    </div>
    
    <footer>
        <p>由 🐟 小鱼 自动生成 | <a href="https://github.com/wallerwvw-cell/ai-daily-news" target="_blank">GitHub</a></p>
    </footer>
    
    <script>
        // 平滑滚动
        document.querySelectorAll('.category-link, .date-link, .nav-category-link').forEach(link => {{
            link.addEventListener('click', function(e) {{
                const href = this.getAttribute('href');
                if (href === '#') return;
                
                e.preventDefault();
                const targetId = href.substring(1);
                const target = document.getElementById(targetId);
                if (target) {{
                    target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                }}
            }});
        }});
        
        // 分类筛选功能
        document.querySelectorAll('.category-link').forEach(link => {{
            link.addEventListener('click', function(e) {{
                e.preventDefault();
                const filter = this.getAttribute('data-filter');
                
                // 更新激活状态
                document.querySelectorAll('.category-link').forEach(l => l.classList.remove('active'));
                this.classList.add('active');
                
                // 筛选卡片
                const cards = document.querySelectorAll('.card');
                cards.forEach(card => {{
                    if (filter === 'all' || filter === '#') {{
                        card.style.display = 'flex';
                    }} else {{
                        const category = card.querySelector('.card-category').className;
                        if (category.includes(filter.replace('category-', ''))) {{
                            card.style.display = 'flex';
                        }} else {{
                            card.style.display = 'none';
                        }}
                    }}
                }});
            }});
        }});
        
        // 滚动高亮当前分类
        const observer = new IntersectionObserver((entries) => {{
            entries.forEach(entry => {{
                if (entry.isIntersecting) {{
                    const id = entry.target.id;
                    document.querySelectorAll('.category-link').forEach(link => {{
                        link.classList.remove('active');
                        if (link.getAttribute('href') === '#' + id) {{
                            link.classList.add('active');
                        }}
                    }});
                }}
            }});
        }}, {{ threshold: 0.3 }});
        
        document.querySelectorAll('.category-section').forEach(section => {{
            observer.observe(section);
        }});
    </script>
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
    
    with open("/Users/alex/.openclaw/workspace/ai-daily-news/index.html", 'w', encoding='utf-8') as f:
        f.write(html)
    print("✅ 生成完成: index.html")

if __name__ == "__main__":
    main()
