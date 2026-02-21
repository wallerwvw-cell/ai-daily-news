#!/usr/bin/env python3
"""
获取新闻详情并生成摘要
"""
import json
import os
import re

SEARCH_RESULTS = "/Users/alex/.openclaw/workspace/ai-daily-news/search_results.json"
OUTPUT_FILE = "/Users/alex/.openclaw/workspace/ai-daily-news/search_results.json"

def clean_text(text):
    """清理文本"""
    if not text:
        return ""
    # 移除 HTML 标签
    text = re.sub(r'<[^>]+>', '', text)
    # 移除多余空白
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def load_results():
    """加载搜索结果"""
    with open(SEARCH_RESULTS, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_results(results):
    """保存搜索结果"""
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

def main():
    print("📋 注意：摘要提取需要使用 web_fetch 工具在 AI 环境中运行")
    print("当前脚本只是展示数据结构...")
    
    results = load_results()
    
    # 显示数据结构
    categories = ['news', 'tech', 'tutorial', 'fun']
    for cat in categories:
        items = results.get(cat, [])
        print(f"\n{cat}: {len(items)} 条")
        for item in items[:2]:  # 只显示前2条
            print(f"  - {item.get('title', '')[:50]}...")
            print(f"    URL: {item.get('url', '')}")
            print(f"    现有摘要: {item.get('snippet', '')[:80]}...")

if __name__ == "__main__":
    main()
