"""Report Formatter Service for CreditNexus.

Provides formatting utilities for agent reports in various formats (Markdown, PDF, JSON).
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class ReportFormatter:
    """
    Service for formatting agent reports.
    
    Provides:
    - Markdown formatting for agent results
    - Structured report generation
    - Format-specific rendering
    """
    
    def format_agent_report_markdown(
        self,
        agent_type: str,
        agent_result: Dict[str, Any]
    ) -> str:
        """
        Format agent report as Markdown.
        
        Args:
            agent_type: Type of agent ('deepresearch', 'langalpha', 'peoplehub')
            agent_result: Agent result data
            
        Returns:
            Formatted Markdown string
        """
        if agent_type == 'deepresearch':
            return self._format_deepresearch_markdown(agent_result)
        elif agent_type == 'langalpha':
            return self._format_langalpha_markdown(agent_result)
        elif agent_type == 'peoplehub':
            return self._format_peoplehub_markdown(agent_result)
        else:
            return self._format_generic_markdown(agent_type, agent_result)
    
    def _format_deepresearch_markdown(self, result: Dict[str, Any]) -> str:
        """Format DeepResearch result as Markdown."""
        lines = []
        lines.append("# DeepResearch Report")
        lines.append("")
        lines.append(f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
        lines.append("")
        
        # Answer
        if result.get('answer'):
            lines.append("## Answer")
            lines.append("")
            lines.append(result['answer'])
            lines.append("")
        
        # Knowledge Items
        if result.get('knowledge_items'):
            lines.append("## Knowledge Items")
            lines.append("")
            for idx, item in enumerate(result['knowledge_items'][:10], 1):  # Limit to 10
                lines.append(f"### {idx}. {item.get('title', 'Untitled')}")
                lines.append("")
                if item.get('content'):
                    content = item['content'][:500] + "..." if len(item.get('content', '')) > 500 else item.get('content', '')
                    lines.append(content)
                    lines.append("")
                if item.get('url'):
                    lines.append(f"**Source:** [{item['url']}]({item['url']})")
                    lines.append("")
        
        # Visited URLs
        if result.get('visited_urls'):
            lines.append("## Sources")
            lines.append("")
            for url in result['visited_urls'][:20]:  # Limit to 20
                lines.append(f"- [{url}]({url})")
            lines.append("")
        
        # Search Queries
        if result.get('search_queries'):
            lines.append("## Search Queries")
            lines.append("")
            for query in result['search_queries'][:10]:  # Limit to 10
                lines.append(f"- `{query}`")
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_langalpha_markdown(self, result: Dict[str, Any]) -> str:
        """Format LangAlpha result as Markdown."""
        lines = []
        lines.append("# LangAlpha Quantitative Analysis Report")
        lines.append("")
        lines.append(f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
        lines.append("")
        
        # Extract structured report if available
        report = result.get('report', {})
        structured = report.get('structured_report', {}) if isinstance(report, dict) else {}
        
        # Executive Summary
        if structured.get('executive_summary'):
            lines.append("## Executive Summary")
            lines.append("")
            lines.append(structured['executive_summary'])
            lines.append("")
        
        # Key Findings
        if structured.get('key_findings'):
            lines.append("## Key Findings")
            lines.append("")
            for finding in structured['key_findings']:
                lines.append(f"- {finding}")
            lines.append("")
        
        # Metrics
        if structured.get('metrics'):
            lines.append("## Metrics")
            lines.append("")
            
            # Market Metrics
            if structured['metrics'].get('market_metrics'):
                lines.append("### Market Metrics")
                lines.append("")
                market = structured['metrics']['market_metrics']
                if isinstance(market, dict):
                    for key, value in market.items():
                        lines.append(f"- **{key}:** {value}")
                lines.append("")
            
            # Fundamental Metrics
            if structured['metrics'].get('fundamental_metrics'):
                lines.append("### Fundamental Metrics")
                lines.append("")
                fundamental = structured['metrics']['fundamental_metrics']
                if isinstance(fundamental, dict):
                    for key, value in fundamental.items():
                        lines.append(f"- **{key}:** {value}")
                lines.append("")
        
        # Recommendations
        if structured.get('recommendations'):
            lines.append("## Recommendations")
            lines.append("")
            for rec in structured['recommendations']:
                lines.append(f"- {rec}")
            lines.append("")
        
        # Risk Assessment
        if structured.get('risk_assessment'):
            lines.append("## Risk Assessment")
            lines.append("")
            risk = structured['risk_assessment']
            if isinstance(risk, dict):
                for key, value in risk.items():
                    lines.append(f"- **{key}:** {value}")
            lines.append("")
        
        # Raw Report
        if report.get('report'):
            lines.append("## Full Report")
            lines.append("")
            lines.append(report['report'])
            lines.append("")
        
        # Market Data
        if result.get('market_data'):
            lines.append("## Market Data")
            lines.append("")
            lines.append("```json")
            import json
            lines.append(json.dumps(result['market_data'], indent=2))
            lines.append("```")
            lines.append("")
        
        # Fundamental Data
        if result.get('fundamental_data'):
            lines.append("## Fundamental Data")
            lines.append("")
            lines.append("```json")
            import json
            lines.append(json.dumps(result['fundamental_data'], indent=2))
            lines.append("```")
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_peoplehub_markdown(self, result: Dict[str, Any]) -> str:
        """Format PeopleHub result as Markdown."""
        lines = []
        lines.append("# PeopleHub Research Report")
        lines.append("")
        lines.append(f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
        lines.append("")
        
        # Person Name
        if result.get('person_name'):
            lines.append(f"## {result['person_name']}")
            lines.append("")
        
        # Profile Data
        profile_data = result.get('profile_data', {})
        if isinstance(profile_data, dict):
            # Research Report
            if profile_data.get('research_report'):
                lines.append("## Research Summary")
                lines.append("")
                lines.append(profile_data['research_report'])
                lines.append("")
            
            # Psychometric Profile
            if profile_data.get('psychometric_profile'):
                lines.append("## Psychometric Profile")
                lines.append("")
                psych = profile_data['psychometric_profile']
                if isinstance(psych, dict):
                    for key, value in psych.items():
                        lines.append(f"- **{key}:** {value}")
                lines.append("")
            
            # Credit Checks
            if profile_data.get('credit_checks'):
                lines.append("## Credit Checks")
                lines.append("")
                checks = profile_data['credit_checks']
                if isinstance(checks, list):
                    for check in checks:
                        if isinstance(check, dict):
                            lines.append(f"- **{check.get('type', 'Unknown')}:** {check.get('status', 'N/A')}")
                lines.append("")
        
        # LinkedIn URL
        if result.get('linkedin_url'):
            lines.append(f"**LinkedIn:** [{result['linkedin_url']}]({result['linkedin_url']})")
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_generic_markdown(self, agent_type: str, result: Dict[str, Any]) -> str:
        """Format generic agent result as Markdown."""
        lines = []
        lines.append(f"# {agent_type.title()} Report")
        lines.append("")
        lines.append(f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
        lines.append("")
        lines.append("## Results")
        lines.append("")
        lines.append("```json")
        import json
        lines.append(json.dumps(result, indent=2))
        lines.append("```")
        lines.append("")
        
        return "\n".join(lines)
