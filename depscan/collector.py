# depscan/collector.py
from github import Github
from github.GithubException import GithubException


class ProjectCollector:
    """项目数据收集器"""

    def __init__(self, github_token=None):
        """
        初始化收集器
        :param github_token: 可选的GitHub个人访问令牌，用于提高API限额
        """
        # 如果有令牌就使用，否则匿名访问（限额较低）
        self.g = Github(github_token) if github_token else Github()
        self.repo = None  # 用于存储仓库对象

    def set_repository(self, repo_url):
        """
        解析并设置目标仓库
        :param repo_url: GitHub仓库的URL，如 'https://github.com/python/cpython'
        :raises: ValueError 或 RuntimeError 当URL无效或仓库不存在时
        """
        # 1. 从URL中提取 '用户名/仓库名'
        if 'github.com/' not in repo_url:
            raise ValueError("❌ 请输入有效的GitHub仓库URL。")
        # 例如从 'https://github.com/python/cpython' 提取出 'python/cpython'
        path = repo_url.split('github.com/')[-1].strip('/')
        if path.count('/') != 1:
            raise ValueError("❌ URL格式错误，应为：https://github.com/用户名/仓库名")

        # 2. 尝试连接GitHub获取仓库对象
        try:
            self.repo = self.g.get_repo(path)
            print(f"✅ 成功连接仓库: {self.repo.full_name}")
        except GithubException as e:
            # 如果出错，给出友好提示
            error_msg = e.data.get('message', '未知错误')
            raise RuntimeError(f"❌ 连接仓库失败: {error_msg}")

    def get_basic_info(self):
        """
        获取并返回仓库的基础信息
        :return: 包含基础信息的字典
        """
        if not self.repo:
            raise RuntimeError("❌ 请先使用 set_repository() 设置目标仓库。")

        return {
            "仓库全名": self.repo.full_name,
            "描述": self.repo.description or "(无描述)",
            "创建时间": self.repo.created_at.strftime("%Y-%m-%d"),
            "最后推送": self.repo.pushed_at.strftime("%Y-%m-%d %H:%M"),
            "Star数": self.repo.stargazers_count,
            "Fork数": self.repo.forks_count,
            "未关闭Issue": self.repo.open_issues_count,
            "许可证": self.repo.license.spdx_id if self.repo.license else "无",
        }

    # ... 你已有的 get_basic_info() 方法 ...

    def get_risk_report(self):
        """
        获取完整的风险分析报告
        需要先调用 set_repository() 设置仓库
        """
        if not self.repo:
            raise RuntimeError("请先使用 set_repository() 设置目标仓库。")

        # 导入分析器（注意：在方法内部导入，避免循环导入问题）
        from .analyzer import RiskAnalyzer

        analyzer = RiskAnalyzer(self.repo)
        return analyzer.generate_risk_report()


# 测试代码：当直接运行此文件时执行
if __name__ == "__main__":
    print("=== DepScan 数据收集器测试 ===\n")

    # 创建一个收集器实例
    collector = ProjectCollector()

    # 测试一个著名且稳定的仓库（GitHub官方Python解释器）
    test_url = "https://github.com/python/cpython"

    try:
        # 连接仓库
        collector.set_repository(test_url)
        # 获取信息
        info = collector.get_basic_info()

        # 打印漂亮的结果
        print("\n📊 仓库基础信息:")
        print("-" * 30)
        for key, value in info.items():
            print(f"{key:>10}: {value}")
        print("-" * 30)
        print("✅ 测试成功！数据收集器工作正常。")

    except Exception as e:
        print(f"❌ 测试失败: {e}")