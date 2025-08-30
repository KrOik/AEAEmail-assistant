from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import os
import re
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 从环境变量获取API密钥
API_KEY = os.getenv('QWEN_API_KEY', 'sk-cd7cae6e397e484493538cafe9ad91f9')
API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# 知识库内容
avoid_thunder_content = """
**1. 主题栏（Subject Line）：精准概括，一眼知意**

主题是邮件的"门面"，需让收件人在未打开邮件时，即可判断邮件核心目的与紧急程度，格式建议为"【场景 / 身份】+ 核心事项 +（可选：时间 / 紧急标识）"。

- 错误示例："咨询问题""请假"（模糊不清，收件人无法快速判断内容）；
- 正确示例："【本科生 - 2023 级】关于 MAT101课程缓考申请的咨询""【研究生】 Thesis 开题答辩时间调整申请（3 月 10日前回复）"。

**2. 称呼（Salutation）：依身份定礼仪，不缺位不越界**

称呼需匹配收件人身份（教师 / 行政人员 /同学），体现尊重且符合西浦沟通习惯：

- 对教师：统一使用 "Dear Prof. [姓氏]"（教授）或 "Dear Dr.[姓氏]"（博士 /讲师，若不确定职称，可通过西浦官网教师名录查询，避免直接用 "老师"）；
- 对行政人员（如教务处、学院办公室）：使用 "Dear [部门名称] Team"（如"Dear Undergraduate Office Team"）或 "Dear Ms./Mr.[姓氏]"（已知姓名时）；
- 对同学 / 同辈：可简化为 "Hi [名字]"（如 "Hi LiMing"），无需过度正式。

**3. 开场白（Opening Paragraph）：简洁寒暄 + 目的前置**

开篇无需冗长铺垫，先简要问候，再**直接说明邮件目的**，避免让收件人"找重点"。

- 基础模板："Dear Prof. Zhang, Hope you are well. I am [你的姓名]，a[你的身份，如 2022 级 BSc Accounting student] from your [课程 /项目，如 FA201 class]. I am writing to inquire about [核心目的，如the extension of the assignment deadline for FA201]."
- 注意：若为首次沟通，需补充关键身份信息（年级、专业、课程 /导师）；若为后续沟通，可加 "Following up on our conversation last weekabout..." 衔接前文。

**4. 正文（Body Paragraphs）：分点阐述，论据清晰**

正文是邮件核心，需围绕 "目的"展开，用简洁的逻辑传递信息，避免大段文字堆积：

- 若为 "咨询问题"：先说明背景（如 "我在完成 FA201 第 3次作业时，对'合并报表抵消分录'的计算逻辑存在疑问"），再明确提问（如"想请教您：子公司内部交易未实现利润，是否需要在合并报表中全额抵消？"）；
- 若为 "申请事项"（如缓考、请假、修改开题时间）：需说明"申请原因"（客观、简洁，避免情绪化描述）+"具体需求"（如 "申请将 MAT101缓考时间调整至 5 月 20 日"）+"后续配合措施"（如"承诺在缓考前完成所有复习任务，并同步向助教提交进度"）；
- 技巧：复杂信息可分 1-2 个段落，每段聚焦 1个核心点，避免跨段落混谈多个事项。

**5. 结尾（Closing Paragraph）：礼貌收尾 + 明确期待**

结尾需表达感谢，并清晰告知"希望对方如何回应"（如回复时间、回复方式），避免模糊表述。

- 基础模板："Thank you for your time and consideration. Could you pleasereply to this email by [日期，如 March 8th] to confirm whether theadjustment is feasible? Should you need any further information,please feel free to contact me. "
- 常用礼貌结语："Best regards,""Sincerely,"（正式场合，对教师 /行政人员）；"Kind regards,"（同辈 / 熟悉的沟通对象），落款为"你的姓名 + 你的身份"（如 "Wang Hua, 2023 级 BSc Computer Science"）。

**6. 附件（Attachments）：标注清晰，主动提醒**

若邮件含附件（如申请表格、作业、证明材料），需在正文结尾明确提及附件名称与用途，避免收件人遗漏。

- 示例："I have attached the 'Application Form for Exam Deferral'(signed by my supervisor) and the medical certificate for yourreference. "
- 注意：附件命名需规范，格式为 "【姓名 - 身份】+ 文件用途 + 日期"（如"【Wang Hua-2023 级 CS】Exam Deferral ApplicationForm_20240305"），方便收件人归档查找。
"""

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


def call_qwen_api(prompt, system_message="你是一个专业的学术邮件撰写助手，擅长根据用户需求生成得体、专业的邮件内容。"):
    """
    调用Qwen API的函数
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "qwen-max",
        "messages": [
            {
                "role": "system",
                "content": system_message
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 2000,
        "temperature": 0.7
    }

    try:
        response = requests.post(f"{API_URL}/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()

        # 提取生成的文本
        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0]['message']['content']
            return content
        else:
            return "抱歉，无法生成内容。API返回格式异常，请检查API配置。"

    except requests.exceptions.RequestException as e:
        return f"API调用失败: {str(e)}"


def construct_email_prompt(user_request, recipient_info=""):
    """
    根据用户请求构建邮件生成提示词
    """
    prompt = f"""
    你是一个专业的学术邮件撰写助手，请根据用户需求生成得体、专业的邮件内容。

    #知识库参考
    请参考以下邮件撰写指南：
    {avoid_thunder_content}

    请参考以下教师称谓列表：
    {email_list_content}

    #用户请求
    {user_request}

    #收件人信息
    {recipient_info if recipient_info else "用户未提供特定收件人信息，请根据上下文推断合适的称呼。"}

    #任务
    请根据用户请求，生成一封完整的学术邮件。

    #要求
    1. 邮件应包含所有必要部分：主题、称呼、正文、结尾敬语、落款
    2. 根据收件人身份使用恰当的称呼和语气
    3. 邮件内容应清晰、专业、得体
    4. 如果用户请求中提到了特定事项（如作业延期、会议请求等），请确保邮件中完整涵盖这些内容
    5. 提供中文和英文两个版本的邮件

    #输出格式
    请按照以下格式返回结果：

    【邮件主题】
    中文主题： [这里写中文主题]
    英文主题： [这里写英文主题]

    【收件人称呼】
    中文称呼： [这里写中文称呼]
    英文称呼： [这里写英文称呼]

    【邮件正文 - 中文】
    [这里写中文邮件正文]

    【邮件正文 - 英文】
    [这里写英文邮件正文]

    【结尾敬语】
    中文结尾： [这里写中文结尾敬语]
    英文结尾： [这里写英文结尾敬语]

    【落款信息】
    中文落款： [这里写中文落款]
    英文落款： [这里写英文落款]

    【撰写建议】
    [这里写邮件撰写建议和注意事项]
    """

    return prompt


def construct_knowledge_prompt(question):
    """
    构建知识库查询提示词
    """
    prompt = f"""
    你是一个学术邮件知识库助手，请根据提供的知识库内容回答用户问题。

    #知识库内容
    1. 邮件撰写指南（避雷.docx）:
    {avoid_thunder_content}

    2. 教师称谓列表（邮件.docx）:
    {email_list_content}

    #用户问题
    {question}

    #要求
    1. 只基于提供的知识库内容回答问题，不要编造不存在的信息
    2. 如果知识库中没有相关信息，请如实告知用户
    3. 回答要准确、简洁、专业

    #输出格式
    请直接回答问题，不需要特殊格式。
    """

    return prompt


def search_knowledge_directly(question):
    """
    直接搜索知识库内容，不调用API
    """
    # 检查是否是教师称谓查询
    teacher_match = re.search(r'(\w+\.\w+|\w+)\s*的?\s*称谓', question)
    if teacher_match:
        teacher_name = teacher_match.group(1).strip()
        # 清理教师姓名，移除可能的"的"字
        if teacher_name.endswith('的'):
            teacher_name = teacher_name[:-1]
        
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
            result += "- 申请事项：说明原因+具体需求+后续措施\n"

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

    # 如果没有匹配到特定模式，返回None让API处理
    return None


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


def parse_email_response(response_text):
    """
    解析邮件生成API的响应文本，转换为结构化数据
    """
    sections = {
        "chinese_subject": "",
        "english_subject": "",
        "chinese_salutation": "",
        "english_salutation": "",
        "chinese_body": "",
        "english_body": "",
        "chinese_closing": "",
        "english_closing": "",
        "chinese_signature": "",
        "english_signature": "",
        "tips": ""
    }

    current_section = None

    for line in response_text.split('\n'):
        line = line.strip()

        if not line:
            continue

        # 检测章节标题
        if line.startswith('【') and line.endswith('】'):
            section_name = line[1:-1]
            if "主题" in section_name:
                current_section = "subject"
            elif "称呼" in section_name:
                current_section = "salutation"
            elif "正文" in section_name:
                current_section = "body"
            elif "结尾" in section_name:
                current_section = "closing"
            elif "落款" in section_name:
                current_section = "signature"
            elif "建议" in section_name:
                current_section = "tips"
            continue

        # 根据当前章节处理内容
        if current_section == "subject":
            if "中文主题" in line:
                sections["chinese_subject"] = line.split("：", 1)[1].strip()
            elif "英文主题" in line:
                sections["english_subject"] = line.split("：", 1)[1].strip()

        elif current_section == "salutation":
            if "中文称呼" in line:
                sections["chinese_salutation"] = line.split("：", 1)[1].strip()
            elif "英文称呼" in line:
                sections["english_salutation"] = line.split("：", 1)[1].strip()

        elif current_section == "body":
            if "中文" in line and "：" in line:
                sections["chinese_body"] += line.split("：", 1)[1].strip() + "\n"
            elif "英文" in line and "：" in line:
                sections["english_body"] += line.split("：", 1)[1].strip() + "\n"
            else:
                # 如果没有明确标注，根据上下文判断
                if sections["chinese_body"] and not sections["english_body"]:
                    sections["chinese_body"] += line + "\n"
                else:
                    sections["english_body"] += line + "\n"

        elif current_section == "closing":
            if "中文结尾" in line:
                sections["chinese_closing"] = line.split("：", 1)[1].strip()
            elif "英文结尾" in line:
                sections["english_closing"] = line.split("：", 1)[1].strip()

        elif current_section == "signature":
            if "中文落款" in line:
                sections["chinese_signature"] = line.split("：", 1)[1].strip()
            elif "英文落款" in line:
                sections["english_signature"] = line.split("：", 1)[1].strip()

        elif current_section == "tips":
            sections["tips"] += line + "\n"

    # 构建完整的邮件内容
    chinese_email = f"{sections['chinese_salutation']}\n\n{sections['chinese_body']}\n{sections['chinese_closing']}\n{sections['chinese_signature']}"
    english_email = f"{sections['english_salutation']}\n\n{sections['english_body']}\n{sections['english_closing']}\n{sections['english_signature']}"

    return {
        "chinese_subject": sections["chinese_subject"],
        "english_subject": sections["english_subject"],
        "chinese_email": chinese_email,
        "english_email": english_email,
        "tips": sections["tips"]
    }


@app.route('/api/generate-email', methods=['POST'])
def generate_email():
    """
    生成邮件内容的API端点（旧版，保留兼容性）
    """
    data = request.get_json()

    if not data or 'scenario' not in data or 'question' not in data:
        return jsonify({"error": "缺少必要参数: scenario 或 question"}), 400

    scenario = data['scenario']
    question = data['question']

    # 构建提示词
    prompt = f"""
    请根据以下场景和问题，生成专业的邮件内容：
    - 场景：{scenario}
    - 问题：{question}

    #知识库参考
    {avoid_thunder_content}

    {email_list_content}

    请生成中文和英文两个版本的邮件，并提供撰写建议。
    """

    # 调用Qwen API
    result = call_qwen_api(prompt)

    # 尝试解析响应
    try:
        parsed_result = json.loads(result)
        return jsonify(parsed_result)
    except json.JSONDecodeError:
        # 如果API返回的不是JSON，返回原始文本
        return jsonify({
            "chinese": result,
            "english": "Failed to generate English version",
            "tips": "API返回格式异常，请检查提示词设置"
        })


@app.route('/api/generate-email-from-chat', methods=['POST'])
def generate_email_from_chat():
    """
    从聊天内容生成邮件的API端点（新版）
    """
    data = request.get_json()

    if not data or 'message' not in data:
        return jsonify({"error": "缺少必要参数: message"}), 400

    user_message = data['message']
    recipient = data.get('recipient', '')

    # 构建提示词
    prompt = construct_email_prompt(user_message, recipient)

    # 调用Qwen API
    result = call_qwen_api(prompt)

    # 解析响应
    parsed_result = parse_email_response(result)

    return jsonify(parsed_result)


@app.route('/api/query-knowledge', methods=['POST'])
def query_knowledge():
    """
    知识库查询API端点
    """
    data = request.get_json()

    if not data or 'question' not in data:
        return jsonify({"error": "缺少必要参数: question"}), 400

    question = data['question']

    # 首先尝试直接搜索知识库
    direct_result = search_knowledge_directly(question)
    if direct_result:
        # 如果找到直接答案，返回结果
        return jsonify(direct_result)

    # 如果没有直接匹配，返回提示信息而不是调用API
    return jsonify({
        "result": "抱歉，我在知识库中没有找到相关信息。",
        "details": "您可以尝试以下查询：\n1. 查询特定教师称谓，如：'haochuan.jiang的称谓是什么'\n2. 查询邮件写作指南，如：'邮件主题应该怎么写'\n3. 查询邮件格式，如：'邮件写作格式是什么'"
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    健康检查端点
    """
    return jsonify({"status": "healthy", "message": "AI学术邮件助手API运行正常"})


if __name__ == '__main__':
    app.run(debug=True, port=5000)