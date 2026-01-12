# depscan/cli.py
import click
from .collector import ProjectCollector


def print_risk_report(report):
    """打印漂亮的风险报告"""
    try:
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        from rich import box

        console = Console()

        # 1. 基础信息面板
        info = report["basic_info"]
        console.print(Panel.fit(
            f"[bold cyan]{info['name']}[/bold cyan]\n"
            f"最后推送: [yellow]{info['last_pushed']}[/yellow] | "
            f"未关闭Issue: [yellow]{info['open_issues']}[/yellow]",
            title="📦 项目概览",
            border_style="cyan"
        ))

        # 2. 关键指标表格
        metrics = report["metrics"]
        metric_table = Table(title="📊 关键指标", box=box.SIMPLE)
        metric_table.add_column("指标", style="cyan")
        metric_table.add_column("值", style="white")
        metric_table.add_column("说明", style="dim")

        metric_data = [
            ("巴士因子", metrics.get("bus_factor", "N/A"), "值越低，维护越集中"),
            ("核心贡献者", ", ".join(metrics.get("core_contributors", []))[:50], "主要代码贡献者"),
            ("近期提交", metrics.get("recent_commits", "N/A"), "近3个月提交数"),
            ("活跃度变化", metrics.get("activity_change", "N/A"), "与3-6个月前相比"),
        ]

        if "avg_issue_response_days" in metrics:
            metric_data.append(
                ("Issue响应时间", f"{metrics['avg_issue_response_days']}天", "平均关闭时间")
            )

        for name, value, desc in metric_data:
            metric_table.add_row(name, str(value), desc)

        console.print(metric_table)

        # 3. 风险提示（重点！）
        risks = report["risks"]
        if risks:
            console.print("\n⚠️  [bold red]发现风险项[/bold red]")
            for i, risk in enumerate(risks, 1):
                color = "red" if risk["level"] == "高危" else "yellow"
                console.print(
                    f"[{color}]{i}. [{risk['level']}] {risk['type']}[/{color}]: "
                    f"{risk['description']}"
                )
                console.print(f"   💡 建议: {risk['suggestion']}")
        else:
            console.print("\n✅ [bold green]未发现明显风险[/bold green]")

    except ImportError:
        # 备用输出（如果rich不可用）
        click.echo("\n=== 风险分析报告 ===")
        click.echo(f"项目: {report['basic_info']['name']}")

        for key, value in report['metrics'].items():
            click.echo(f"{key}: {value}")

        if report['risks']:
            click.echo("\n⚠️ 风险提示:")
            for risk in report['risks']:
                click.echo(f"  [{risk['level']}] {risk['type']}: {risk['description']}")
                click.echo(f"     建议: {risk['suggestion']}")
        else:
            click.echo("\n✅ 未发现明显风险")


@click.command()
@click.argument('repo_url')
@click.option('--token', '-t', help='GitHub个人访问令牌 (可选)', default=None)
@click.option('--simple', '-s', is_flag=True, help='仅显示基础信息')
def scan(repo_url, token, simple):
    """
    扫描指定的GitHub仓库，评估其弃用风险。

    REPO_URL: GitHub仓库的完整URL，例如 https://github.com/username/repo
    """
    click.echo(f"🔍 开始扫描仓库: {repo_url}")

    try:
        collector = ProjectCollector(github_token=token)
        collector.set_repository(repo_url)

        if simple:
            # 简单模式：仅基础信息
            info = collector.get_basic_info()
            click.echo("\n=== 基础信息 ===")
            for key, value in info.items():
                click.echo(f"  {key}: {value}")
        else:
            # 完整模式：风险分析报告
            click.echo("⏳ 正在分析风险指标...")
            report = collector.get_risk_report()
            print_risk_report(report)

        click.echo("\n✅ 扫描完成！")

    except Exception as e:
        click.echo(f"❌ 扫描失败: {e}", err=True)


if __name__ == '__main__':
    scan()