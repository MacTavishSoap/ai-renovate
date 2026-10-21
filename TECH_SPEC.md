# AI 家装产品 · 技术方案

> **版本**：v8.0 · **日期**：2026-10-21
> **状态**：工程进行中。核心交互模式已更新（多点全景图 + 场景图 + 两条路径），生图模型能力评估待实测验证
>
> **本版核心变更**：
> - 引入**多点全景图**模式：户型图 → 预设 N 个 Viewpoint → 每个 Viewpoint 一张全景图 → 全景图上可点击生成场景图
> - 两条路径合并：路径一（户型图驱动）和路径二（纯效果图），共用同一数据结构
> - 户型图解析**依赖生图模型能力**，减少预处理：OpenCV 做必要清洗，结构理解交给模型
> - 视角点**预置隔离**：每个全景图对应一个物理位置，天然避免跨房间穿帮
> - 全景图**固定机位，不可漫游**：用户通过点击全景图上的预设位置查看各角度场景图

---

## 一·一、核心交互模式

### 两条路径

| 路径 | 输入 | 流程 | 典型用户 |
|---|---|---|---|
| **路径一：户型图驱动** | 户型图（CAD/照片/扫描件） | 解析 → 预设 Viewpoint → 生成全景图 → 点击生成场景图 | 有原始户型图，想看整体规划 |
| **路径二：纯效果图** | 直接生成效果图 | 连续生成，reference 保证一致性 | 没有户型图，只要效果图 |

### 路径一：多点全景图模式

```
户型图
  │
  ├──→ 解析 RoomState
  │
  ├──→ 预设 N 个 Viewpoint（系统预置，可扩展）
  │       │
  │       ├── Viewpoint A（客厅门口）→ Panorama A（360°）
  │       │       ├── ClickableSpot A1 → SceneImage A1（看向沙发）
  │       │       └── ClickableSpot A2 → SceneImage A2（看向窗户）
  │       │
  │       ├── Viewpoint B（主卧床头）→ Panorama B
  │       │       └── ClickableSpot B1 → SceneImage B1
  │       │
  │       └── Viewpoint C（次卧）→ Panorama C
  │
  └──→ 用户在全景图上点击 → 弹出该角度场景图（新窗口）
```

**"小作弊"核心**：每个全景图对应一个物理位置，天然隔离空间范围。客厅全景图的场景图不会"穿帮"到隔壁餐厅。

### 全景图交互

- 全景图 = **固定图片，不可漫游**
- 全景图上预设 N 个可点击位置
- 点击 → 弹出该角度的场景图（新窗口/弹窗）

### 两条路径数据一致性

| 层级 | 一致性来源 |
|---|---|
| 全景图之间 | 共享 RoomState + 统一 StyleConfig |
| 全景图 → 场景图 | 场景图生成时传入全景图作为 reference |
| 场景图之间（同全景图） | 都以同一全景图为锚点 |
| 跨项目 | 每个 Project 独立 RoomState + StyleConfig |

---

## 一·二、数据结构设计（统一）

### ER 图

```
User
  └── Project
          ├── input_type: 'floor_plan' | 'effect_only'
          ├── style_prompt / negative_prompt / style_reference
          │
          ├── [路径一] RoomState
          │       ├── walls_json
          │       ├── rooms_json
          │       └── openings_json
          │
          └── Viewpoint ①
                  ├── position / direction / label / is_preset
                  └── Panorama ①
                          ├── ClickableSpot ①a → SceneImage ①a
                          ├── ClickableSpot ①b → SceneImage ①b
                          └── ...
```

### 数据库表设计

```sql
-- 1. 项目（顶层实体）
CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    input_type TEXT NOT NULL,              -- 'floor_plan' | 'effect_only'
    style_prompt TEXT,                     -- 风格 prompt
    negative_prompt TEXT,
    style_reference_url TEXT,               -- 风格参考图
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 2. 房间结构（路径一有，路径二无）
CREATE TABLE room_states (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,
    floor_plan_url TEXT,
    walls_json TEXT,                        -- [{x1,y1,x2,y2}, ...]
    rooms_json TEXT,                         -- [{name, polygon, type}, ...]
    openings_json TEXT,                     -- [{type, position, size}, ...]
    -- 原始提取产物（可选）
    depth_map_url TEXT,
    line_map_url TEXT,
    camera_params TEXT,                     -- {fov, pitch, roll}
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- 3. 视角点（户型图上的位置）
CREATE TABLE viewpoints (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,
    label TEXT NOT NULL,                    -- "客厅门口"、"主卧床头"
    position_x REAL NOT NULL,                -- 户型图归一化坐标
    position_y REAL NOT NULL,
    direction REAL NOT NULL,                 -- 朝向角度（度数）
    is_preset BOOLEAN DEFAULT FALSE,         -- True=系统预置
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- 4. 全景图（每个 Viewpoint 一张）
CREATE TABLE panoramas (
    id INTEGER PRIMARY KEY,
    viewpoint_id INTEGER NOT NULL,
    image_url TEXT,
    width INTEGER,
    height INTEGER,
    status TEXT DEFAULT 'pending',          -- 'pending' | 'generating' | 'done' | 'failed'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (viewpoint_id) REFERENCES viewpoints(id)
);

-- 5. 可点击点和场景图
CREATE TABLE clickable_spots (
    id INTEGER PRIMARY KEY,
    panorama_id INTEGER NOT NULL,
    position_x REAL NOT NULL,                -- 全景图归一化坐标
    position_y REAL NOT NULL,
    direction REAL NOT NULL,
    label TEXT,                              -- "看向沙发"、"看向窗户"
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (panorama_id) REFERENCES panoramas(id)
);

CREATE TABLE scene_images (
    id INTEGER PRIMARY KEY,
    clickable_spot_id INTEGER,
    project_id INTEGER NOT NULL,
    panorama_id INTEGER,                    -- 来源全景图（用于一致性）
    view_direction REAL NOT NULL,
    image_url TEXT,
    status TEXT DEFAULT 'pending',
    -- 一致性约束快照
    constraints_json TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (clickable_spot_id) REFERENCES clickable_spots(id),
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (panorama_id) REFERENCES panoramas(id)
);
```

---

## 一·三、户型图解析方案

### 核心思路：依赖生图模型，减少预处理

现代多模态生图模型（如 Seedream、GPT-Image4 等）对图像结构理解能力较强，户型图的**墙体布局、空间关系、门窗位置**可以在 prompt 中直接声明，让模型理解并保持一致。

**减少预处理的好处**：
- 不用上复杂的 OpenCV 管线（透视矫正、Hough 直线检测、轮廓填充...）
- 不依赖 PaddleOCR（CPU 负担）
- 不用自己实现房间类型推断

**需要评估的风险**：
- 模型对户型图的"结构保持"能力——能不能真的识别并保持墙体线
- 多次生成时结构一致性如何

### 解析流程（简化版）

```
户型图上传
    │
    ├──→ 必要清洗（可选，按需）
    │       ├── 尺寸归一化（resize to 1024x1024 或 2048x2048）
    │       ├── 对比度增强（可选，CAD 图太淡时）
    │       └── 去背景（白底图直接用，拍照图可能需要）
    │
    ├──→ 语义提取（LLM / 规则）
    │       ├── 房间数量和类型推断（规则：面积+位置）
    │       └── 标注文字 OCR（轻量：EasyOCR 或 PaddleOCR，备选）
    │
    └──→ 输出 RoomState JSON
            {
              "walls": [...],
              "rooms": [...],
              "openings": [...],
              "summary": "3室2厅，客厅朝南，主卧带独立卫浴"
            }
```

### 待评估项（需要实测）

| 问题 | 评估方法 |
|---|---|
| 生图模型能否识别并保持户型图结构？ | 用同一张户型图 + 不同风格 prompt 生成 3 张，叠加对比墙体线重合度 |
| 多次生成时房间结构一致性？ | 同一 Viewpoint 生成 3 次，评估结构漂移程度 |
| OCR 房间名称是否必要？ | 先试不带 OCR 的效果，看模型能否正确识别"主卧""客厅" |

### 预处理工具选型（按需，轻量）

| 步骤 | 方案 | 说明 |
|---|---|---|
| 尺寸归一化 | PIL resize | 统一到 1024 或 2048 |
| 对比度增强 | OpenCV `convertScaleAbs` | CAD 图线条太淡时用 |
| 去背景 | OpenCV `inRange` 白色mask | 拍照图白底时用 |
| OCR（备选） | EasyOCR | 轻量，Python 包，可选 |

### 远期升级路径

如果实测发现模型对结构保持能力不足，再加回：
- M-LSD 墙体检测 → 结构线作为 prompt 约束
- Depth Anything → 深度图作为结构参考
- 现有的 warp 一致性方案

---

## 二、产品定义

**输入**（二选一）：
- A. 单视角房间照片 / 白模图 / 户型图
- B. 全景原图（2:1 equirect 毛坯房实拍，如 insta360/理光）——一致性最强的输入形态，商用主打

**输出**：同一房间的装修效果图 + 360° 全景图（线上可浏览、可分享）

**核心约束**：
1. 原图 → 效果图 → 全景图**结构一致**（同一间房）
2. 部署在**云服务器（纯 CPU，4核8G）**，Docker 化，7×24 对外服务，**无 GPU**
3. 一切输入输出基于生图模型 **API**（豆包/万相/OpenAI 系），不自部署生成模型
4. 有**准入管理**：不是谁都能生成，但不建重系统
5. 毛坯房最难，白模图/全景原图可降难度

### 一致性预期管理（先讲清楚，再选技术）

相机视锥内（约 90°~120° 水平）的信息在原图里真实存在，这部分可以做到**像素级一致**；
相机**背后**的内容原图里不存在，只能生成补齐。这是信息问题，不是工程问题。承诺分级：

| 级别 | 范围 | 保证 | 手段 |
|---|---|---|---|
| L1 | 相机可见区域 | ✅ 结构/像素一致 | 几何 warp（不是生成） |
| L2 | 效果图整体 | ✅ 结构线重合度可度量、不达标重试 | 指令式编辑 API + M-LSD 验收 |
| L3 | 相机背后区域 | ⚠️ 只保证风格/语义连贯 | mask 定点 outpainting API |
| L1-B | 全景原图输入 | ✅ 360° 全场 L1 | 全景图直接编辑 API，商用主卖点 |

对客户的话术只能说"同一间房"，不能说"背后那面墙长什么样是对的"。

---

## 二、技术核心：结构状态

### 问题

生图模型本质是随机的。两次调用同一个模型生成"北欧客厅"，得到的是两间不同的房。用户要的是**同一间房的不同表现**。

### 解法：房间 = 结构状态，一次提取，全链路复用

原则：**一次提取，全链路复用，禁止从中间产物重新估计**（re-extract 会累积误差、破坏一致性链条）。

```
structure_state = {
  source_hash,                    # 原图 hash，重复上传直接复用
  depth_map,                      # Depth Anything V2 Small（CPU，~秒级/张）
  line_map,                       # M-LSD（CPU，毫秒级）
  camera: {fov, pitch, roll},     # 透视参数估计，warp 用（起步 fov≈90° 也可用）
  room_layout                     # 远期升级：cuboid
}
```

结构状态在本方案里有**三个用途**（不是只给 ControlNet 喂条件，我们没有 GPU）：

1. **生成条件**：把 depth/line 作为条件喂给支持结构控制的 API（万相线稿生图），或在 prompt 中声明"保持原有空间结构、透视、门窗位置不变"
2. **验收标准**（关键）：产出后对该图跑 M-LSD，与 state.line_map 计算线段重合度 ≥ 阈值才放行；不达标自动换参数重试（best-of-N，最多 3 次）。一致性是**度量出来的**，不是靠相信模型
3. **全景 warp**：效果图 + state.depth 反投影到球面，得到 partial pano

```
用户照片 / 白模图 / 全景原图
       ↓
 ┌─────────────────────────────┐
 │ 结构状态提取（一次性，CPU）    │
 │ depth + mlsd + camera        │
 │ → rooms 表行 + COS 资产       │
 └─────────────────────────────┘
       ↓ 同一份 state 贯穿所有环节
 ┌─────────────────────────────┐    ┌──────────────────────────────┐
 │ 效果图生成（API）            │──→ │ 全景图生成                    │
 │ 指令编辑：原图 + 风格 prompt  │    │ 路径A（单视角输入）：          │
 │   （或 万相线稿生图）         │    │  效果图 + state.depth         │
 │ ↓                            │    │  → 针孔反投影 warp 到球面     │
 │ M-LSD 重合度验收（CPU）       │    │  → partial pano + 缺口 mask   │
 │ ↓ 不达标重试 ≤3 次           │    │  → 编辑/修补 API 补缺口       │
 │ 效果图入库                    │    │ 路径B（全景原图输入）：       │
 └─────────────────────────────┘    │  pano 图直接指令编辑 API      │
                                     └──────────────────────────────┘
```

### 全景一致性为什么靠 warp，而不是二次生成

- 效果图只覆盖相机前方，背后 270° 的内容不存在于任何输入里——**信息缺口**，再估深度也变不出来
- 从效果图重新估结构 = 让模型给自己的输出做标注，一致性链条断掉
- 通用生图 API 直出整幅 2:1 全景，畸变、接缝、与效果图对不齐，不可控

正确做法的信息论依据：**能几何确定的就不要生成**。

| 环节 | 手段 | 一致性来源 |
|---|---|---|
| 效果图 | 指令编辑 API（结构声明 + 线稿条件）| 模型受约束 + 产出后 M-LSD 度量验收 |
| 全景可见区 | 效果图 + state.depth 反投影 warp | 纯数学，100% 一致 |
| 全景缺口区 | mask outpainting API 只补缺口 | 被已 warp 内容强约束，风格连贯 |

warp 用的是 state.depth（原图提的那一份），CPU numpy 几十行代码，不需要 GPU。

> 若 mask 补缺口质量不达标，备选：万相画面扩图（wrap padding 后再扩）、或调研 DiffPano 类专用模型；warp 骨架不变。

### 为什么不自部署 SD+ControlNet / ComfyUI

| 维度 | 自部署 SD（GPU） | 托管生图 API |
|---|---|---|
| 服务器 | 云 GPU（T4 ¥800/月起）+ nvidia 运维 | 现有 4核8G CPU 云服务器就够 |
| 结构一致性 | 原生 ControlNet 强 | 指令编辑+线稿条件+**M-LSD 验收重试**补齐 |
| 成本 | 固定高成本，闲置照付 | 按张付费，量小极省 |
| 质量上限 | SD1.5 系一般 | 商用大模型（豆包/万相/gpt-image）更高 |

**结论**：一切生成交给 API，与"输入输出都基于生图模型"的产品原则一致。demo（renovate-demo）走 images.edit 中转 API 已跑通，链路已验证。

### 生图 API 供应商（adapter 抽象，config 可切换）

| 能力 | 候选 | 用途 |
|---|---|---|
| 指令式编辑（改风格保结构） | 火山豆包 Seedream/SeedEdit；OpenAI 系 images.edit | 效果图生成 |
| 线稿条件生图 | 阿里万相（sketch-to-image） | 结构条件更强时的备选通道 |
| mask 定点修补 / 画面扩展 | OpenAI 系 images.edit（mask）；万相扩图 | 全景缺口补齐 |
| 质检（可选） | 多模态理解模型 | 语义级抽检，起步可不做 |

- 统一封装一层 `generate(provider, task, ...)` adapter，供应商差异（鉴权/参数/计费）藏在里面；demo 已有雏形
- 价格以各官网公示为准，评测脚本跑通后用**结构重合度 + 单价**两个指标定主力供应商

---

## 三、技术栈

### 必须要的

| 层 | 选型 | 说明 |
|---|---|---|
| **容器编排** | Docker Compose | 2 服务（nginx + web），纯 CPU |
| **反向代理** | Nginx | HTTPS / 路由 / 静态文件 / 限流 |
| **业务后端** | FastAPI | 用户/任务/状态提取/验收/warp/切片，单容器 |
| **生成界面** | Gradio | `gr.mount_gradio_app()` 挂进 FastAPI，单进程 |
| **生图** | 托管 API 全家桶 | 豆包/万相/OpenAI 系，adapter 切换 |
| **数据库** | SQLite（WAL） | 四张表，挂 volume，零运维 |
| **准入** | 邀请码注册 + 手机验证码登录 | JWT httpOnly cookie |
| **结构提取** | Depth Anything V2 Small + M-LSD | 小模型，CPU 可跑，Apache-2.0 |
| **一致性验收** | M-LSD 线段重合度比对 | CPU，产出必过这道关 |
| **全景 warp** | py360convert + numpy | 几十行代码，纯几何，CPU |
| **超分** | 阿里云生成式超分 API | ¥0.06/张 |
| **切片** | Python（py360convert） | multires tiles |
| **图片存储** | 腾讯云 COS + CDN | 不存本地，tiles 直接 CDN 加载 |
| **全景浏览** | Pannellum 2.5.6 multires | 开源 MIT，demo 已验证 |
| **分享** | itsdangerous 签名链接 | 免登录、可过期 |

### 不要的（及原因）

| 不要 | 为什么 |
|---|---|
| **自部署 SD / ComfyUI** | 要 GPU 服务器，与"纯 CPU 云服务器 + 全走生图 API"硬冲突；按张付费的 API 更省 |
| GPU 机型 / nvidia runtime | 没有生成模型要跑，提取模型全 CPU |
| LangChain / LangGraph | 固定流程不是动态决策，Python 函数链够；多 agent 互相聊天才用 LangGraph |
| Celery / Redis | BackgroundTasks + 每用户任务锁够，月活 500+ 再上 |
| Postgres | SQLite(WAL) 撑到月活万级，升级路径明确 |
| K8s / 微服务 | 不到那个量级 |
| Vue/React 后台 | /admin 就一页，不建后台系统 |

---

## 四·一、Agent 设计决策

### 为什么不是 LangGraph

LangGraph 是为"多 Agent 协作、动态决策、有状态回退"的场景设计的（例如：多个 Agent 互相讨论、分支重试、循环决策）。你的流程本质是**工厂流水线**：

```
输入 → 结构提取 → 生图 → 质量检查 → 后处理 → 输出
```

每一步输入输出确定，没有"走哪条路"的动态决策，没有 Agent 间互相调用。LangGraph 的引入只会增加复杂度，不解决问题。

### 用 Pydantic AI 在哪里

**只在两个真正的决策点**：

| 决策点 | 输入 | 决策内容 | 输出 |
|---|---|---|---|
| **意图解析** | 用户自由文字 + 风格/房间类型选择 | 用户要什么？生成什么风格的图？ | 结构化参数：房间类型、风格、施工类型、英文 prompt |
| **质量验收** | 生成的图 + 原始结构 state | 这张图合格吗？ | passed: bool + score: int + issues: list[str] |

其他环节（结构提取、生图、后处理、warp、切片）都是**确定性函数**，不经过 LLM。

### Pipeline 架构

```
FastAPI 路由（只做分发，不含业务逻辑）
    │
    ▼
GenerationService（事务管理：建任务、扣积分、更新状态）
    │
    ▼
GenerationPipeline（函数链 + Agent 决策点）
    │
    ├── step_intent_parse()      ← Pydantic AI Agent（决策）
    ├── step_structure_extract()  ← Depth Anything + M-LSD（确定性）
    ├── step_image_generate()     ← 图像生成 API（确定性）
    ├── step_quality_check()      ← Pydantic AI Agent（决策）
    └── step_post_process()       ← warp + 超分 + 切片 + 上传（确定性）
```

### 什么时候需要更多 Agent

如果未来出现以下场景，才考虑增加 Agent：
- 用户可以在中途干预修改生成参数（Human-in-the-loop）
- 多张图之间需要互相参考（跨图一致性 Agent）
- 生成失败后需要模型自己决定怎么重试策略（自我反思 Agent）

目前的固定流水线够用，不要过度设计。

---

## 四、架构（Docker Compose，纯 CPU）

```
腾讯云 CVM（4核8G，无 GPU）
│
├─ nginx 容器 (:443/:80)
│   ├─ /            → 首页/登录（静态）
│   ├─ /app /api    → web 容器（FastAPI + Gradio 单进程）
│   ├─ /pano/<id>   → web 渲染 Pannellum + COS tiles URL
│   ├─ /s/<token>   → 分享入口（签名，免登录）
│   └─ /admin       → basic auth → web（单页管理）
│
└─ web 容器（CPU）
    ├─ FastAPI：鉴权 / 任务 / credits / adapter 调生图 API
    ├─ Gradio mount 在 /app → 生成交互界面
    ├─ 结构提取（Depth Anything + M-LSD，CPU）
    ├─ 一致性验收（M-LSD 重合度）/ warp / 切片
    ├─ SQLite：data volume（WAL）
    └─ 生图请求 → 托管 API → 收图 → COS

两个容器，docker compose up 就完事。GPU 自始至终不出现。
```

### 数据库（四张表）

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    phone TEXT UNIQUE NOT NULL,
    credits INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE invite_codes (
    code TEXT PRIMARY KEY,
    credits INTEGER DEFAULT 3,    -- 用该码注册赠送的额度
    used_by INTEGER,              -- 被哪个 user 用了，NULL=未用
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE rooms (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    source_hash TEXT NOT NULL,    -- 同图秒级复用
    input_type TEXT NOT NULL,     -- 'photo' | 'whitemodel' | 'pano'
    source_url TEXT,              -- 原图 COS URL
    state_url TEXT,               -- 结构状态 JSON + depth/mlsd 资产 COS 前缀
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE generations (
    id INTEGER PRIMARY KEY,
    room_id INTEGER NOT NULL,     -- 归属哪个房间（状态实体）
    type TEXT NOT NULL,           -- 'effect' | 'pano'
    style TEXT,
    provider TEXT,                -- 实际用了哪家 API（验收数据的来源）
    structure_score REAL,         -- M-LSD 重合度验收分，留档
    output_image_url TEXT,
    pano_url TEXT,
    status TEXT DEFAULT 'pending',
    cost REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_id) REFERENCES rooms(id)
);
```

**房间 = 状态实体**：用户反复给同一间房换风格/出全景，state 只提一次。

### 接入与准入（够轻，别过度设计）

1. **准入+登录**（已简化，2026-09-09）：邀请码即登录，一店一码一账号。彻底砍掉短信/手机号——短信通道需企业资质且审核要排期，这个量级用不上
3. **计费**：credits 颗数，生成前事务内扣减，失败退还
4. **分享**：`/s/<token>`（itsdangerous 签名），免登录、可设过期——给客户看效果就靠它
5. **后台**：`/admin` 单页（用户列表 / 任务记录 / 手动加余额 / 发码），nginx basic auth 保护
6. **防滥用**：nginx limit_req 限频 + 每用户同时在跑 1 个任务 + 邀请码初始额度有限

---

## 五、生成流程（7 步）

```
1. 用户上传照片/白模图/全景原图 + 选风格/家具
       ↓
2. 结构状态提取（CPU）
   同 source_hash 已有 → 直接复用 rooms 行
   否则 → Depth Anything + M-LSD + camera 估计 → 存 COS + 写 rooms 表
       ↓
3. prompt 组装：风格模板（prompts/ 已有）+ 用户附加要求
       ↓
4. 效果图生成（API）
   原图 + prompt（+线稿条件）→ 编辑 API → 出图
   → M-LSD 重合度验收，不达标重试（≤3 次，计 best-of-N）
       ↓
5. 全景图生成
   路径A：效果图 + state.depth → warp partial pano + mask → 修补 API 补缺口
   路径B（全景原图）：pano 图 → 指令编辑 API 直接改造
   → 2:1 equirectangular
       ↓
6. 后处理
   全景图 → 阿里云超分（4x → 6K）→ multires 切片 → 上传 COS
       ↓
7. 入库 + 通知
   写 generations 表（含 provider、structure_score）→ 返回 /pano/<id> + 分享链接
```

---

## 六、成本

### 月度运营

| 项 | demo 规模（~100张/月） | 小商家（1000张/月） |
|---|---|---|
| CVM 4核8G（纯 CPU） | ¥200 | ¥200 |
| 生图 API（含 1.3x 重试余量）| ~¥50 | ~¥300 |
| COS + CDN | ¥5 | ¥7 |
| 阿里云超分 | ¥6 | ¥60 |
| **合计** | **~¥270** | **~¥580** |

> 无 GPU 月租，无图像自托管运维。生成 API 单价以供应商官网为准（编辑类模型常见档位 ¥0.2~0.5/张），评测后用"结构重合度×单价"定主力供应商。
> 对比自部署 GPU 方案（~¥1080/月），API 方案量小阶段便宜一半以上。

### 单张成本

| 环节 | 成本 |
|---|---|
| 结构提取 | ~0（CPU 本地，一次性） |
| 生图 API（含重试）| ~¥0.3 |
| 超分 API | ¥0.06 |
| 存储+流量 | ~¥0.01 |
| **合计** | **~¥0.4/张** |

---

## 七、技术选型依据速查

| 问题 | 答案 |
|---|---|
| 结构一致性怎么保证？ | 深度图+直线图+camera 作为"结构状态"，一次提取全链路复用 |
| 效果图一致性靠什么？ | 指令编辑 API + M-LSD 重合度验收，不达标重试——度量出来的 |
| 全景一致性靠什么？ | **几何 warp**（CPU），可见区不靠生成；缺口区 mask 修补 API |
| 生成模型谁提供？ | 托管生图 API（豆包/万相/OpenAI 系），adapter 可切换 |
| 要 GPU 吗？ | **不要**。提取模型全是小模型，CPU 可跑 |
| 为什么不是 ComfyUI？ | 要 GPU 服务器，与纯 CPU 云服务器部署冲突，还更贵 |
| 为什么不用 LangChain？ | 固定流程不是动态决策，Python 函数够 |
| 前后端分离吗？ | 不分：Gradio mount 进 FastAPI 单进程 |
| 要数据库吗？ | SQLite 四张表，WAL 挂卷 |
| 怎么 Docker 部署？ | compose 两容器（nginx + web），纯 CPU，compose up 即上线 |
| 谁都能生成吗？ | 邀请码准入 + credits 计费 + 限流 |
| 全景图怎么不卡？ | multires 切片 + CDN 渐进式加载 |

---

## 八、项目结构

```
workspace/
├── TECH_SPEC.md          ← 本文档（唯一技术方案）
├── docker-compose.yml    ← nginx + web 两服务（待建）
├── Dockerfile            ← web 镜像（待建）
├── deploy/               ← nginx.conf 等（待建）
├── renovate-demo/        ← 2D 效果图 demo（Gradio port 7860，images.edit 链路已通）
│   ├── app.py
│   ├── config.json
│   └── prompts/
├── pano-demo/            ← 全景图 demo（HTTP port 8700）
│   ├── generate.py
│   ├── viewer.py
│   ├── prompts.py
│   ├── config.json
│   ├── outputs/
│   └── README.md
└── demo.py               ← 早期测试脚本
```

---

## 九、下一步（按风险排序，最难的先验证）

1. **供应商结构保持率实测（最高优先级）**：用同一批测试图调各家编辑 API，产出后跑 M-LSD 重合度打分 → 用数据决定主力供应商和验收阈值（纯 CPU 脚本，立刻能做）
2. **验证全景 warp 链路**：效果图 + depth → 反投影 partial pano（CPU）→ mask 修补 API → Pannellum 看接缝
3. **抽 adapter**：把 demo 里的 images.edit 调用收敛成 generate(provider, task) 统一接口
4. **接阿里云超分 + 写切片脚本**
5. ~~搭后端骨架~~（已完成：FastAPI + SQLite 三表 + 邀请码登录）
6. **部署联调**：docker-compose（frontend 内 nginx 兼任入口）+ COS/CDN

---

## 十、前端部署踩坑记录（2026-09-10）

> 以下为 `demo/` 全景看房 Demo 从本地开发到云服务器部署过程中实际踩到的坑及解决方案，供正式工程参考。

### 10.1 Docker 构建相关

| 坑 | 现象 | 根因 | 解法 |
|---|---|---|---|
| **nginx:alpine 镜像拉不下来** | `docker pull nginx:alpine` 层下载卡死/超时 | 国内网络拉 Docker Hub 大层（>4MB）极不稳定，多个镜像源（1ms.run、xuanyuan.me、daocloud）都存在大层卡死问题 | 放弃多阶段构建（node:20-slim + nginx:alpine），改为**单阶段 node:20-slim** + 自写 Node.js 静态服务器 `server.cjs`，完全绕开 nginx |
| **docker buildx i/o error** | `failed to fetch metadata: fork/exec .../docker-buildx: input/output error` | WSL 中 buildx 插件文件损坏/不可执行 | 非阻塞警告，legacy builder 正常工作，可忽略；如需修复可重装 buildx 插件 |
| **镜像源选择** | 不同镜像源速度差异极大 | 部分镜像源对大层支持差 | `docker.m.daocloud.io` 对小层最快，但大层仍可能卡死。最终方案：避免拉取大镜像，只用已缓存的 `node:20-slim` |

### 10.2 Node.js 运行时相关

| 坑 | 现象 | 根因 | 解法 |
|---|---|---|---|
| **require is not defined（容器启动即崩）** | 容器日志报 `ReferenceError: require is not defined`，容器反复重启 | `package.json` 中 `"type": "module"` 导致 Node.js 把所有 `.js` 文件按 ES Module 模式加载，CommonJS 的 `require()` 不可用 | 将 `server.js` 重命名为 **`server.cjs`**，`.cjs` 扩展名强制 CommonJS 模式；Dockerfile CMD 同步改为 `["node", "server.cjs"]` |
| **sudo docker 读不到认证** | `sudo docker push` 报 `denied: requested access to the resource is denied` | `sudo` 切到 root 用户，root 的 `~/.docker/config.json` 没有认证信息 | 不用 sudo，直接用 docker 组用户执行 push；或将 config.json 复制到 `/root/.docker/` |

### 10.3 腾讯云 TCR 个人版相关

| 坑 | 现象 | 根因 | 解法 |
|---|---|---|---|
| **docker login 失败** | `unauthorized: no scope specify` | TCR 个人版 `/v2/` ping 返回 401 且 token endpoint 要求 scope 参数，Docker login 的无 scope token 请求被拒 | TCR 个人版已知问题。**手动写 `~/.docker/config.json`** 的 `auths` 字段（base64 of `user:password`），push 时 Docker 自动走 Bearer token 流程 |
| **push denied（actions 为空）** | JWT token 的 `actions: []` 为空数组，无 push/pull 权限 | TCR 个人版需在控制台**初始化/重置固定密码**，不是腾讯云账号密码 | 控制台 → 实例管理 → 个人版实例 → 更多 → **重置登录密码**。重置后 push 立即生效 |
| **namespace 不匹配** | push 报 `denied`，token endpoint 返回 `image repo not found` | 用户在控制台创建的 namespace 名为 `pano-demo`，但 Makefile 配置的是 `pano` | 确保 Makefile `NAMESPACE` 与控制台创建的 namespace 完全一致 |
| **镜像地址格式** | `ccr.ccs.tencentyun.com/pano/pano-demo` vs `ccr.ccs.tencentyun.com/pano-demo/pano-demo` | TCR 个人版地址格式为 `ccr.ccs.tencentyun.com/<namespace>/<repo>`，namespace 和 repo 名可能相同 | 仔细核对控制台显示的"镜像地址"字段，与 Makefile/CI 配置完全对齐 |

### 10.4 全景图性能相关

| 坑 | 现象 | 根因 | 解法 |
|---|---|---|---|
| **手机端加载极慢** | 全景图加载需 30s+，手机几乎不可用 | 原图为 PNG 无损压缩，单张 28-30MB；4 张图共 ~100MB | ImageMagick 转 **JPG quality=85** + 生成 **mobile（4096px 宽）和 thumb（512px 宽）** 多分辨率版本。总体积从 99MB → 12MB |
| **手机端无法滑动查看全景** | 触摸拖动无响应，页面不旋转 | 1) CSS 缺少 `touch-action: none`，浏览器拦截触摸事件；2) PSV v5 配置 `mousemove: !isMobile` 在手机上禁用了移动 | 1) `.viewer-page` 和 `.psv-container` 添加 `touch-action: none`；2) `mousemove: true`（PSV v5 中此选项同时控制触摸拖动） |
| **PNG vs JPG** | 全景照片用 PNG 格式 | PNG 无损压缩对照片类内容极其浪费 | 全景照片统一用 **JPG**，quality 85 视觉无损，体积缩小 10-15 倍。WebP 更优但 PSV 兼容性需验证 |

### 10.5 Docker 部署架构决策

```
初始方案（失败）:
  Stage 1: node:20-slim  → npm build → dist/
  Stage 2: nginx:alpine  → COPY dist/ → serve    ← 拉不下来

最终方案（成功）:
  Stage 1: node:20-slim  → npm build → dist/
         → server.cjs (Node.js 静态服务器)
         → CMD ["node", "server.cjs"]
```

`server.cjs` 实现了 nginx 的全部必要功能：

- ✅ 静态文件 serve + MIME 类型
- ✅ SPA fallback（`try_files $uri /index.html`）
- ✅ gzip 压缩（JS/CSS/JSON/SVG）
- ✅ 全景图缓存 7 天（`/panoramas/` 路径）
- ✅ JS/CSS 永久缓存（hash 文件名）
- ✅ manifest.json 不缓存（`no-cache`，方便实时更新）
- ✅ 外部目录挂载（`/data/panoramas` VOLUME，运行时可覆盖内置图）

### 10.6 关键配置速查

**Docker daemon.json（WSL /etc/docker/daemon.json）**：
```json
{
  "registry-mirrors": ["https://docker.1ms.run", "https://docker.xuanyuan.me"]
}
```

**Docker config.json（~/.docker/config.json）**：
```json
{
  "auths": {
    "ccr.ccs.tencentyun.com": {
      "auth": "<base64(username:password)>"
    }
  }
}
```

**Photo Sphere Viewer v5 手机触摸配置**：
```js
{
  mousemove: true,              // 不能按 isMobile 禁用
  touchmoveTwoFingers: false,   // 单指拖动
  moveInertia: true,
}
// CSS: .psv-container { touch-action: none; }
```

**全景图优化命令**：
```bash
# PNG → JPG + 多分辨率
convert input.png -quality 85 -strip output.jpg                    # full
convert input.png -resize 4096x -quality 80 -strip output_mobile.jpg  # mobile
convert input.png -resize 512x -quality 70 -strip output_thumb.jpg    # thumb
```

### 10.7 版本历史

| 版本 | 日期 | 变更 |
|---|---|---|
| v1.0.0 | 09-09 | 初始多阶段构建（nginx:alpine），push 失败 |
| v1.1.0 | 09-10 | 改单阶段 node:20-slim + server.js，支持全景图外部挂载 |
| v1.1.1 | 09-10 | 修复 `type: module` 导致的 require 崩溃（server.js → server.cjs） |
| v1.2.0 | 09-10 | 全景图 PNG→JPG 优化（99MB→12MB）+ 手机触摸修复 |
