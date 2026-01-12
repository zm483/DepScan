# depscan/analyzer.py
from datetime import datetime, timedelta
from collections import Counter


class RiskAnalyzer:
    """风险分析引擎"""

    def __init__(self, repo):
        """
        初始化分析器
        :param repo: PyGithub的Repository对象
        """
        self.repo = repo
        self._commits = None
        self._contributors = None

    def _get_commits(self):
        """获取提交列表（缓存）"""
        if self._commits is None:
            # 获取最近100条提交，对于初步分析足够
            self._commits = list(self.repo.get_commits()[:100])
        return self._commits

    def _get_contributors(self):
        """获取贡献者统计（缓存）"""
        if self._contributors is None:
            contributors = self.repo.get_stats_contributors()
            if contributors:
                # 转换为列表，按提交数排序
                self._contributors = sorted(
                    [(c.author.login, c.total) for c in contributors if c.author],
                    key=lambda x: x[1],
                    reverse=True
                )
            else:
                self._contributors = []
        return self._contributors

    def calculate_bus_factor(self, threshold=0.5):
        """
        计算巴士因子
        :param threshold: 关键知识阈值，默认50%
        :return: (巴士因子, 主要贡献者列表)
        """
        contributors = self._get_contributors()
        if not contributors:
            return 0, []

        total_commits = sum(c[1] for c in contributors)
        target_commits = total_commits * threshold

        accumulated = 0
        bus_factor = 0
        core_contributors = []

        for contributor, commits in contributors:
            accumulated += commits
            bus_factor += 1
            core_contributors.append(contributor)
            if accumulated >= target_commits:
                break

        return bus_factor, core_contributors

    def calculate_activity_trend(self, months=6):
        """
        计算活跃度趋势
        :param months: 分析的时间范围（月）
        :return: (近期提交数, 前期提交数, 变化率)
        """
        commits = self._get_commits()
        if not commits:
            return 0, 0, 0.0

        now = datetime.now()
        cutoff_recent = now - timedelta(days=30 * months // 2)  # 最近3个月
        cutoff_previous = now - timedelta(days=30 * months)  # 前3-6个月

        recent_count = 0
        previous_count = 0

        for commit in commits:
            commit_date = commit.commit.author.date
            if commit_date > cutoff_recent:
                recent_count += 1
            elif cutoff_previous < commit_date <= cutoff_recent:
                previous_count += 1
            else:
                break  # 提交是按时间倒序的

        # 计算变化率
        if previous_count > 0:
            change_rate = (recent_count - previous_count) / previous_count
        else:
            change_rate = 1.0 if recent_count > 0 else 0.0

        return recent_count, previous_count, change_rate

    def calculate_issue_response_time(self, days=90):
        """
        估算Issue平均响应时间
        :param days: 分析的时间范围（天）
        :return: 平均关闭天数（仅统计已关闭的Issue）
        """
        issues = list(self.repo.get_issues(state='closed')[:50])
        if not issues:
            return None

        total_days = 0
        count = 0
        cutoff = datetime.now() - timedelta(days=days)

        for issue in issues:
            if issue.created_at < cutoff:
                continue
            if issue.closed_at:
                days_to_close = (issue.closed_at - issue.created_at).days
                if days_to_close > 0:
                    total_days += days_to_close
                    count += 1

        return total_days / count if count > 0 else None

    def generate_risk_report(self):
        """生成完整风险报告"""
        report = {
            "basic_info": {
                "name": self.repo.full_name,
                "last_pushed": self.repo.pushed_at.strftime("%Y-%m-%d"),
                "open_issues": self.repo.open_issues_count,
            },
            "metrics": {},
            "risks": []
        }

        # 1. 计算巴士因子
        bus_factor, core_contributors = self.calculate_bus_factor()
        report["metrics"]["bus_factor"] = bus_factor
        report["metrics"]["core_contributors"] = core_contributors[:5]  # 只显示前5

        # 风险评估：巴士因子
        if bus_factor <= 1:
            report["risks"].append({
                "level": "高危",
                "type": "维护集中",
                "description": f"项目极度依赖个人（巴士因子={bus_factor}）",
                "suggestion": "建议考察是否有活跃的贡献者社区"
            })
        elif bus_factor <= 2:
            report["risks"].append({
                "level": "中危",
                "type": "维护集中",
                "description": f"项目主要依赖{bus_factor}名核心贡献者",
                "suggestion": "建议鼓励更广泛的代码审查和贡献"
            })

        # 2. 计算活跃度趋势
        recent, previous, change_rate = self.calculate_activity_trend()
        report["metrics"]["recent_commits"] = recent
        report["metrics"]["previous_commits"] = previous
        report["metrics"]["activity_change"] = f"{change_rate:.1%}"

        # 风险评估：活跃度下降
        if change_rate < -0.5:  # 下降超过50%
            report["risks"].append({
                "level": "高危",
                "type": "活跃度下降",
                "description": f"近期开发活跃度显著下降（{change_rate:.1%}）",
                "suggestion": "项目可能正在失去维护动力，请谨慎评估"
            })
        elif change_rate < -0.2:  # 下降20%-50%
            report["risks"].append({
                "level": "中危",
                "type": "活跃度下降",
                "description": f"开发活跃度有所下降（{change_rate:.1%}）",
                "suggestion": "建议关注后续更新情况"
            })

        # 3. Issue响应时间
        avg_response = self.calculate_issue_response_time()
        if avg_response:
            report["metrics"]["avg_issue_response_days"] = round(avg_response, 1)
            if avg_response > 30:
                report["risks"].append({
                    "level": "中危",
                    "type": "社区响应慢",
                    "description": f"Issue平均解决时间较长（{avg_response:.1f}天）",
                    "suggestion": "社区响应可能不够及时，问题解决周期长"
                })

        return report