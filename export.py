from datetime import datetime
from typing import Dict
from typing import List

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.columns import Columns
    from rich.text import Text
    from rich.align import Align
    from rich.layout import Layout

    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    print("❌ Rich library not found. Please install: pip install rich")
    sys.exit(1)

BATTALION_PRIORITY_ORDER = ["CONDOR", "YAGUARETE", "CARPINCHO"]

MEDAL_CONFIG = {
    "gold": {"icon": "🥇", "name": "Gold"},
    "silver": {"icon": "🥈", "name": "Silver"},
    "bronze": {"icon": "🥉", "name": "Bronze"},
}

BATTALION_CONFIG = {
    "CONDOR": {
        "icon": "🦅",
        "color": "bright_red",
        "header_color": "bright_white on bright_red",
    },
    "YAGUARETE": {
        "icon": "🐆",
        "color": "bright_yellow",
        "header_color": "black on bright_yellow",
    },
    "CARPINCHO": {
        "icon": "🦫",
        "color": "bright_green",
        "header_color": "black on bright_green",
    },
}


def export_summary_report(
    users, battalion_assignments, user_data, country_total_damage, active_population, country_name, format_type="html"
):
    """Export only summary of battalions"""
    export_console = Console(record=True, width=100)

    battalions_data = {}
    assigned_damage = 0
    unassigned_users_found = 0

    for user in users:
        battalion = assign_battalion(user['name'], battalion_assignments)
        if battalion == "UNASSIGNED":
            unassigned_users_found += 1
        else:
            if battalion not in battalions_data:
                battalions_data[battalion] = {'total_damage': 0, 'soldier_count': 0, 'soldiers': []}
            battalions_data[battalion]['total_damage'] += user['weeklyDamage']
            battalions_data[battalion]['soldier_count'] += 1
            assigned_damage += user['weeklyDamage']

    unassigned_damage = country_total_damage - assigned_damage

    # Create summary panel
    summary_panel = create_compact_summary_panel(
        battalions_data, country_total_damage, unassigned_damage, unassigned_users_found, active_population
    )

    export_console.print(summary_panel)

    filename = f"{country_name}_{get_current_week()}_summary_report.{format_type}"
    if format_type == "html":
        export_console.save_html(filename)
    elif format_type == "svg":
        export_console.save_svg(filename)
    elif format_type == "text":
        export_console.save_text(filename)
    else:
        console.print(f"[red]❌ Unsupported format: {format_type}[/red]")
        return

    console.print(f"[green]✅ Summary report exported to {filename}[/green]")


def assign_battalion(username: str, battalion_assignments: Dict[str, str]) -> str:
    """Assigns a battalion to a user"""
    username_lower = username.lower()

    if username_lower in battalion_assignments and battalion_assignments[username_lower]:
        assigned_battalion = battalion_assignments[username_lower]
        if assigned_battalion in ["CONDOR", "YAGUARETE", "CARPINCHO"]:
            return assigned_battalion

    return "UNASSIGNED"


def export_single_battalion_report(
    battalion_name,
    users,
    battalion_assignments,
    user_data,
    country_total_damage,
    active_population,
    country_name,
    format_type="html",
):
    """Export only one battalion's report"""
    export_console = Console(record=True, width=100)

    battalion_users = [
        user for user in users if assign_battalion(user['name'], battalion_assignments) == battalion_name
    ]

    if not battalion_users:
        console.print(f"[yellow]⚠ No users found for battalion: {battalion_name}[/yellow]")
        return

    table = create_battalion_table(battalion_name, battalion_users, user_data)
    header_text = f"{battalion_name} BATTALION REPORT - {get_current_week()}"
    header_panel = Panel(header_text, style="bold white on dark_blue")

    export_console.print(header_panel)
    export_console.print(table)

    filename = f"{country_name}_{get_current_week()}_{battalion_name.lower()}_report.{format_type}"
    if format_type == "html":
        export_console.save_html(filename)
    elif format_type == "svg":
        export_console.save_svg(filename)
    elif format_type == "text":
        export_console.save_text(filename)
    else:
        console.print(f"[red]❌ Unsupported format: {format_type}[/red]")
        return

    console.print(f"[green]✅ {battalion_name} report exported to {filename}[/green]")


def create_battalion_table(battalion_name, users_in_battalion, user_data, battalion_rank=1):
    """Creates a rich table for a specific battalion"""
    config = BATTALION_CONFIG[battalion_name]

    # Create table with battalion styling
    table = Table(
        title=f"{config['icon']} Battalion {battalion_name}",
        title_style=config['header_color'],
        border_style=config['color'],
        header_style=config['header_color'],
        show_lines=True,
    )

    # Add columns with better widths
    table.add_column("Rank", style="bold cyan", width=6, justify="center")
    table.add_column("Soldier", style="bold white", min_width=20)
    table.add_column("Level", style="yellow", width=8, justify="center")
    table.add_column("Weekly Damage", style="green", width=12, justify="right")
    table.add_column("Global Rank", style="blue", width=12, justify="center")
    table.add_column("Medals", style="gold1", width=8, justify="center")

    # Sort users by damage
    sorted_users = sorted(users_in_battalion, key=lambda x: x['weeklyDamage'], reverse=True)

    # Add rows
    for i, user in enumerate(sorted_users, 1):
        # Just show the level number
        level_display = str(user['level'])

        # Get user medals from user data
        username_lower = user['name'].lower()
        user_medals = {}
        if username_lower in user_data and isinstance(user_data[username_lower], dict):
            user_medals = user_data[username_lower].get("medals", {})

        medal_display = get_medal_display(user_medals)

        table.add_row(
            f"#{i}",
            f"{user['name']}",
            level_display,
            f"{format_damage(user['weeklyDamage'])}",
            f"#{user['weeklyRankingPosition']}",
            medal_display,
        )

    # Add battalion stats footer
    total_damage = sum(user['weeklyDamage'] for user in users_in_battalion)
    avg_damage = total_damage // len(users_in_battalion) if users_in_battalion else 0
    avg_level = (
        sum(user['level'] for user in users_in_battalion) // len(users_in_battalion) if users_in_battalion else 0
    )

    table.add_section()
    table.add_row(
        "[bold]STATS[/bold]",
        f"[bold]{len(users_in_battalion)} soldiers[/bold]",
        f"[bold]Avg: {avg_level}[/bold]",
        f"[bold]{format_damage(total_damage)}[/bold]",
        f"[bold]Avg: {format_damage(avg_damage)}[/bold]",
        "",  # Empty cell instead of description
    )

    return table


def get_medal_display(user_medals):
    """Returns medal display string for a user"""
    if not user_medals:
        return ""

    medal_counts = {"gold": 0, "silver": 0, "bronze": 0}

    for week, medal_type in user_medals.items():
        if medal_type in medal_counts:
            medal_counts[medal_type] += 1

    display_parts = []
    for medal_type, count in medal_counts.items():
        if count > 0:
            icon = MEDAL_CONFIG[medal_type]["icon"]
            if count > 1:
                display_parts.append(f"{icon}x{count}")
            else:
                display_parts.append(icon)

    return " ".join(display_parts)


def format_damage(damage):
    """Formats damage with thousands separators"""
    return f"{int(damage):,}"


def get_current_week():
    """Returns current week number in format 'week_N'"""
    current_date = datetime.now()
    week_number = current_date.isocalendar()[1]
    year = current_date.year
    return f"week_{year}_{week_number}"


def create_compact_summary_panel(
    battalions_data, country_total_damage, unassigned_damage, unassigned_users_found, active_population
):
    """Creates a compact summary panel with better width management"""

    # Create main summary table with smaller widths
    summary_table = Table(
        title="BATTALION SUMMARY",
        title_style="black on bright_blue",
        border_style="blue",
        header_style="black on bright_blue",
        show_lines=True,
    )

    summary_table.add_column("Battalion", style="bold", width=12)
    summary_table.add_column("Icon", width=6, justify="center")
    summary_table.add_column("Soldiers", style="cyan", width=10, justify="center")
    summary_table.add_column("Total Damage", style="green", width=16, justify="right")
    summary_table.add_column("Percentage", style="yellow", width=10, justify="center")
    summary_table.add_column("Avg/Soldier", style="magenta", width=16, justify="right")

    # Add battalion rows
    for battalion_name in BATTALION_PRIORITY_ORDER:
        if battalion_name in battalions_data:
            data = battalions_data[battalion_name]
            config = BATTALION_CONFIG[battalion_name]

            total_damage = data['total_damage']
            soldier_count = data['soldier_count']
            percentage = (total_damage / country_total_damage) * 100
            avg_damage = total_damage // soldier_count if soldier_count > 0 else 0

            summary_table.add_row(
                battalion_name,
                config['icon'],
                str(soldier_count),
                format_damage(total_damage),
                f"{percentage:.1f}%",
                format_damage(avg_damage),
            )

    # Add unassigned row
    if unassigned_damage > 0:
        # Calculate unassigned population and average
        assigned_population = sum(data['soldier_count'] for data in battalions_data.values())
        unassigned_population = active_population - assigned_population
        unassigned_avg = unassigned_damage // unassigned_population if unassigned_population > 0 else 0

        percentage = (unassigned_damage / country_total_damage) * 100
        summary_table.add_row(
            "UNASSIGNED",
            "❓",
            f"{unassigned_population:,}",
            format_damage(unassigned_damage),
            f"{percentage:.1f}%",
            format_damage(unassigned_avg),
        )

    # Add total row with real country average
    country_avg_per_soldier = country_total_damage // active_population if active_population > 0 else 0
    summary_table.add_section()
    summary_table.add_row(
        "[bold]TOTAL[/bold]",
        "🏴",
        f"[bold]{active_population:,}[/bold]",
        f"[bold]{format_damage(country_total_damage)}[/bold]",
        "[bold]100.0%[/bold]",
        f"[bold]{format_damage(country_avg_per_soldier)}[/bold]",
    )

    return Panel.fit(summary_table, title="STRATEGIC OVERVIEW", border_style="gold1", padding=(1, 1))
