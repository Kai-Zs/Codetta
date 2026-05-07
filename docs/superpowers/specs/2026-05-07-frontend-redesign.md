# 练笔小筑 — 前端重写设计文档

## 一、路由表（不变）

| 路径 | 视图 | meta |
|------|------|------|
| `/login` | LoginView | — |
| `/` | HomeView | auth |
| `/practice/sequential` | PracticeView | auth |
| `/practice/random` | PracticeView | auth |
| `/practice/wrong` | PracticeView | auth |
| `/wrong` | WrongBooks | auth |
| `/wrong/:qid` | PracticeView | auth, readonly |
| `/admin/reset-pin` | AdminResetPin | auth |

路由守卫逻辑不变：无 token → `/login`；有 token 在 `/login` → `/`。

## 二、页面层级

```
App.vue                          ← 全局壳：背景 + 手机壳 + 编辑器浮层
├── BackgroundLayer              ← CSS-only，固定全屏，pointer-events: none
├── PhoneShell                   ← 340×9:16，r=20，居中
│   └── <router-view />          ← 所有页面渲染在此
│       ├── LoginView
│       ├── HomeView
│       ├── PracticeView
│       ├── WrongBooks
│       └── AdminResetPin
└── CodeEditorPanel              ← Teleport→body，编程题时显示，手机右侧
```

### 关键约束

- **BackgroundLayer**：纯 CSS，不依赖 JS。渐变底 + inline SVG 图案 + CSS animation。`prefers-reduced-motion` 时停动画。
- **PhoneShell**：`App.vue` 提供，各视图无需感知。内部 `overflow-y: auto`。
- **CodeEditorPanel**：通过 Pinia store 控制显隐。仅在 PracticeView 且 question.type === "编程题" 且 progMode === "write" 时显示。进入时 fade + 右滑入（300ms）。

## 三、核心组件

### 可复用组件（保留并重写）

| 组件 | 职责 | 使用者 |
|------|------|--------|
| `BottomDisclaimer` | 底部免责声明 | HomeView, PracticeView, WrongBooks |
| `Toast` | 轻提示 | 全局（Teleport） |
| `LoadingSpinner` | 加载动画 | 各视图 |
| `EmptyState` | 空状态占位 | WrongBooks |
| `ConfirmDialog` | 二次确认弹窗 | HomeView, WrongBooks |
| `FilterModal` | 随机抽题筛选弹窗 | HomeView |
| `SettingsPanel` | 设置侧滑面板 | HomeView, PracticeView |
| `AnswerSheet` | 答题卡弹窗 | PracticeView |
| `ProgModeModal` | 编程模式首次选择弹窗 | PracticeView |

### 题目组件（保留并重写）

| 组件 | 对应题型 |
|------|----------|
| `SingleChoice` | 单选题 |
| `TrueFalse` | 判断题 |
| `FillBlank` | 填空题 |
| `CodeWrite` | 编程题 write 模式（只渲染题干部分） |
| `CodeReview` | 编程题 review 模式 |

### 新增组件

| 组件 | 职责 |
|------|------|
| `BackgroundLayer` | 全屏动态背景，纯 CSS |
| `PhoneShell` | 手机外框容器，包裹 `<slot>` |
| `CodeEditorPanel` | 代码编辑器浮层大面板 |

## 四、状态管理（保留逻辑，重写代码）

### auth store
- `token`, `user` 状态
- `login()`, `verifyPin()`, `setPin()`, `fetchMe()`, `updateSettings()`, `logout()` actions
- token 同步 localStorage

### practice store
- `currentQuestion`, `mode`, `filters`, `loading` 状态
- `fetchQuestion()`, `fetchNextQuestion()`, `submitAnswer()`, `setMode()`, `setFilters()` actions
- **新增**：`showEditor` — 控制 CodeEditorPanel 显隐

### wrong store
- `list`, `filters`, `pagination`, `selected`, `loading` 状态
- `fetchList()`, `removeFromWrong()`, `exportExcel()`, `toggleSelect()`, `selectAll()` actions
- 逻辑不变

### settings store
- `progMode`, `soundOn`, `vibrateOn` 状态
- `init()`, `update()` actions
- 逻辑不变

## 五、API 层（不变）

`frontend/src/api/index.js` 保持不变：axios 实例，baseURL `/api`，自动附加 Bearer token，401 跳转登录。

## 六、主要交互流程

### 登录流程
1. 输入学号 → `POST /auth/login`
2. `need_setup` → 设 PIN 页面（两次输入）
3. `need_pin` → 输 PIN 页面（4 位）
4. 成功 → token 存 localStorage → 跳转 `/`

### 刷题流程（非编程题）
1. 进入 `/practice/sequential` 或 `/practice/random`
2. 加载题目列表 → 渲染第一题
3. 用户作答 → 点提交 → `POST /progress`
4. 显示结果（正确/错误高亮）
5. 下一题 → 加载下一题内容

### 刷题流程（编程题 write 模式）
1. 进入 PracticeView，检测 question.type === "编程题" 且 progMode === "write"
2. `showEditor = true` → 手机左移，CodeEditorPanel 从右侧滑入
3. 用户在编辑器中写代码
4. 点提交 → `POST /judge/code` → 显示 AI 评分+评语
5. 编辑器可重置代码到模板

### 错题管理流程
1. `/wrong` → WrongBooks
2. 筛选 → 勾选 → 重做（跳 `/practice/wrong?ids=...`）/ 移出 / 导出

## 七、不做

- 不改路由结构
- 不改 API 调用方式
- 不改 Pinia store 业务逻辑（仅新增 `showEditor`）
- 不改后端
- 不改题库数据
