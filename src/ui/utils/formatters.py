"""Formatting utilities for UI display."""
from typing import List, Dict
from ...models.ranking import CountryRanking, GlobalRankings


def format_country_detail(ranking: CountryRanking) -> str:
    """Format detailed country ranking information.
    
    Args:
        ranking: Country ranking object
        
    Returns:
        Formatted string for display
    """
    output = []
    
    # Header
    output.append(f"## {ranking.country_name} ({ranking.country_code})")
    output.append(f"**Period:** {ranking.period}")
    output.append(f"**Overall Score:** {ranking.overall_score:.2f}/10")
    output.append(f"**Global Rank:** #{ranking.rank}")
    output.append("")
    
    # Subcategory scores
    output.append("### Subcategory Breakdown:")
    for sc in ranking.subcategory_scores:
        # Add emoji indicators
        if sc.score >= 8:
            emoji = "✅"
        elif sc.score >= 6:
            emoji = "⚠️"
        else:
            emoji = "❌"
        output.append(f"{emoji} **{sc.subcategory_name}:** {sc.score:.1f}/10")
    output.append("")
    
    # Strengths
    if ranking.key_strengths:
        output.append("### Key Strengths:")
        for strength in ranking.key_strengths:
            output.append(f"- {strength}")
        output.append("")
    
    # Weaknesses
    if ranking.key_weaknesses:
        output.append("### Key Weaknesses:")
        for weakness in ranking.key_weaknesses:
            output.append(f"- {weakness}")
        output.append("")
    
    # Flagged issues
    if ranking.flagged_issues:
        output.append("### ⚠️ Issues Requiring Expert Review:")
        for issue in ranking.flagged_issues:
            output.append(f"- {issue}")
    
    return "\n".join(output)


def format_rankings_table(rankings: GlobalRankings, top_n: int = 10) -> str:
    """Format rankings as a markdown table.
    
    Args:
        rankings: Global rankings object
        top_n: Number of top countries to show
        
    Returns:
        Formatted markdown table
    """
    output = []
    output.append(f"## Global Renewable Market Rankings - {rankings.period}")
    output.append(f"*Generated: {rankings.generated_at.strftime('%Y-%m-%d %H:%M')}*")
    output.append("")
    
    # Table header
    output.append("| Rank | Country | Score | Key Strength |")
    output.append("|------|---------|-------|--------------|")
    
    # Table rows
    for ranking in rankings.get_top_n(top_n):
        strength = ranking.key_strengths[0] if ranking.key_strengths else "-"
        output.append(
            f"| #{ranking.rank} | {ranking.country_name} | "
            f"{ranking.overall_score:.2f}/10 | {strength} |"
        )
    
    output.append("")
    output.append(f"*Showing top {top_n} of {rankings.total_countries} countries*")
    
    return "\n".join(output)


def format_comparison(countries: List[CountryRanking]) -> str:
    """Format comparison between multiple countries.
    
    Args:
        countries: List of country rankings to compare
        
    Returns:
        Formatted comparison table
    """
    if not countries:
        return "No countries to compare."
    
    output = []
    output.append(f"## Comparison: {', '.join([c.country_name for c in countries])}")
    output.append("")
    
    # Overall scores
    output.append("### Overall Scores:")
    output.append("| Country | Score | Rank |")
    output.append("|---------|-------|------|")
    for country in countries:
        output.append(
            f"| {country.country_name} | {country.overall_score:.2f}/10 | #{country.rank} |"
        )
    output.append("")
    
    # Subcategory comparison
    output.append("### Subcategory Comparison:")
    
    # Get all subcategory names
    if countries[0].subcategory_scores:
        subcategories = [sc.subcategory_name for sc in countries[0].subcategory_scores]
        
        # Create header
        header = "| Subcategory | " + " | ".join([c.country_name for c in countries]) + " |"
        separator = "|-------------|" + "|".join(["------" for _ in countries]) + "|"
        output.append(header)
        output.append(separator)
        
        # Add rows
        for subcat in subcategories:
            row = f"| {subcat} |"
            for country in countries:
                score = country.get_subcategory_score(subcat)
                if score:
                    row += f" {score:.1f} |"
                else:
                    row += " - |"
            output.append(row)
    
    return "\n".join(output)


def format_chat_response(message: str, data: Dict = None) -> str:
    """Format a chat response with optional data.
    
    Args:
        message: Response message
        data: Optional data to include
        
    Returns:
        Formatted response
    """
    output = [message]
    
    if data:
        output.append("")
        output.append("---")
        for key, value in data.items():
            output.append(f"**{key}:** {value}")
    
    return "\n".join(output)
