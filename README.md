DepScan 使用文档

 项目简介

DepScan（全称：Dependency Scanner）是一款面向开发者的命令行工具，它能像“雷达”一样，自动扫描开源项目的关键健康指标，在30秒内生成易懂的风险报告，帮助你在引入依赖前识别潜在风险。

 快速开始

前提条件

· Python 3.7 或更高版本
· Git（可选，用于版本控制）

安装方法

方法一：从源码安装（推荐）

```bash
# 克隆仓库
git clone https://github.com/zm483/DepScan.git
cd DepScan

# 安装依赖
pip install -r requirements.txt

# 以开发模式安装
pip install -e .
```

方法二：从PyPI安装（未来发布后）

```bash
pip install depscan
```

 配置指南

1. GitHub API令牌配置（关键步骤）

由于GitHub对未认证API调用有严格限制（60次/小时），强烈建议配置个人访问令牌以获得5000次/小时的限额。

获取令牌步骤：

1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 备注名：填写 DepScan-API-Token
4. 权限：只需勾选  public_repo（访问公开仓库）
5. 点击 "Generate token"
6. 立即复制生成的令牌（格式为 ghp_xxxxxxxxxxxx）

使用令牌的三种方式：

方式一：命令行参数（最安全，推荐）

```bash
depscan https://github.com/python/cpython --token=ghp_ 令牌
# 或简写
depscan https://github.com/python/cpython -t ghp_ 令牌
```

方式二：环境变量（一次设置，多次使用）

```bash
# Windows (PowerShell)
$env:GITHUB_TOKEN="ghp_ 令牌"

# Windows (CMD)
set GITHUB_TOKEN=ghp_ 令牌

# Linux/Mac
export GITHUB_TOKEN="ghp_ 令牌"

# 设置后直接使用
depscan https://github.com/python/cpython
```

方式三：配置文件（持久化存储）
在项目根目录创建 .env 文件：

```env
GITHUB_TOKEN=ghp_ 令牌
```

然后安装python-dotenv并在代码中加载（高级用法）

2. 项目结构配置

确保 项目遵循以下结构：

```
DepScan/
├── depscan/              # 核心代码
│   ├── __init__.py
│   ├── cli.py           # 命令行入口
│   ├── collector.py     # 数据收集
│   └── analyzer.py      # 风险分析
├── docs/                # 文档
│   └── DepScan_Project_Slides.pdf
├── tests/               # 测试文件
├── requirements.txt     # 依赖列表
├── setup.py            # 安装配置
└── README.md           # 项目说明
```

 使用方法

基本扫描

```bash
# 完整风险分析
depscan https://github.com/用户名/仓库名

# 仅获取基础信息（快速）
depscan https://github.com/用户名/仓库名 --simple
```

实用示例

```bash
# 扫描Python官方仓库（完整分析）
depscan https://github.com/python/cpython -t ghp_ 令牌

# 扫描示例仓库（快速查看）
depscan https://github.com/octocat/Spoon-Knife --simple

# 查看帮助信息
depscan --help
```

输出示例

```
 开始扫描仓库: https://github.com/python/cpython
 成功连接仓库: python/cpython
 正在分析风险指标...

 项目概览
python/cpython
最后推送: 2023-10-24 | 未关闭Issue: 8296

 关键指标
┌─────────────────┬─────────┬─────────────────────────┐
│ 指标           │ 值      │ 说明                    │
├─────────────────┼─────────┼─────────────────────────┤
│ 巴士因子       │ 12      │ 值越低，维护越集中      │
│ 核心贡献者     │ user1, user2... │ 主要代码贡献者     │
│ 近期提交       │ 156     │ 近3个月提交数           │
│ 活跃度变化     │ +15.3%  │ 与3-6个月前相比         │
│ Issue响应时间  │ 8.5天   │ 平均关闭时间            │
└─────────────────┴─────────┴─────────────────────────┘
 未发现明显风险
```

 开发配置

虚拟环境设置

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# 安装开发依赖
pip install -r requirements.txt
pip install -e .
```

依赖管理

requirements.txt 内容：

```
PyGithub>=2.0.0
click>=8.0.0
rich>=10.0.0
python-dotenv>=1.0.0  # 可选，用于环境变量管理
```

 故障排除

常见问题

Q1: 出现 "rate limit exceeded" 错误

```
原因：GitHub API调用超限
解决：配置GitHub个人访问令牌（见上文）
```

Q2: 扫描速度很慢

```
原因：仓库数据量大或网络延迟
解决：
1. 使用 --simple 模式快速查看
2. 确保使用令牌提高API限额
3. 网络问题可尝试重试
```

Q3: 无法安装依赖

```
原因：Python版本不兼容或网络问题
解决：
1. 确认Python版本 ≥ 3.7: python --version
2. 使用国内镜像源：
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

Q4: 命令找不到

```
原因：未正确安装或虚拟环境未激活
解决：
1. 确保在虚拟环境中：检查提示符是否有 (.venv)
2. 重新安装：pip install -e .
3. 检查PATH：which depscan 或 where depscan
```

错误代码参考

错误码 含义 解决方案
403 API限额超限 配置GitHub令牌
404 仓库不存在 检查URL是否正确
401 令牌无效 重新生成令牌
500 GitHub服务器错误 稍后重试

 高级功能

自定义分析参数

可通过修改 depscan/analyzer.py 调整：

· calculate_activity_trend(months=6)：调整分析时间范围
· calculate_bus_factor(threshold=0.5)：调整巴士因子阈值
· calculate_issue_response_time(days=90)：调整Issue分析范围

扩展新指标

1. 在 analyzer.py 中添加新的计算方法
2. 在 generate_risk_report() 中集成新指标
3. 在 cli.py 的 print_risk_report() 中展示结果

 参与贡献

欢迎提交Issue和Pull Request！

1. Fork 本仓库
2. 创建功能分支：git checkout -b feature/new-feature
3. 提交更改：git commit -m 'Add some feature'
4. 推送到分支：git push origin feature/new-feature
5. 提交Pull Request
 
