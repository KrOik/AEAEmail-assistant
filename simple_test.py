#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的教师称谓查询测试
"""

import re

# 模拟邮件文件中的教师称谓内容
email_list_content = """
haochuan.jiang 称谓：Dear Dr. Jiang
haoran.li 称谓：Dear Dr. Li
Wenjuan.Fan 称谓：Dear Dr. Fan
"""

def test_teacher_search():
    question = "haochuan.jiang的称谓是什么"
    
    # 检查是否是教师称谓查询
    teacher_match = re.search(r'(\w+\.\w+|\w+)\s*的?\s*称谓', question)
    if teacher_match:
        teacher_name = teacher_match.group(1).strip()
        # 清理教师姓名，移除可能的"的"字
        if teacher_name.endswith('的'):
            teacher_name = teacher_name[:-1]
        
        print(f"正则匹配结果: {teacher_match.group(1)}")
        print(f"清理后的教师姓名: '{teacher_name}'")
        
        # 在教师列表中搜索
        for line in email_list_content.split('\n'):
            line = line.strip()
            if line and '称谓：' in line:
                print(f"检查行: '{line}'")
                if teacher_name.lower() in line.lower():
                    print(f"✅ 找到匹配: {line}")
                    return
        
        print("❌ 未找到匹配")
    else:
        print("❌ 正则表达式未匹配")

if __name__ == "__main__":
    test_teacher_search()
