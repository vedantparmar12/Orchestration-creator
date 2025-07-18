#!/usr/bin/env python3
"""
Demo UI Agent Creation System
Demonstrates creating a beautiful UI agent with pre-configured settings
"""

import asyncio
import sys
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.layout import Layout
from rich.live import Live
from rich.tree import Tree
from rich.align import Align
from rich.columns import Columns
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from src.utils.pydantic_ai_config import create_openrouter_model
from pydantic_ai import Agent
import json
import os
from dotenv import load_dotenv
from datetime import datetime
import time

# Load environment variables
load_dotenv()

console = Console()

class UIAgentDemo:
    """Demo UI Agent Creation System"""
    
    def __init__(self):
        self.console = Console()
        self.model = create_openrouter_model()
        
        # Create plain text agents (no structured output to avoid tool issues)
        self.agents = self._create_plain_agents()
    
    def _create_plain_agents(self) -> Dict[str, Agent]:
        """Create plain text agents"""
        return {
            'ui_designer': Agent(
                model=self.model,
                system_prompt="""You are a UI/UX design expert. Create beautiful, functional user interfaces. 
                Focus on modern design principles, color theory, typography, responsive layouts, and accessibility.
                Provide detailed design specifications in clear, readable format."""
            ),
            
            'frontend_developer': Agent(
                model=self.model,
                system_prompt="""You are a senior frontend developer. Create clean, semantic HTML, modern CSS,
                and JavaScript ES6+ code. Specialize in React, Vue, Angular frameworks with performance optimization
                and cross-browser compatibility. Provide production-ready, maintainable code."""
            ),
            
            'accessibility_expert': Agent(
                model=self.model,
                system_prompt="""You are an accessibility expert focused on inclusive design.
                Ensure WCAG 2.1 AA compliance, screen reader compatibility, keyboard navigation,
                color contrast optimization, semantic HTML, and ARIA attributes."""
            ),
            
            'interaction_designer': Agent(
                model=self.model,
                system_prompt="""You are an interaction design specialist. Create engaging micro-interactions,
                animations, user flow optimizations, gesture interactions, state management patterns,
                and progressive enhancement for intuitive user experiences."""
            )
        }
    
    def display_banner(self):
        """Display beautiful banner"""
        banner = Text("🎨 UI AGENT CREATOR DEMO", style="bold cyan")
        banner.append("\\nBeautiful Interface Generation System", style="dim")
        
        panel = Panel(
            banner,
            border_style="cyan",
            padding=(1, 2),
            title="✨ Advanced UI Generation Demo",
            title_align="center"
        )
        self.console.print(panel)
        self.console.print()
    
    def display_capabilities(self):
        """Display agent capabilities"""
        capabilities_table = Table(show_header=True, header_style="bold magenta")
        capabilities_table.add_column("🤖 Agent", style="cyan", width=20)
        capabilities_table.add_column("🎯 Specialization", style="white", width=30)
        capabilities_table.add_column("⚡ Key Skills", style="green", width=40)
        
        agents_info = [
            ("🎨 UI Designer", "Visual Design & UX", "Modern design, Typography, Color theory, Responsive layouts"),
            ("💻 Frontend Developer", "Code Implementation", "HTML/CSS/JS, React/Vue/Angular, Performance optimization"),
            ("♿ Accessibility Expert", "Inclusive Design", "WCAG compliance, Screen readers, Keyboard navigation"),
            ("🎭 Interaction Designer", "User Experience", "Animations, Micro-interactions, User flows")
        ]
        
        for agent_name, specialization, skills in agents_info:
            capabilities_table.add_row(agent_name, specialization, skills)
        
        self.console.print(Panel(
            capabilities_table,
            title="🚀 Available UI Agents",
            border_style="blue",
            padding=(1, 2)
        ))
        self.console.print()
    
    def get_demo_requirements(self) -> Dict[str, Any]:
        """Get demo requirements"""
        return {
            "ui_type": "dashboard",
            "title": "Modern Analytics Dashboard",
            "description": "A sleek, modern dashboard for data visualization and analytics",
            "framework": "react",
            "styling": "css",
            "color_scheme": "modern-blue",
            "include_animations": True,
            "include_responsive": True,
            "include_accessibility": True,
            "timestamp": datetime.now().isoformat()
        }
    
    async def generate_ui_with_progress(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Generate UI with beautiful progress display"""
        
        # Create progress layout
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="progress", size=8),
            Layout(name="status", size=5)
        )
        
        # Header
        header = Panel(
            Text(f"🎨 Generating: {requirements['title']}", style="bold cyan"),
            border_style="cyan"
        )
        
        # Progress tracking
        agents_progress = {
            "🎨 UI Designer": {"progress": 0, "status": "⏳ Waiting..."},
            "💻 Frontend Developer": {"progress": 0, "status": "⏳ Waiting..."},
            "♿ Accessibility Expert": {"progress": 0, "status": "⏳ Waiting..."},
            "🎭 Interaction Designer": {"progress": 0, "status": "⏳ Waiting..."}
        }
        
        results = {}
        
        with Live(layout, refresh_per_second=4, screen=True):
            layout["header"].update(header)
            
            # Step 1: UI Design
            agents_progress["🎨 UI Designer"]["status"] = "🔄 Designing..."
            self._update_progress_display(layout, agents_progress, "Creating visual design...")
            
            # Simulate progress
            for i in range(0, 101, 25):
                agents_progress["🎨 UI Designer"]["progress"] = i
                self._update_progress_display(layout, agents_progress, f"Design progress: {i}%")
                await asyncio.sleep(0.2)
            
            try:
                design_result = await self._run_ui_designer(requirements)
                agents_progress["🎨 UI Designer"]["status"] = "✅ Complete"
                results["design"] = design_result
            except Exception as e:
                agents_progress["🎨 UI Designer"]["status"] = f"❌ Error: {str(e)[:20]}..."
                results["design"] = f"Design generation failed: {str(e)}"
            
            # Step 2: Frontend Development
            agents_progress["💻 Frontend Developer"]["status"] = "🔄 Coding..."
            self._update_progress_display(layout, agents_progress, "Generating code...")
            
            for i in range(0, 101, 33):
                agents_progress["💻 Frontend Developer"]["progress"] = i
                self._update_progress_display(layout, agents_progress, f"Code generation: {i}%")
                await asyncio.sleep(0.2)
            
            try:
                code_result = await self._run_frontend_developer(requirements, results.get("design", ""))
                agents_progress["💻 Frontend Developer"]["status"] = "✅ Complete"
                results["code"] = code_result
            except Exception as e:
                agents_progress["💻 Frontend Developer"]["status"] = f"❌ Error: {str(e)[:20]}..."
                results["code"] = f"Code generation failed: {str(e)}"
            
            # Step 3: Accessibility
            agents_progress["♿ Accessibility Expert"]["status"] = "🔄 Optimizing..."
            self._update_progress_display(layout, agents_progress, "Adding accessibility features...")
            
            for i in range(0, 101, 50):
                agents_progress["♿ Accessibility Expert"]["progress"] = i
                self._update_progress_display(layout, agents_progress, f"Accessibility: {i}%")
                await asyncio.sleep(0.2)
            
            try:
                accessibility_result = await self._run_accessibility_expert(requirements, results.get("code", ""))
                agents_progress["♿ Accessibility Expert"]["status"] = "✅ Complete"
                results["accessibility"] = accessibility_result
            except Exception as e:
                agents_progress["♿ Accessibility Expert"]["status"] = f"❌ Error: {str(e)[:20]}..."
                results["accessibility"] = f"Accessibility enhancement failed: {str(e)}"
            
            # Step 4: Interactions
            agents_progress["🎭 Interaction Designer"]["status"] = "🔄 Animating..."
            self._update_progress_display(layout, agents_progress, "Adding interactions...")
            
            for i in range(0, 101, 25):
                agents_progress["🎭 Interaction Designer"]["progress"] = i
                self._update_progress_display(layout, agents_progress, f"Interactions: {i}%")
                await asyncio.sleep(0.2)
            
            try:
                interaction_result = await self._run_interaction_designer(requirements, results.get("code", ""))
                agents_progress["🎭 Interaction Designer"]["status"] = "✅ Complete"
                results["interactions"] = interaction_result
            except Exception as e:
                agents_progress["🎭 Interaction Designer"]["status"] = f"❌ Error: {str(e)[:20]}..."
                results["interactions"] = f"Interaction design failed: {str(e)}"
            
            # Final update
            self._update_progress_display(layout, agents_progress, "🎉 Generation complete!")
            
            # Small delay to show completion
            await asyncio.sleep(1)
        
        return {
            "requirements": requirements,
            **results,
            "generation_time": datetime.now().isoformat()
        }
    
    def _update_progress_display(self, layout, agents_progress, status_message):
        """Update progress display"""
        # Create progress table
        progress_table = Table(show_header=False, box=None, padding=(0, 1))
        progress_table.add_column("Agent", style="cyan", width=20)
        progress_table.add_column("Progress", width=40)
        progress_table.add_column("Status", style="green", width=20)
        
        for agent_name, info in agents_progress.items():
            progress_bar = "█" * (info["progress"] // 10) + "░" * (10 - info["progress"] // 10)
            progress_table.add_row(agent_name, f"[{progress_bar}] {info['progress']}%", info["status"])
        
        progress_panel = Panel(progress_table, title="Agent Progress", border_style="blue")
        layout["progress"].update(progress_panel)
        
        status_panel = Panel(Text(status_message, style="bold yellow"), border_style="yellow", title="Current Status")
        layout["status"].update(status_panel)
    
    async def _run_ui_designer(self, requirements: Dict[str, Any]) -> str:
        """Run UI designer agent"""
        prompt = f"""
        Create a comprehensive UI design specification for:
        - Type: {requirements['ui_type']}
        - Title: {requirements['title']}
        - Description: {requirements['description']}
        - Color scheme: {requirements['color_scheme']}
        - Responsive: {requirements['include_responsive']}
        
        Provide detailed design decisions, color palette, typography, layout structure, and component hierarchy.
        """
        
        result = await self.agents['ui_designer'].run(prompt)
        return result.data
    
    async def _run_frontend_developer(self, requirements: Dict[str, Any], design: str) -> str:
        """Run frontend developer agent"""
        prompt = f"""
        Based on this design specification:
        {design[:500]}...
        
        Generate complete frontend code for:
        - Framework: {requirements['framework']}
        - Styling: {requirements['styling']}
        - Type: {requirements['ui_type']}
        
        Include HTML, CSS, and JavaScript code with proper structure and best practices.
        """
        
        result = await self.agents['frontend_developer'].run(prompt)
        return result.data
    
    async def _run_accessibility_expert(self, requirements: Dict[str, Any], code: str) -> str:
        """Run accessibility expert agent"""
        prompt = f"""
        Review and enhance this code for accessibility:
        {code[:500]}...
        
        Add WCAG 2.1 AA compliance features, ARIA attributes, keyboard navigation, and screen reader support.
        """
        
        result = await self.agents['accessibility_expert'].run(prompt)
        return result.data
    
    async def _run_interaction_designer(self, requirements: Dict[str, Any], code: str) -> str:
        """Run interaction designer agent"""
        prompt = f"""
        Add beautiful interactions and animations to this UI:
        {code[:500]}...
        
        Include micro-interactions, hover effects, loading states, and smooth transitions.
        """
        
        result = await self.agents['interaction_designer'].run(prompt)
        return result.data
    
    def display_results(self, results: Dict[str, Any]):
        """Display beautiful results"""
        self.console.print("\\n" + "="*80)
        self.console.print("[bold green]🎉 UI GENERATION COMPLETE![/bold green]")
        self.console.print("="*80)
        
        # Requirements summary
        req_table = Table(show_header=False, box=None, padding=(0, 1))
        req_table.add_column("Property", style="cyan", width=20)
        req_table.add_column("Value", style="white", width=40)
        
        req = results["requirements"]
        req_table.add_row("📱 Type", req["ui_type"])
        req_table.add_row("🎨 Framework", req["framework"])
        req_table.add_row("🎭 Styling", req["styling"])
        req_table.add_row("🌈 Color Scheme", req["color_scheme"])
        req_table.add_row("📱 Responsive", "✅ Yes" if req["include_responsive"] else "❌ No")
        req_table.add_row("♿ Accessibility", "✅ Yes" if req["include_accessibility"] else "❌ No")
        req_table.add_row("🎪 Animations", "✅ Yes" if req["include_animations"] else "❌ No")
        
        self.console.print(Panel(
            req_table,
            title="📋 Generated UI Specifications",
            border_style="green"
        ))
        
        # Results sections
        sections = [
            ("🎨 Design Specification", results.get("design", "Not generated")),
            ("💻 Generated Code", results.get("code", "Not generated")),
            ("♿ Accessibility Features", results.get("accessibility", "Not generated")),
            ("🎭 Interactions & Animations", results.get("interactions", "Not generated"))
        ]
        
        for title, content in sections:
            self.console.print(f"\\n[bold cyan]{title}:[/bold cyan]")
            # Show first 300 chars of content
            if content and not content.startswith("failed"):
                preview = content[:300] + "..." if len(content) > 300 else content
                self.console.print(Panel(
                    preview,
                    border_style="blue",
                    padding=(1, 2)
                ))
            else:
                self.console.print(Panel(
                    content,
                    border_style="red",
                    padding=(1, 2)
                ))
        
        # Save demo results
        self.save_demo_results(results)
    
    def save_demo_results(self, results: Dict[str, Any]):
        """Save demo results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ui_agent_demo_{timestamp}.json"
        
        try:
            with open(filename, "w") as f:
                json.dump(results, f, indent=2)
            
            self.console.print(f"\\n[bold green]💾 Demo results saved to: {filename}[/bold green]")
        except Exception as e:
            self.console.print(f"\\n[bold red]❌ Error saving demo results: {str(e)}[/bold red]")

async def main():
    """Main demo function"""
    demo = UIAgentDemo()
    
    # Display banner and capabilities
    demo.display_banner()
    demo.display_capabilities()
    
    # Show demo requirements
    requirements = demo.get_demo_requirements()
    
    console.print("[bold yellow]📋 Demo Requirements:[/bold yellow]")
    req_display = f"""
    • UI Type: {requirements['ui_type']}
    • Title: {requirements['title']}
    • Description: {requirements['description']}
    • Framework: {requirements['framework']}
    • Styling: {requirements['styling']}
    • Color Scheme: {requirements['color_scheme']}
    • Responsive: {'✅ Yes' if requirements['include_responsive'] else '❌ No'}
    • Accessibility: {'✅ Yes' if requirements['include_accessibility'] else '❌ No'}
    • Animations: {'✅ Yes' if requirements['include_animations'] else '❌ No'}
    """
    console.print(Panel(req_display, border_style="yellow", title="🎯 Demo Configuration"))
    
    console.print(f"\\n[bold yellow]🚀 Starting UI generation for: {requirements['title']}[/bold yellow]")
    console.print()
    
    try:
        # Generate UI
        results = await demo.generate_ui_with_progress(requirements)
        
        # Display results
        demo.display_results(results)
        
    except KeyboardInterrupt:
        console.print("\\n[yellow]UI generation interrupted by user.[/yellow]")
    except Exception as e:
        console.print(f"\\n[red]Error during UI generation: {str(e)}[/red]")
        console.print("\\n[dim]This might be due to API limits or model availability.[/dim]")

if __name__ == "__main__":
    asyncio.run(main())
