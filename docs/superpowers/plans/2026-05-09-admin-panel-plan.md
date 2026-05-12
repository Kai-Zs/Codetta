# Codetta 管理员后台实施计划

> 设计文档：`docs/superpowers/specs/2026-05-09-admin-panel-design.md`
> 数据库约束：不改表结构
> 设计：大屏 PC 侧边栏布局，卡片风格与手机壳统一

---

### Task 1: 后端 Admin API

**目标**：新增 `/api/admin/*` 路由组，统一校验管理员密码。

**Files:**
- Create: `backend/app/routers/admin.py`
- Create: `backend/app/services/admin.py`
- Create: `backend/app/schemas_admin.py`
- Modify: `backend/app/main.py`（注册路由）

**Steps:**
- [ ] 创建 `schemas_admin.py`：Pydantic 请求体模型
- [ ] 创建 `services/admin.py`：
  - `verify_admin(password) → bool`
  - `list_questions(type, chapter, q_number, page, per) → dict`
  - `update_question(id, data) → dict`
  - `create_question(data) → dict`
  - `toggle_question_active(id) → dict`
  - `list_users(search, page, per) → dict`
  - `get_user_detail(user_id) → dict`
  - `reset_user_pin(user_id) → None`
  - `get_stats() → dict`
  - `get_maintenance_status() → bool`
  - `toggle_maintenance(enable) → None`
  - `change_admin_password(new_password) → None`
  - `reload_seed() → None`
- [ ] 创建 `routers/admin.py`：
  - 所有路由统一 `Depends(verify_admin_password)` 中间件
  - `POST /api/admin/verify`（无需鉴权，用于前端密码验证）
  - `GET /api/admin/questions`
  - `PUT /api/admin/questions/{id}`
  - `POST /api/admin/questions`
  - `PUT /api/admin/questions/{id}/active`
  - `GET /api/admin/users`
  - `GET /api/admin/users/{id}`
  - `POST /api/admin/users/{id}/reset-pin`
  - `GET /api/admin/stats`
  - `GET /api/admin/settings`
  - `POST /api/admin/maintenance`
  - `PUT /api/admin/password`
  - `POST /api/admin/reload-seed`
- [ ] `main.py`：`app.include_router(admin.router)`
- [ ] 在 `config.py` 读取 `ADMIN_PASSWORD` 环境变量
- [ ] Commit

---

### Task 2: 前端 AdminLayout + 路由 + 鉴权

**目标**：搭建管理后台骨架——侧边栏布局、路由、管理员密码弹窗。

**Files:**
- Create: `frontend/src/views/admin/AdminLayout.vue`
- Create: `frontend/src/views/admin/AdminLogin.vue`（密码弹窗组件）
- Modify: `frontend/src/router/index.js`

**Steps:**
- [ ] 创建 `AdminLayout.vue`：
  - 复用 `BackgroundLayer`
  - 左右两张卡片：左侧 `AdminSidebar`（200px）+ 右侧 `router-view`（flex-1）
  - 卡片样式：20px 圆角、双层紫边框、白底/暗黑底
  - 侧边栏菜单：Codetta Admin 标题 + 题目管理/用户管理/数据统计/系统设置 + 返回前台
  - 底部备案信息
- [ ] 创建 `AdminLogin.vue`：
  - 居中弹窗（Teleport to body），密码输入框 + 确认按钮
  - 验证成功存 sessionStorage `admin_token`
- [ ] 更新路由：
  - 添加 `/admin` 主路由，component=AdminLayout，children 为四个子页面
  - 路由守卫：检查 `admin_token`，无则显示 AdminLogin 弹窗（不跳转，在原页面上弹窗）
  - 移除旧的 `/admin/reset-pin` 路由
- [ ] Commit

---

### Task 3: 题目管理页面

**目标**：题目搜索、列表、新增、编辑、停用。

**Files:**
- Create: `frontend/src/views/admin/AdminQuestions.vue`
- Create: `frontend/src/views/admin/QuestionEditModal.vue`

**Steps:**
- [ ] `AdminQuestions.vue`：
  - 搜索栏：题号/题型下拉/章节下拉/搜索按钮
  - 表格列表：题号/题型/标题/状态/操作（编辑/停用）
  - 分页
  - 底部"新增题目"按钮
- [ ] `QuestionEditModal.vue`：
  - 居中弹窗（与 FilterModal 同款动画）
  - 基础字段：题号、章节、题型、标题、题干
  - 根据题型动态显示额外字段
  - 单选：选项行（可增减）+ 正确答案选择
  - 判断：正确/错误单选
  - 填空：多空输入（$ 分隔）
  - 编程：预置代码 textarea + 答案代码 textarea
  - 备注字段
  - 保存/取消按钮
- [ ] Commit

---

### Task 4: 用户管理页面

**目标**：用户搜索、列表、重置 PIN、查看详情。

**Files:**
- Create: `frontend/src/views/admin/AdminUsers.vue`
- Create: `frontend/src/views/admin/AdminUserDetail.vue`

**Steps:**
- [ ] `AdminUsers.vue`：
  - 搜索：学号/姓名 input + 搜索按钮
  - 表格：学号/姓名/做题数/正确率/最后活跃/操作（重置PIN/详情）
  - 分页
  - 重置PIN：ConfirmDialog 二次确认 → 调用 API
- [ ] `AdminUserDetail.vue`：
  - 用户基本信息卡片
  - 统计数字（做题数/正确率/错题数）
  - 最近答题记录表格（题号/题型/时间/正误）
  - 返回按钮
- [ ] Commit

---

### Task 5: 数据统计页面

**目标**：总览统计、章节正确率、题型分布、活跃 TOP10。

**Files:**
- Create: `frontend/src/views/admin/AdminStats.vue`

**Steps:**
- [ ] 四张总览卡片（grid 2x2）：总用户数/总题数/总提交数/整体正确率
- [ ] 章节正确率表格
- [ ] 题型分布列表
- [ ] 活跃用户 TOP10 表格
- [ ] 数据从 `GET /api/admin/stats` 一次性加载
- [ ] Commit

---

### Task 6: 系统设置页面

**目标**：维护模式开关、改管理员密码、题库重载。

**Files:**
- Create: `frontend/src/views/admin/AdminSettings.vue`

**Steps:**
- [ ] 维护模式开关（toggle switch）
- [ ] 改密码：旧密码 + 新密码 + 确认新密码 表单
- [ ] 题库重载：红色按钮 + ConfirmDialog "确定重载题库？此操作不可恢复"
- [ ] Commit

---

### Task 7: 维护模式全局拦截

**目标**：当维护模式开启时，非管理员用户访问任何页面显示维护提示。

**Files:**
- Modify: `frontend/src/router/index.js`
- Create: `frontend/src/views/MaintenanceView.vue`

**Steps:**
- [ ] `MaintenanceView.vue`：简洁维护提示页面（"系统维护中，请稍后再试"）
- [ ] 路由守卫：每次页面切换时检查维护状态（调 API 或读本地标记）
- [ ] 优化：Admin 页面不受维护模式限制（管理员需要能关闭维护模式）
- [ ] Commit

---

### Task 8: 联调 + 测试 + 构建

**Steps:**
- [ ] 启动本地前后端，设置 `ADMIN_PASSWORD` 环境变量
- [ ] 测试管理员登录 → 各模块功能
- [ ] 测试维护模式开启/关闭
- [ ] 测试题目新增/编辑/停用
- [ ] 测试用户搜索/重置 PIN/详情
- [ ] 修复联调问题
- [ ] `npm run build` + 部署到服务器
