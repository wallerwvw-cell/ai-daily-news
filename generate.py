#!/usr/bin/env python3
"""
AI 日报生成脚本 - 多分类版本
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
    return {
        "news": [], "tech": [], "tutorial": [], "fun": [],
        "products": [], "funding": [], "people": [], "opinions": []
    }

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
    """生成卡片 HTML - 优化版卡片设计"""
    title = item.get('title', '')
    # 优先使用提取的摘要，否则使用 snippet
    summary = item.get('summary', '') or item.get('snippet', '')
    if not summary:
        summary = "点击查看详细内容..."
    # 限制摘要长度
    if len(summary) > 180:
        summary = summary[:180] + '...'
    
    url = item.get('url', '#')
    source = item.get('source', '') or extract_domain(url)
    favicon = get_favicon_url(url)
    time_str = item.get('time', get_random_time())
    
    return f'''
        <article class="card">
            <div class="card-header">
                <img src="{favicon}" alt="{source}" class="card-favicon" onerror="this.src='https://via.placeholder.com/32x32?text=AI'">
                <span class="card-source">{source}</span>
            </div>
            <h3 class="card-title"><a href="{url}" target="_blank" rel="noopener">{title}</a></h3>
            <p class="card-summary">{summary}</p>
            <div class="card-footer">
                <span class="card-category {category_class}">{get_category_label(category_class)}</span>
                <span class="card-date">🕐 {time_str}</span>
            </div>
        </article>'''

def get_category_label(cat_class):
    """获取分类标签"""
    labels = {
        'category-news': '📰 新闻',
        'category-tech': '💻 技术',
        'category-tutorial': '📚 教程',
        'category-fun': '🎉 趣闻',
        'category-products': '🚀 AI产品',
        'category-funding': '💰 融资',
        'category-people': '👤 人物',
        'category-opinions': '💡 观点'
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
        ('products', '🚀 产品', '#products'),
        ('funding', '💰 融资', '#funding'),
        ('people', '👤 人物', '#people'),
        ('opinions', '💡 观点', '#opinions'),
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
        ('category-products', '🚀 产品', '#products'),
        ('category-funding', '💰 融资', '#funding'),
        ('category-people', '👤 人物', '#people'),
        ('category-opinions', '💡 观点', '#opinions'),
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

def generate_section(cat_id, cat_title, cat_items, cat_class, date_str):
    """生成分类区块 HTML"""
    if not cat_items:
        return ''
    
    cards = [generate_card(item, cat_class, date_str) for item in cat_items]
    return f'''
        <section class="category-section" id="{cat_id}">
            <div class="category-header">
                <h2 class="category-title">{cat_title}</h2>
                <span class="category-count">{len(cat_items)} 条</span>
            </div>
            <div class="cards-grid">
                {' '.join(cards)}
            </div>
        </section>'''

def generate_html(data):
    """生成完整 HTML - 多分类版本"""
    date = datetime.now()
    date_str = date.strftime('%Y-%m-%d')
    date_display = date.strftime('%Y年%m月%d日 %A')
    title = "AI 日报"
    subtitle = "每日 AI 新闻资讯、技术文章、产品融资和人物观点"
    
    # 获取各分类数据
    news = data.get('news', [])
    tech = data.get('tech', [])
    tutorial = data.get('tutorial', [])
    fun = data.get('fun', [])
    products = data.get('products', [])
    funding = data.get('funding', [])
    people = data.get('people', [])
    opinions = data.get('opinions', [])
    
    # 生成所有分类区块
    sections = []
    
    # 新闻
    if news:
        sections.append(generate_section('news', '📰 AI 新闻', news, 'category-news', date_str))
    
    # 技术
    if tech:
        sections.append(generate_section('tech', '💻 技术文章', tech, 'category-tech', date_str))
    
    # 产品
    if products:
        sections.append(generate_section('products', '🚀 AI产品', products, 'category-products', date_str))
    
    # 融资
    if funding:
        sections.append(generate_section('funding', '💰 AI融资', funding, 'category-funding', date_str))
    
    # 人物
    if people:
        sections.append(generate_section('people', '👤 AI人物', people, 'category-people', date_str))
    
    # 观点
    if opinions:
        sections.append(generate_section('opinions', '💡 AI观点', opinions, 'category-opinions', date_str))
    
    # 教程
    if tutorial:
        sections.append(generate_section('tutorial', '📚 教程', tutorial, 'category-tutorial', date_str))
    
    # 趣闻
    if fun:
        sections.append(generate_section('fun', '🎉 趣闻', fun, 'category-fun', date_str))
    
    all_cards_html = '\n'.join(sections)
    category_nav = generate_category_nav()
    
    # 侧边栏日期（当天）
    dates = [date_str]
    sidebar_dates = generate_sidebar_datelist(dates)
    sidebar_categories = generate_sidebar_category_nav()
    
    # 计算总数
    total_count = len(news) + len(tech) + len(tutorial) + len(fun) + len(products) + len(funding) + len(people) + len(opinions)
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - {date.strftime('%Y-%m-%d')} | 每日AI资讯</title>
    <meta name="description" content="每日AI新闻、技术文章、产品融资、人物观点 - 您的AI资讯助手">
    
    <!-- Open Graph -->
    <meta property="og:title" content="{title} - {date.strftime('%Y年%m月%d日')}">
    <meta property="og:description" content="{subtitle}">
    <meta property="og:type" content="website">
    
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
            --accent-light: rgba(249, 115, 22, 0.15);
            --border: #27272a;
            --border-light: #3f3f46;
            
            /* 分类颜色 */
            --category-news: #ef4444;
            --category-tech: #3b82f6;
            --category-products: #22c55e;
            --category-funding: #eab308;
            --category-people: #a855f7;
            --category-opinions: #ec4899;
            --category-tutorial: #14b8a6;
            --category-fun: #f59e0b;
            
            --sidebar-width: 140px;
            --header-height: 64px;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'PingFang SC', sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            min-height: 100vh;
        }}
        
        /* 订阅提示条 */
        .subscribe-bar {{
            background: linear-gradient(135deg, #1e1e22 0%, #27272d 100%);
            border-bottom: 1px solid var(--border);
            padding: 12px 24px;
            text-align: center;
        }}
        
        .subscribe-content {{
            max-width: 800px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 16px;
            flex-wrap: wrap;
        }}
        
        .subscribe-text {{
            color: var(--text-secondary);
            font-size: 0.9rem;
        }}
        
        .subscribe-text strong {{
            color: var(--accent);
        }}
        
        .subscribe-btn {{
            background: var(--accent);
            color: #fff;
            padding: 8px 20px;
            border-radius: 20px;
            text-decoration: none;
            font-weight: 600;
            font-size: 0.85rem;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}
        
        .subscribe-btn:hover {{
            background: var(--accent-hover);
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3);
        }}
        
        /* 顶部导航 */
        .top-nav {{
            background: rgba(20, 20, 22, 0.95);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border);
            padding: 0 24px;
            position: sticky;
            top: 0;
            z-index: 100;
            height: var(--header-height);
            display: flex;
            align-items: center;
        }}
        
        .nav-container {{
            max-width: 1600px;
            margin: 0 auto;
            width: 100%;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 20px;
        }}
        
        .nav-brand {{
            display: flex;
            align-items: center;
            gap: 12px;
            flex-shrink: 0;
        }}
        
        .nav-logo {{
            font-size: 1.4rem;
            font-weight: 800;
            color: var(--text-primary);
            text-decoration: none;
            letter-spacing: -0.5px;
        }}
        
        .nav-logo span {{
            color: var(--accent);
        }}
        
        .nav-meta {{
            display: flex;
            flex-direction: column;
            gap: 2px;
        }}
        
        .nav-subtitle {{
            color: var(--text-secondary);
            font-size: 0.75rem;
        }}
        
        .nav-date {{
            color: var(--text-muted);
            font-size: 0.7rem;
        }}
        
        .nav-categories {{
            display: flex;
            gap: 4px;
            flex-wrap: wrap;
            justify-content: flex-end;
        }}
        
        .nav-category-link {{
            padding: 6px 12px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 500;
            font-size: 0.8rem;
            transition: all 0.2s;
            background: transparent;
            color: var(--text-secondary);
            white-space: nowrap;
        }}
        
        .nav-category-link:hover {{
            background: var(--bg-card);
            color: var(--text-primary);
        }}
        
        /* 主布局 */
        .main-layout {{
            max-width: 1600px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: var(--sidebar-width) 1fr;
            gap: 20px;
            padding: 24px 20px;
        }}
        
        @media (max-width: 1100px) {{
            .main-layout {{
                grid-template-columns: 1fr;
            }}
            .sidebar {{
                display: none;
            }}
        }}
        
        /* 左侧边栏 */
        .sidebar {{
            position: sticky;
            top: calc(var(--header-height) + 24px);
            height: fit-content;
        }}
        
        .sidebar-section {{
            background: var(--bg-secondary);
            border-radius: 12px;
            padding: 16px;
            border: 1px solid var(--border);
            margin-bottom: 16px;
        }}
        
        .sidebar-title {{
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: var(--text-muted);
            margin-bottom: 12px;
            font-weight: 600;
        }}
        
        .category-list, .date-list {{
            list-style: none;
        }}
        
        .category-item, .date-item {{
            margin-bottom: 4px;
        }}
        
        .category-link, .date-link {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 10px;
            border-radius: 6px;
            text-decoration: none;
            color: var(--text-secondary);
            transition: all 0.2s;
            font-weight: 500;
            font-size: 0.8rem;
        }}
        
        .category-link:hover, .date-link:hover {{
            background: var(--bg-card);
            color: var(--accent);
        }}
        
        .category-link.active {{
            background: var(--accent-light);
            color: var(--accent);
        }}
        
        /* 右侧内容 */
        .content {{
            min-width: 0;
        }}
        
        /* 分类区块 */
        .category-section {{
            margin-bottom: 36px;
        }}
        
        .category-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 18px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--border);
        }}
        
        .category-title {{
            font-size: 1.2rem;
            font-weight: 700;
            color: var(--text-primary);
        }}
        
        .category-count {{
            background: var(--bg-card);
            color: var(--text-muted);
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 500;
        }}
        
        /* 卡片网格 */
        .cards-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 16px;
        }}
        
        @media (max-width: 480px) {{
            .cards-grid {{
                grid-template-columns: 1fr;
            }}
        }}
        
        /* 卡片样式 - 优化版 */
        .card {{
            background: var(--bg-secondary);
            border-radius: 14px;
            overflow: hidden;
            border: 1px solid var(--border);
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            flex-direction: column;
            position: relative;
        }}
        
        .card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 16px 40px rgba(0, 0, 0, 0.4);
            border-color: var(--border-light);
        }}
        
        .card:hover .card-title a {{
            color: var(--accent);
        }}
        
        .card-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 14px 16px 0;
        }}
        
        .card-favicon {{
            width: 24px;
            height: 24px;
            border-radius: 6px;
            object-fit: contain;
            background: var(--bg-card);
            padding: 2px;
        }}
        
        .card-source {{
            color: var(--text-muted);
            font-size: 0.75rem;
            font-weight: 500;
        }}
        
        .card-title {{
            font-size: 0.95rem;
            font-weight: 600;
            line-height: 1.45;
            padding: 10px 16px;
            margin: 0;
        }}
        
        .card-title a {{
            color: var(--text-primary);
            text-decoration: none;
            transition: color 0.2s;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}
        
        .card-summary {{
            color: var(--text-secondary);
            font-size: 0.82rem;
            line-height: 1.55;
            padding: 0 16px;
            flex: 1;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}
        
        .card-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 14px 16px;
            margin-top: auto;
            border-top: 1px solid var(--border);
        }}
        
        .card-category {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.3px;
        }}
        
        .category-news {{ background: var(--category-news); color: #fff; }}
        .category-tech {{ background: var(--category-tech); color: #fff; }}
        .category-products {{ background: var(--category-products); color: #fff; }}
        .category-funding {{ background: var(--category-funding); color: #000; }}
        .category-people {{ background: var(--category-people); color: #fff; }}
        .category-opinions {{ background: var(--category-opinions); color: #fff; }}
        .category-tutorial {{ background: var(--category-tutorial); color: #fff; }}
        .category-fun {{ background: var(--category-fun); color: #000; }}
        
        .card-date {{
            color: var(--text-muted);
            font-size: 0.75rem;
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
            padding: 32px 24px;
            color: var(--text-muted);
            font-size: 0.8rem;
            border-top: 1px solid var(--border);
            margin-top: 24px;
            background: var(--bg-secondary);
        }}
        
        footer a {{
            color: var(--accent);
            text-decoration: none;
        }}
        
        footer a:hover {{
            text-decoration: underline;
        }}
        
        .footer-stats {{
            margin-top: 12px;
            color: var(--text-muted);
            font-size: 0.75rem;
        }}
        
        /* 响应式 */
        @media (max-width: 768px) {{
            .nav-container {{
                flex-direction: column;
                padding: 12px 0;
                gap: 12px;
            }}
            
            .nav-brand {{
                width: 100%;
                justify-content: center;
            }}
            
            .nav-meta {{
                display: none;
            }}
            
            .nav-categories {{
                width: 100%;
                justify-content: center;
            }}
            
            .subscribe-content {{
                flex-direction: column;
                gap: 10px;
            }}
            
            .sidebar {{
                position: static;
                display: none;
            }}
        }}
        
        /* 滚动条 */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: var(--bg-primary);
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: var(--border);
            border-radius: 4px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: var(--border-light);
        }}
    </style>
</head>
<body>
    <!-- 订阅提示条 -->
    <div class="subscribe-bar">
        <div class="subscribe-content">
            <span class="subscribe-text">📬 订阅获得最新AI资讯 | <strong>每日更新</strong> | 精选全球AI新闻</span>
            <a href="#" class="subscribe-btn">📧 立即订阅</a>
        </div>
    </div>
    
    <!-- 顶部导航 -->
    <nav class="top-nav">
        <div class="nav-container">
            <div class="nav-brand">
                <a href="#" class="nav-logo">🤖 AI <span>{title}</span></a>
                <div class="nav-meta">
                    <span class="nav-subtitle">{subtitle}</span>
                    <span class="nav-date">{date_display} · {total_count}条资讯</span>
                </div>
            </div>
            <div class="nav-categories">
                {category_nav}
            </div>
        </div>
    </nav>
    
    <!-- 主布局 -->
    <div class="main-layout">
        <!-- 左侧边栏 -->
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
        <p>🤖 由 <strong>AI 日报</strong> 自动生成 · <a href="https://github.com/wallerwvw-cell/ai-daily-news" target="_blank">GitHub</a></p>
        <p class="footer-stats">汇聚 {total_count} 条精选AI资讯 · 每天早上8点更新</p>
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
                    const offset = 100;
                    const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - offset;
                    window.scrollTo({{
                        top: targetPosition,
                        behavior: 'smooth'
                    }});
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
        const observerOptions = {{
            rootMargin: '-100px 0px -60% 0px',
            threshold: 0
        }};
        
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
        }}, observerOptions);
        
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
    
    html = generate_html(results)
    
    with open("/Users/alex/.openclaw/workspace/ai-daily-news/index.html", 'w', encoding='utf-8') as f:
        f.write(html)
    
    # 统计
    total = sum(len(v) for v in results.values() if isinstance(v, list))
    print(f"✅ 生成完成: index.html (共 {total} 条资讯)")
    
    # 分类统计
    for cat, items in results.items():
        if isinstance(items, list) and items:
            print(f"   - {cat}: {len(items)} 条")

if __name__ == "__main__":
    main()
