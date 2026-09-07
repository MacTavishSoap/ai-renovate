# Product

<!-- impeccable:product-schema 1 -->

## Platform

web (移动端优先)

## Stack

前端：Vue 3 + Vite + Vant 4（移动端组件库）+ Photo Sphere Viewer（全景引擎）
后端：FastAPI + SQLite(WAL) + Docker Compose
部署：腾讯云 CVM 4核8G（纯 CPU，无 GPU）+ Nginx + COS + CDN

## Users

- **C 端装修业主**：想看到自己家装修后的效果。在手机上操作，上传房间照片或白模图，选风格，等几十秒拿到效果图和 360° 全景。不是设计师，不懂专业术语。
- **B 端（潜在）**：设计师/装修公司用这个工具给客户展示方案。当前以 C 端为主。

## Product Purpose

让普通人不靠设计师，用手机拍一张照片就能看到装修后的效果——效果图 + 可拖动的 360° 全景。核心价值是"看到自己家变什么样"，不是"设计一个新家"。

## Positioning

- 不是设计工具（酷家乐/三维家是给设计师用的 3D 编辑器）
- 不是效果图素材库（好好住/小红书是看别人的家）
- 是"你的家 → 装修后"的视觉转换器，同一间房、不同风格

## Operating Context

- 用户在手机上完成全流程：拍照/上传 → 选风格 → 等待 → 浏览 → 分享
- 生成一张效果图约 30-60 秒，全景图更长
- 全景图在手机端全屏拖动浏览，支持场景间切换（客厅→卧室→厨房）
- 分享链接免登录可看，有有效期
- 积分制准入，不是谁都能生成

## Capabilities and Constraints

- 输入：单视角房间照片 / 白模图 / 户型图 / 全景原图（2:1 equirect）
- 输出：同一房间的装修效果图 + 360° 全景图
- 结构一致性是核心承诺：原图→效果图→全景图必须是同一间房
- 生成全走托管生图 API（豆包/万相/OpenAI 系），不自部署模型，纯 CPU 服务器
- 结构提取用小模型（Depth Anything V2 Small + M-LSD），CPU 可跑
- 全景图 multires 切片 + CDN 加载，手机端流畅
- 超分用阿里云 API（生成式超分 ¥0.06/张）
- 准入：邀请码注册 + 手机验证码 + 积分制
- 数据库 SQLite 四张表（users / invite_codes / rooms / generations）

## Brand Commitments

- [推断] 品牌名待定，暂用"AI 家装"
- [推断] 无现有 logo / VI / 品牌色，设计系统从零建立
- [推断] 调性偏向专业可信（像贝壳找房的干净专业感），而非温暖生活化（好好住）或高端设计感

## Evidence on Hand

- renovate-demo：可运行的 2D 效果图 demo（Gradio，441 行）
- pano-demo：可运行的全景图 demo（HTTP server + Pannellum，267 行）
- 测试全景图输出：test_nordic_01.jpg (2048×1024)、test_nordic_hq.jpg (4096×2048)
- 超分对比图：超分例子.jpg (8192×4096, 2.9MB, 清晰) — 阿里云生成式超分真实结果
- 竞品参考：vr.justeasy.cn（krpano + Next.js，底部场景轮播切换）
- TECH_SPEC.md：完整技术方案 v5.0

## Product Principles

1. **同一间房**——所有输出必须与输入是同一个房间，这是产品存在的理由
2. **手机优先**——用户在手机上完成全流程，PC 是次要适配
3. **等待可接受，质量不可妥协**——30-60 秒可以等，但出来的图必须清晰、结构对
4. **简单到不需要教**——不需要懂装修术语，选个风格就行
5. **能分享才有传播**——全景图分享链接是获客渠道

## Accessibility & Inclusion

- 移动端触控交互，全景图需支持陀螺仪
- 验证码登录无需密码，降低使用门槛
- [待确认] 是否需要无障碍标准合规
