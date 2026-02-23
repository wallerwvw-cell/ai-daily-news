#!/usr/bin/env python3
"""
AI 日报 RSS Feed 生成脚本
"""

import json
import os
from datetime import datetime
from urllib.parse import urlparse

SEARCH_RESULTS = "/Users/alex/.openclaw/workspace/ai-daily-news/search_results.json"
OUTPUT_FILE = "/Users/alex/.openclaw/workspace/ai-daily-news/feed.xml"

def extract_domain(url):
    try:
        return urlparse(url).netloc.replace('www.', '')
    except:
        return ''

def load_search_results():
    if os.path.exists(SEARCH_RESULTS):
        with open(SEARCH_RESULTS, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def generate_rss():
    data = load_search_results()
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 收集所有文章
    all_items = []
    categories = {
        'news': '📰 新闻',
        'tech': '💻 技术', 
        'tutorial': '📚 教程',
        'fun': '🎉 趣闻',
        'products': '🚀 AI产品',
        'funding': '💰 融资',
        'people': '👤 人物',
        'opinions': '💡 观点'
    }
    
    for cat_key, cat_name in categories.items():
        if cat_key in data and isinstance(data[cat_key], list):
            for item in data[cat_key]:
                item['category'] = cat_name
                all_items.append(item)
    
    # 按时间排序（最新的在前）
    all_items.sort(key=lambda x: x.get('time', ''), reverse=True)
    
    # 生成 RSS
    rss = '''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
    <title>AI 日报</title>
    <link>https://wallerwvw-cell.github.io/ai-daily-news/</link>
    <description>每日AI新闻、技术文章、产品融资、人物观点 - 您的AI资讯助手</description>
    <language>zh-cn</language>
    <lastBuildDate>''' + datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000") + '''</lastBuildDate>
    <atom:link href="https://wallerwvw-cell.github.io/ai-daily-news/feed.xml" rel="self" type="application/rss+xml"/>
'''
    
    for item in all_items[:50]:  # 最多50条
        title = item.get('title', '').replace('<', '&lt;').replace('>', '&gt;')
        url = item.get('url', '#')
        summary = item.get('summary', '') or item.get('snippet', '')
        if len(summary) > 300:
            summary = summary[:300] + '...'
        summary = summary.replace('<', '&lt;').replace('>', '&gt;')
        source = item.get('source', '') or extract_domain(url)
        category = item.get('category', '📰 新闻')
        
        rss += f'''    <item>
        <title><![CDATA[{title}]]></title>
        <link>{url}</link>
        <description><![CDATA[{summary}]]></description>
        <source>{source}</source>
        <category>{category}</category>
        <guid isPermaLink="true">{url}</guid>
    </item>
'''
    
    rss += '''</channel>
</rss>'''
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(rss)
    
    print(f"✅ RSS Feed 已生成: {OUTPUT_FILE}")
    print(f"📡 共 {len(all_items)} 条资讯")

if __name__ == "__main__":
    generate_rss()
