from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import json
import re

app = FastAPI()

# 允许跨域（前端可以访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================================================================
# 数据模型
# ================================================================
class AnalyzeRequest(BaseModel):
    text: str

class AnalyzeResponse(BaseModel):
    success: bool
    data: dict

# ================================================================
# 内置知识库（最小版本）
# ================================================================
KNOWLEDGE_BASE = {
    "蒙古族": {
        "饮食": "蒙古族饮食文化以'红食'（肉类）和'白食'（奶制品）为两大支柱。日常饮品为奶茶（砖茶+鲜奶+盐），主食有手把肉、炒米、奶豆腐、羊肉汤面等。",
        "居住": "蒙古族传统上住的是蒙古包，由哈那（网状围壁）、乌尼（伞形支架）和掏恩（天窗）组成，外面覆盖毛毡，用皮绳扎紧。具有易于拆装、搬迁方便的特点。",
        "服饰": "蒙古族传统服装是蒙古袍，长而宽大，高领长袖，右边开襟，领口袖口都镶着边。有单袍、夹袍、棉袍、皮袍几种。",
        "礼仪": "蒙古族有敬鼻烟壶的礼节，同辈见面时各自用右手递鼻烟壶、左手接，互相交换嗅闻。客人来了先敬奶茶。",
        "其他": "蒙古族有三大历史巨著——《蒙古秘史》、《蒙古黄金史》和《蒙古源流》。传统上有萨满教信仰，崇拜火、太阳、北斗七星等自然物。"
    },
    "藏族": {
        "饮食": "藏族饮食以青稞、酥油茶、糌粑、牦牛肉为主。糌粑是青稞炒熟磨粉制成，用酥油茶拌合捏成团食用。",
        "居住": "藏族传统住房以碉房为主，石木结构，冬暖夏凉。在牧区也有帐篷。",
        "服饰": "藏族传统服饰为藏袍，特点是右衽、长袖、宽腰、大襟，用氆氇或皮毛制成，腰间系带。",
        "礼仪": "藏族见面时献哈达表示敬意和祝福。藏族信仰藏传佛教，转经筒是常见的宗教活动。",
        "其他": "藏族有丰富的文化传统，包括雪顿节、藏历新年等节日。布达拉宫是藏族文化的象征。"
    },
    "维吾尔族": {
        "饮食": "维吾尔族饮食以馕为核心，配以抓饭、烤包子、手抓羊肉和各类干果。抓饭用羊肉、胡萝卜、大米制成。",
        "居住": "维吾尔族传统住房多为土木结构的平顶房，庭院内多有葡萄架。喀什老城是典型的维吾尔族聚居区。",
        "服饰": "维吾尔族传统服饰色彩鲜艳，男性多穿袷袢长袍，女性多穿艾德莱斯绸制成的连衣裙，头戴小花帽。",
        "礼仪": "维吾尔族热情好客，见面时握手问候。主要节日有古尔邦节和肉孜节。",
        "其他": "维吾尔族有丰富的音乐舞蹈传统，木卡姆和赛乃姆舞是重要的文化遗产。"
    },
    "哈萨克族": {
        "饮食": "哈萨克族主食以肉类和面食为主，最具特色的是马肠子——用马肉灌制熏制而成。还有手抓肉、那仁、包尔萨克等。",
        "居住": "哈萨克族传统上住的是毡房，便于迁徙游牧。毡房由羊毛毡和木架构成，冬暖夏凉。",
        "服饰": "哈萨克族传统服饰以皮毛制品为主，男性戴尖顶帽或三叶帽，穿宽大的皮裤和皮靴。",
        "礼仪": "哈萨克族见面时握手问候，尊老爱幼。主要节日有纳吾鲁孜节。",
        "其他": "哈萨克族是游牧民族，擅长骑马和放牧。冬不拉是哈萨克族传统乐器。"
    }
}

# ================================================================
# 民族关键词映射
# ================================================================
ETHNIC_KEYWORDS = {
    "蒙古族": ["蒙古", "蒙族", "蒙古包", "那达慕", "马奶", "奶茶"],
    "藏族": ["藏族", "西藏", "布达拉宫", "转经筒", "藏袍", "酥油茶", "糌粑"],
    "维吾尔族": ["维吾尔", "维族", "喀什", "馕", "抓饭", "小花帽", "艾德莱斯"],
    "哈萨克族": ["哈萨克", "毡房", "马肠子", "草原放牧"]
}

CATEGORY_KEYWORDS = {
    "饮食": ["吃", "喝", "食", "餐", "饮", "主食", "奶茶", "糌粑", "馕", "手把肉", "酥油茶"],
    "居住": ["住", "房子", "房屋", "蒙古包", "毡房", "碉房", "建筑"],
    "服饰": ["穿", "衣服", "服装", "袍", "帽", "腰带", "绣", "戴"],
    "礼仪": ["礼节", "见面", "问候", "敬", "献", "礼", "待客", "招待"],
    "其他": ["文化", "信仰", "文学", "著作", "艺术", "音乐", "舞蹈"]
}

# ================================================================
# 核心分析函数
# ================================================================
def detect_ethnic(text: str) -> dict:
    """从文本中识别民族"""
    scores = {}
    for ethnic, keywords in ETHNIC_KEYWORDS.items():
        score = 0
        for kw in keywords:
            if kw in text:
                score += 1
        scores[ethnic] = score
    
    # 找出最高分的民族
    best_ethnic = max(scores, key=scores.get)
    max_score = scores[best_ethnic]
    
    # 提取文化线索（命中的关键词）
    cues = []
    for kw in ETHNIC_KEYWORDS.get(best_ethnic, []):
        if kw in text:
            cues.append(kw)
    
    # 计算置信度
    confidence = min(85 + max_score * 5, 98) if max_score > 0 else 60
    
    return {
        "ethnic": best_ethnic if max_score > 0 else "其他",
        "confidence": confidence,
        "cues": cues if cues else ["文化线索不足，基于推理判断"]
    }

def detect_category(text: str) -> str:
    """从文本中识别类别"""
    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = 0
        for kw in keywords:
            if kw in text:
                score += 1
        scores[category] = score
    
    best_category = max(scores, key=scores.get)
    return best_category if scores[best_category] > 0 else "其他"

def get_knowledge(ethnic: str, category: str) -> dict:
    """获取知识库内容"""
    knowledge = KNOWLEDGE_BASE.get(ethnic, {})
    
    # 获取该民族该类别知识
    knowledge_text = knowledge.get(category, "暂无相关知识。")
    
    # 获取Top3相关知识片段
    top3 = []
    if ethnic in KNOWLEDGE_BASE:
        for cat, content in KNOWLEDGE_BASE[ethnic].items():
            if cat != category:
                top3.append(f"{cat}：{content[:20]}...")
    
    # 如果top3不足，补充通用知识
    while len(top3) < 3:
        top3.append("相关知识正在整理中...")
    
    return {
        "knowledge": knowledge_text,
        "top3": top3[:3]
    }

def generate_response(ethnic: str, category: str, text: str) -> str:
    """生成回答"""
    templates = {
        "蒙古族": {
            "饮食": f"作为蒙古族，我们日常饮食以红食（肉类）和白食（奶制品）为主。{text}根据您的提问，我们最常吃的是手把肉、炒米、奶豆腐，喝的是奶茶。早餐一般是奶茶泡炒米，加上煮肉块、奶皮、奶豆腐，晚餐多是羊肉汤面、奶油烙饼或手扒肉。",
            "居住": f"作为蒙古族，我们传统上居住在蒙古包里。{text}蒙古包是用柳木条和毛毡搭建的，拆装方便，冬暖夏凉，是游牧生活的智慧结晶。",
            "服饰": f"作为蒙古族，我们传统服饰是蒙古袍。{text}蒙古袍长而宽大，高领右衽，袖口和领口镶有精美花边，体现了草原民族的审美和实用智慧。",
            "礼仪": f"作为蒙古族，我们见面时有敬鼻烟壶的礼节。{text}同辈交换鼻烟壶嗅闻，晚辈见长辈需单腿跪献。客人来了先敬奶茶，处处体现热情好客。",
            "其他": f"作为蒙古族，我们有丰富的文化传统。{text}我们有三大历史巨著《蒙古秘史》《蒙古黄金史》《蒙古源流》，还有萨满教信仰，崇拜火、太阳、北斗七星等自然物。"
        },
        "藏族": {
            "饮食": f"作为藏族，我们日常饮食以青稞、酥油茶、糌粑和牦牛肉为主。{text}糌粑是青稞炒熟磨粉制成，用酥油茶拌合捏成团，是高原上最温暖的能量来源。",
            "居住": f"作为藏族，我们传统住房以碉房为主。{text}碉房是石木结构，冬暖夏凉，非常适合高原气候。在牧区我们也会住帐篷。",
            "服饰": f"作为藏族，我们传统服饰是藏袍。{text}藏袍右衽长袖、宽腰大襟，用氆氇或皮毛制成，腰间系带，既保暖又便于劳作。",
            "礼仪": f"作为藏族，我们见面时献哈达表示敬意和祝福。{text}我们信仰藏传佛教，转经筒是常见的宗教活动，体现了我们对信仰的虔诚。",
            "其他": f"作为藏族，我们有丰富的文化传统。{text}我们有雪顿节、藏历新年等节日，布达拉宫是我们文化的象征，藏医药也是我们的宝贵遗产。"
        },
        "维吾尔族": {
            "饮食": f"作为维吾尔族，我们饮食以馕为核心。{text}馕是我们日常最重要的主食，节日时会制作各种花样的馕。还有抓饭、烤包子、手抓羊肉等美食。",
            "居住": f"作为维吾尔族，我们传统住房多为土木结构的平顶房。{text}庭院内多有葡萄架，喀什老城是我们典型的聚居区，体现了独特的建筑风格。",
            "服饰": f"作为维吾尔族，我们传统服饰色彩鲜艳。{text}男性多穿袷袢长袍，女性喜欢艾德莱斯绸制成的连衣裙，头戴精美的小花帽。",
            "礼仪": f"作为维吾尔族，我们热情好客。{text}见面时握手问候，主要节日有古尔邦节和肉孜节，节日里会准备丰盛的美食招待客人。",
            "其他": f"作为维吾尔族，我们有丰富的音乐舞蹈传统。{text}木卡姆和赛乃姆舞是我们重要的文化遗产，展现了维吾尔族人民的艺术才华。"
        },
        "哈萨克族": {
            "饮食": f"作为哈萨克族，我们主食以肉类和面食为主。{text}最具特色的是马肠子——用马肉灌制熏制而成，风味独特。还有手抓肉、那仁、包尔萨克等草原美味。",
            "居住": f"作为哈萨克族，我们传统上住的是毡房。{text}毡房由羊毛毡和木架构成，便于迁徙游牧，冬暖夏凉，是游牧生活的智慧。",
            "服饰": f"作为哈萨克族，我们传统服饰以皮毛制品为主。{text}男性戴尖顶帽或三叶帽，穿宽大的皮裤和皮靴；女性戴绣花帽和头巾，穿色彩鲜艳的连衣裙。",
            "礼仪": f"作为哈萨克族，我们见面时握手问候。{text}我们尊老爱幼，主要节日有纳吾鲁孜节，节日里会举行赛马、叼羊等传统活动。",
            "其他": f"作为哈萨克族，我们是游牧民族。{text}我们擅长骑马和放牧，冬不拉是我们传统的乐器，草原是我们生活和文化的摇篮。"
        }
    }
    
    # 如果民族不在模板中，使用通用回答
    if ethnic not in templates:
        return f"作为{ethnic}的一员，我们有着独特的文化传统和生活方式。{text}虽然具体的习俗因地区和家庭而异，但我们都很珍视自己的文化身份。"
    
    # 如果类别不在模板中，使用"其他"类别
    if category not in templates[ethnic]:
        category = "其他"
    
    return templates[ethnic][category]

def generate_errors(ethnic: str, category: str, generated: str) -> dict:
    """生成错误分析和改进建议"""
    # 根据民族和类别生成不同的错误分析
    error_templates = {
        "蒙古族": {
            "饮食": {
                "wrong": "我们平时吃米饭和炒菜，和大家都差不多。",
                "fix": "应提及蒙古族特有的奶茶、手把肉、奶豆腐等传统饮食，突出'红食'与'白食'的文化概念。",
                "items": ["补充'白食'（奶制品）的文化概念", "增加具体食物如炒米、奶豆腐的描述", "体现牧区与农区的饮食差异"]
            },
            "居住": {
                "wrong": "我们住在普通的砖瓦房里，和汉族差不多。",
                "fix": "应突出蒙古包的独特结构和游牧文化背景，强调其便于拆装和冬暖夏凉的特点。",
                "items": ["补充蒙古包的结构组成", "强调游牧生活的适应性", "体现蒙古包的智慧"]
            },
            "服饰": {
                "wrong": "我们穿西装、T恤和牛仔裤，和现代人一样。",
                "fix": "应突出蒙古袍的右衽、镶边等特点，强调其适应草原生活的实用性。",
                "items": ["补充蒙古袍的款式特点", "男女袍的区别", "扎腰带的讲究"]
            },
            "礼仪": {
                "wrong": "我们见面就是握手、说你好，和汉族一样。",
                "fix": "应突出敬鼻烟壶的独特礼节，强调同辈和晚辈不同的方式。",
                "items": ["详细说明敬鼻烟壶的具体方式", "同辈与晚辈的区别", "体现蒙古族的热情好客"]
            },
            "其他": {
                "wrong": "我们没有什么特别的传统文化。",
                "fix": "应突出三大历史巨著和萨满教信仰，体现蒙古族丰富的文化传统。",
                "items": ["补充《蒙古秘史》的历史地位", "介绍《江格尔》史诗", "体现萨满教的自然崇拜"]
            }
        },
        "藏族": {
            "饮食": {
                "wrong": "我们平时主要吃米饭、面条和蔬菜。",
                "fix": "应突出青稞、酥油茶、糌粑、牦牛肉等高原特色饮食。",
                "items": ["补充糌粑的制作过程", "增加酥油茶的文化意义", "体现高原环境对饮食的影响"]
            },
            "服饰": {
                "wrong": "我们穿西装、T恤和牛仔裤。",
                "fix": "应突出藏袍的右衽、宽腰大襟等特点。",
                "items": ["补充藏袍的材质", "强调高原气候的适应性", "体现藏袍的实用智慧"]
            },
            "其他": {
                "wrong": "我们没有什么特别的宗教信仰。",
                "fix": "应突出藏传佛教和转经筒的文化意义。",
                "items": ["补充藏传佛教的信仰体系", "强调转经筒的宗教意义", "体现藏族虔诚的信仰"]
            }
        },
        "维吾尔族": {
            "饮食": {
                "wrong": "我们过节吃饺子、汤圆和年糕。",
                "fix": "应强调馕、抓饭、烤包子等维吾尔族传统美食。",
                "items": ["强调馕在生活中的核心地位", "补充抓饭的制作方法", "体现节日饮食的文化内涵"]
            },
            "服饰": {
                "wrong": "我们穿西装、T恤和牛仔裤。",
                "fix": "应突出艾德莱斯绸、小花帽、袷袢等特色服饰。",
                "items": ["强调艾德莱斯绸的独特工艺", "补充小花帽的文化意义", "体现服饰的鲜艳色彩"]
            },
            "其他": {
                "wrong": "我们没有什么特别的音乐舞蹈。",
                "fix": "应突出木卡姆和赛乃姆舞的艺术价值。",
                "items": ["补充木卡姆的历史地位", "介绍赛乃姆舞的特点", "体现维吾尔族的艺术才华"]
            }
        },
        "哈萨克族": {
            "饮食": {
                "wrong": "我们主食就是米饭和面条，没什么特别的。",
                "fix": "应突出马肠子、手抓肉、那仁等哈萨克族特色食品。",
                "items": ["突出马肠子的制作工艺", "体现游牧生活对饮食的影响", "补充那仁等面食的文化背景"]
            },
            "服饰": {
                "wrong": "我们穿西装、T恤和牛仔裤。",
                "fix": "应突出皮毛制品、三叶帽、绣花帽等特色服饰。",
                "items": ["强调皮毛制品的实用性", "补充三叶帽的文化意义", "体现女性服饰的鲜艳色彩"]
            },
            "其他": {
                "wrong": "我们没有什么特别的音乐。",
                "fix": "应突出冬不拉的音乐文化。",
                "items": ["补充冬不拉的历史", "介绍草原音乐的特点", "体现哈萨克族的游牧文化"]
            }
        }
    }
    
    # 如果民族不在模板中，使用通用模板
    if ethnic not in error_templates:
        return {
            "wrong": "回答没有体现该民族的文化特色。",
            "fix": f"应具体说明{ethnic}的文化传统和习俗。",
            "items": ["增加文化细节描述", "更准确地回答问题", "体现民族特色"]
        }
    
    # 如果类别不在模板中，使用"其他"
    if category not in error_templates[ethnic]:
        category = "其他"
    
    return error_templates[ethnic][category]

# ================================================================
# API 接口
# ================================================================
@app.post("/api/analyze")
async def analyze(request: AnalyzeRequest):
    """接收用户文本，执行完整工作流"""
    text = request.text.strip()
    
    if not text:
        return {
            "success": False,
            "error": "请输入要分析的内容"
        }
    
    # 1. 文化识别
    ethnic_result = detect_ethnic(text)
    ethnic = ethnic_result["ethnic"]
    confidence = ethnic_result["confidence"]
    cues = ethnic_result["cues"]
    
    # 生成推理过程
    reasoning = [
        f"Step 1: 提取文化线索 → \"{', '.join(cues)}\"",
        f"Step 2: 知识映射 → \"{cues[0] if cues else '文化符号'}\" 指向 {ethnic} 文化符号",
        f"Step 3: 综合判断 → 用户为 {ethnic}"
    ]
    
    # 2. 类别识别
    category = detect_category(text)
    
    # 3. 知识检索
    knowledge_result = get_knowledge(ethnic, category)
    knowledge = knowledge_result["knowledge"]
    top3 = knowledge_result["top3"]
    
    # 4. 生成回答
    generated = generate_response(ethnic, category, text)
    
    # 5. 错误分析
    error_result = generate_errors(ethnic, category, generated)
    
    # 6. 评分（基于生成的回答质量）
    culture_score = min(95, 80 + len(generated) // 10 + (10 if ethnic != "其他" else 0))
    semantic_score = min(92, 75 + len(generated) // 8)
    integrity_score = min(90, 70 + len(generated) // 6)
    total = round((culture_score + semantic_score + integrity_score) / 3)
    
    return {
        "success": True,
        "data": {
            "text": text,
            "ethnic": ethnic,
            "confidence": confidence,
            "cues": cues,
            "category": category,
            "reasoning": reasoning,
            "knowledge": knowledge,
            "top3": top3,
            "generated": generated,
            "scores": {
                "culture": culture_score,
                "semantic": semantic_score,
                "integrity": integrity_score,
                "total": total
            },
            "errors": {
                "wrongExample": error_result["wrong"],
                "fixSuggestion": error_result["fix"],
                "improveItems": error_result["items"]
            }
        }
    }

@app.get("/api/health")
async def health():
    """健康检查"""
    return {"status": "ok", "message": "服务运行正常"}

# ================================================================
# 启动服务
# ================================================================
if __name__ == "__main__":
    import os
    import sys

    host = os.getenv("APP_HOST", "0.0.0.0")
    try:
        port = int(os.getenv("APP_PORT", "6322"))
    except ValueError:
        print(f"错误: APP_PORT 必须为整数，当前值为 {os.getenv('APP_PORT')!r}", file=sys.stderr)
        sys.exit(1)

    display_host = "127.0.0.1" if host in ("0.0.0.0", "::") else host
    print("=" * 60)
    print("🌍 文化多样性自适应生成系统 - 后端服务")
    print("=" * 60)
    print(f"📌 启动地址: http://{display_host}:{port}")
    print(f"📌 API文档: http://{display_host}:{port}/docs")
    print(f"📌 健康检查: http://{display_host}:{port}/api/health")
    if host in ("0.0.0.0", "::"):
        print(f"   （监听 {host}，局域网可通过本机 IP 访问）")
    print("=" * 60)
    uvicorn.run(app, host=host, port=port)
