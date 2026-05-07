# Codetta 前端设计文档

## 技术栈

Vue 3 + Vite + Vue Router + Tailwind CSS + Pinia

## 路由

| 路径 | 页面 | 说明 |
|------|------|------|
| `/login` | LoginView | 学号 → PIN → 设 PIN（三阶段内聚） |
| `/` | HomeView | 进度概览 + 入口 + 用户名菜单 + 设置 |
| `/practice/sequential` | PracticeView | 顺序刷题 |
| `/practice/random` | PracticeView | 随机抽题（先弹筛选） |
| `/practice/wrong` | PracticeView | 错题重做（`?source=wrong`） |
| `/wrong` | WrongBooks | 错题列表管理 |
| `/wrong/:qid` | PracticeView | 错题只读详情（回看） |
| `/admin/reset-pin` | AdminResetPin | 隐藏路由 |

路由守卫：未登录 → 重定向 `/login`

## 组件树

```
App.vue
├── Toast.vue                     # 全局轻提示
├── views/
│   ├── LoginView.vue             # 登录三阶段
│   ├── HomeView.vue              # 首页
│   ├── PracticeView.vue          # 刷题容器（所有模式共用）
│   ├── WrongBooks.vue            # 错题管理
│   └── AdminResetPin.vue         # 隐藏
├── components/
│   ├── practice/
│   │   ├── SingleChoice.vue      # 单选题
│   │   ├── TrueFalse.vue         # 判断题
│   │   ├── FillBlank.vue         # 填空题
│   │   ├── CodeWrite.vue         # 编程-write
│   │   └── CodeReview.vue        # 编程-review
│   ├── common/
│   │   ├── FilterModal.vue       # 随机筛选 / 错题筛选
│   │   ├── ProgModeModal.vue     # 首次编程题模式选择
│   │   ├── AnswerSheet.vue       # 答题卡悬浮窗
│   │   ├── SettingsPanel.vue     # 设置悬浮窗
│   │   ├── ConfirmDialog.vue     # 二次确认弹窗
│   │   ├── LoadingSpinner.vue    # 加载态
│   │   └── EmptyState.vue        # 空状态
│   └── layout/
│       └── BottomDisclaimer.vue  # 底部免责声明
└── stores/
    ├── auth.js                   # token/user/login/logout
    ├── practice.js               # 当前题/筛选/答题卡/提交
    ├── wrong.js                  # 错题列表/分页/操作
    └── settings.js               # prog_mode/sound/vibrate
```

## Pinia Store

### authStore
- state: `token`, `user` (name/student_id/prog_mode/sound/vibrate), `isLoggedIn`
- actions: `login(id)`, `verifyPin(id, pin)`, `setPin(pin, oldPin?)`, `fetchMe()`, `updateSettings(data)`, `logout()`
- persist: token 存 localStorage

### practiceStore
- state: `currentQuestion`, `mode` (sequential/random/wrong), `filters` (type/chapter/status), `answerSheet` (已做题目状态列表), `loading`, `error`
- actions: `fetchQuestion(id)`, `fetchNextQuestion()`, `submitAnswer(data)`, `setFilters(f)`, `setMode(m)`

### wrongStore
- state: `list`, `filters`, `pagination` (page/total/per), `selected` (勾选), `loading`
- actions: `fetchList()`, `removeFromWrong(ids)`, `toggleSelect(id)`, `selectAll()`, `exportExcel()`

### settingsStore
- state: `progMode`, `soundOn`, `vibrateOn`
- actions: `updateSettings()`, `setProgMode(m)`, 从 authStore.user 初始化

## 关键交互

### 编程题首次弹窗
- 后端 `auth/me` 返回 `prog_mode=null` → 弹出 ProgModeModal
- 选择 write/review → PATCH `/api/auth/settings`
- 关闭弹窗 = 默认 write，右下角 Toast 提示

### 随机抽题筛选
- 点击首页"随机抽题" → FilterModal（题型/章节/状态）
- 确认 → push `/practice/random` + 筛选参数

### 错题重做
- 错题页勾选 → "练习重做" → push `/practice/wrong?ids=1,2,3`
- PracticeView 读取 ids，只加载这批题

### DeepSeek 超时
- 40s 无响应 → 显示"判题超时" + 两个按钮：[做对了] [做错了]
- 用户手动选择 → 提交到 progress

### 响应式断点
- 手机 (< 768px): 单栏，编程题题干上编辑器下
- 大屏 (>= 768px): 双栏，编程题题干左编辑器右
- 答题卡: 手机全屏弹窗，大屏悬浮窗

### 三态覆盖
- Loading: LoadingSpinner（>300ms 显示）
- Empty: EmptyState + 引导文案
- Error: Toast 红色提示 + 重试按钮

## 设计 Token

- 主色: `#7C3AED`（紫）
- 强调: `#059669`（绿）
- 背景: `#FAF5FF`
- 字体: Cormorant Garamond（标题）+ Noto Sans SC（正文）
- 圆点: 正确=绿、错误=红、未做=灰
- 底部始终: "题库答案不一定完全正确，仅供参考"
- AI 标注: "人工智能生成，仅供参考"

## 非功能

- PWA manifest + 离线提示
- 声音反馈（正确/错误音效，可关闭）
- 震动反馈（移动端，可关闭）
- 路由懒加载（`() => import(...)`）
