#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库查询功能测试脚本
"""

# 模拟邮件文件中的教师称谓内容
email_list_content = """
haochuan.jiang 称谓：Dear Dr. Jiang
haoran.li 称谓：Dear Dr. Li
Wenjuan.Fan 称谓：Dear Dr. Fan
Tianhong.Gu 称谓： Dear Dr. Gu
Syed.Abbas 称谓：Dear Dr. Abbas
Dharma.Adhikari 称谓： Dear Dr. Adhikari
Yuanrui Huang 称谓：Dear Dr.Huang
Xun Lei 称谓：Dear Dr.Lei
Haoying An 称谓：Dear Dr.An
Yunfei Bo称谓：Dear Dr.Bo
Ren Zhao 称谓：Dear Dr.Zhao
Steven Bateman 称谓：Dear Dr.Bateman
Khalid Akhal Dear Dr.Akhal
Muhammad Ateeq Dear Dr. Ateeq
"""

def get_common_knowledge_answers():
    """
    返回常见问题的直接答案，避免调用API
    """
    return {
        "邮件写作": {
            "keywords": ["邮件", "写作", "格式", "模板"],
            "answer": """邮件写作基本格式：

1. 主题栏（Subject Line）
   - 格式：【场景/身份】+ 核心事项 +（可选：时间/紧急标识）
   - 示例：【本科生-2023级】关于MAT101课程缓考申请的咨询

2. 称呼（Salutation）
   - 对教师：Dear Prof. [姓氏] 或 Dear Dr. [姓氏]
   - 对行政人员：Dear [部门名称] Team 或 Dear Ms./Mr. [姓氏]
   - 对同学：Hi [名字]

3. 开场白（Opening Paragraph）
   - 简洁寒暄 + 目的前置
   - 示例：Dear Prof. Zhang, Hope you are well. I am [姓名]...

4. 正文（Body Paragraphs）
   - 分点阐述，论据清晰
   - 咨询问题：先说明背景再明确提问
   - 申请事项：说明原因+具体需求+后续措施

5. 结尾（Closing Paragraph）
   - 礼貌收尾 + 明确期待
   - 示例：Thank you for your time and consideration...

6. 附件（Attachments）
   - 标注清晰，主动提醒
   - 命名格式：【姓名-身份】+文件用途+日期"""
        },
        "教师称谓": {
            "keywords": ["称谓", "称呼", "老师", "教授", "博士"],
            "answer": f"""教师称谓规则：

{email_list_content}

称谓使用原则：
- 对教授：Dear Prof. [姓氏]
- 对博士/讲师：Dear Dr. [姓氏]
- 对行政人员：Dear [部门名称] Team 或 Dear Ms./Mr. [姓氏]
- 对同学：Hi [名字]"""
        },
        "邮件主题": {
            "keywords": ["主题", "subject", "标题"],
            "answer": """邮件主题栏写作要点：

1. 格式：【场景/身份】+ 核心事项 +（可选：时间/紧急标识）

2. 正确示例：
   - 【本科生-2023级】关于MAT101课程缓考申请的咨询
   - 【研究生】Thesis开题答辩时间调整申请（3月10日前回复）
   - 【本科生】FA201课程作业延期申请（特殊情况）

3. 错误示例：
   - "咨询问题"（模糊不清）
   - "请假"（信息不完整）
   - "Help"（过于简单）

4. 注意事项：
   - 让收件人一眼就能判断邮件目的
   - 包含关键信息：身份、事项、时间要求
   - 避免模糊或过于简单的表述"""
        }
    }


def search_knowledge_directly(question):
    """
    直接搜索知识库内容，不调用API
    """
    import re
    
    # 检查是否是教师称谓查询
    teacher_match = re.search(r'(\w+\.\w+|\w+)\s*(的)?\s*称谓', question)
    if teacher_match:
        teacher_name = teacher_match.group(1)
        print(f"正在查询教师 {teacher_name} 的称谓...")
        
        # 在教师列表中搜索，改进搜索逻辑
        for line in email_list_content.split('\n'):
            line = line.strip()
            if line and '称谓：' in line:
                # 提取教师姓名和称谓
                if teacher_name.lower() in line.lower():
                    return {
                        "result": line,
                        "details": f"找到教师 {teacher_name} 的称谓信息"
                    }
        
        # 如果没有找到，返回所有可用的教师称谓列表
        available_teachers = []
        for line in email_list_content.split('\n'):
            line = line.strip()
            if line and '称谓：' in line:
                available_teachers.append(line)
        
        return {
            "result": f"未找到教师 {teacher_name} 的称谓信息",
            "details": f"请检查教师姓名是否正确。\n\n可用的教师称谓列表：\n" + "\n".join(available_teachers)
        }

    # 检查常见问题
    common_knowledge = get_common_knowledge_answers()
    for category, info in common_knowledge.items():
        if any(keyword in question for keyword in info["keywords"]):
            return {
                "result": info["answer"],
                "details": f"这是关于{category}的详细信息"
            }

    # 检查是否是邮件写作指南查询
    guide_keywords = ["主题", "称呼", "开场", "正文", "结尾", "附件", "避雷"]
    if any(keyword in question for keyword in guide_keywords):
        # 提取相关问题
        result = "根据邮件撰写指南：\n"
        details = ""

        if "主题" in question:
            result += "- 主题栏应精准概括，格式为'【场景/身份】+核心事项+（可选：时间/紧急标识）'\n"
            details += "主题栏示例：'【本科生-2023级】关于MAT101课程缓考申请的咨询'\n"

        if "称呼" in question:
            result += "- 对教师使用'Dear Prof. [姓氏]'或'Dear Dr. [姓氏]'\n"
            result += "- 对行政人员使用'Dear [部门名称] Team'或'Dear Ms./Mr. [姓氏]'\n"
            result += "- 对同学使用'Hi [名字]'\n"

        if "开场" in question:
            result += "- 开场白应简洁寒暄+目的前置\n"
            details += "示例：'Dear Prof. Zhang, Hope you are well. I am [姓名]...'\n"

        if "正文" in question:
            result += "- 正文应分点阐述，论据清晰\n"
            details += "- 咨询问题：先说明背景再明确提问\n"
            details += "- 申请事项：说明原因+具体需求+后续措施\n"

        if "结尾" in question:
            result += "- 结尾应礼貌收尾+明确期待\n"
            details += "示例：'Thank you for your time and consideration...'\n"

        if "附件" in question:
            result += "- 附件应标注清晰，主动提醒\n"
            details += "命名格式：'【姓名-身份】+文件用途+日期'\n"

        return {
            "result": result,
            "details": details if details else "更多详细信息请参考完整的邮件撰写指南"
        }

    # 如果没有匹配到特定模式，返回None
    return None


def test_knowledge_queries():
    """
    测试各种知识库查询
    """
    test_questions = [
        "haochuan.jiang的称谓是什么",
        "邮件主题应该怎么写",
        "邮件写作格式是什么",
        "给老师的邮件称呼应该用什么",
        "邮件附件应该怎么处理",
        "不相关的问题"
    ]
    
    print("=== 知识库查询功能测试 ===\n")
    
    for question in test_questions:
        print(f"问题: {question}")
        result = search_knowledge_directly(question)
        
        if result:
            print(f"✅ 找到答案:")
            print(f"结果: {result['result']}")
            print(f"详情: {result['details']}")
        else:
            print("❌ 未找到答案")
        
        print("-" * 50)


if __name__ == "__main__":
    test_knowledge_queries()
