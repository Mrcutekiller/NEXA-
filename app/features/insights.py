# app/features/insights.py
"""
Weekly Insights & Analytics.
Generates performance reports and renders topic distributions as ASCII bar charts.
"""

from typing import Dict, Any

class InsightsManager:
    def __init__(self, stats_manager=None):
        self.stats_manager = stats_manager

    def generate_report(self) -> str:
        """
        Creates a structured, styled text-based analytics report.
        """
        if not self.stats_manager:
            return "Analytics subsystem offline: no stats manager connected."

        stats = self.stats_manager.stats
        total_xp = stats.get("total_xp", 0)
        level = stats.get("level", 1)
        level_name = stats.get("level_name", "Greenhorn")
        streak = stats.get("streak", 0)
        message_count = stats.get("message_count", 0)
        challenges = stats.get("challenges_completed_count", 0)
        
        # Calculate progress
        earned, total, percent = self.stats_manager.get_progress_to_next()
        progress_bar_length = 20
        filled = int(percent * progress_bar_length)
        xp_bar = "█" * filled + "░" * (progress_bar_length - filled)

        # Topic breakdown bar chart
        breakdown = stats.get("topic_breakdown", {
            "coding": 0,
            "design": 0,
            "debugging": 0,
            "general": 0
        })
        
        total_topics = sum(breakdown.values())
        chart_lines = []
        bar_length = 15
        
        for topic, count in breakdown.items():
            percentage = (count / total_topics * 100) if total_topics > 0 else 0
            filled_bars = int((percentage / 100) * bar_length)
            bar = "█" * filled_bars + "░" * (bar_length - filled_bars)
            chart_lines.append(f"  {topic.capitalize():10} [{bar}] {percentage:.1f}% ({count})")
            
        chart_str = "\n".join(chart_lines)

        report = f"""
\033[1;33m👑 NEXA WEEKLY INSIGHTS & ANALYTICS REPORT 👑\033[0m
==================================================
\033[1mActive User Level:\033[0m {level} ({level_name})
\033[1mTotal Experience:\033[0m {total_xp} XP
\033[1mLevel Progress:\033[0m   [{xp_bar}] {percent*100:.1f}% ({earned}/{total} XP)
\033[1mUsage Streak:\033[0m     {streak} days active
\033[1mMessages Logged:\033[0m  {message_count}
\033[1mChallenges Solved:\033[0m {challenges}

\033[1;36m📊 Topics & Skills Distribution Chart:\033[0m
--------------------------------------------------
{chart_str}
==================================================
        """
        return report.strip()
