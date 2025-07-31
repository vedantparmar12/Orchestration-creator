import asyncio
import sys
from rich.console import Console
from rich.prompt import Prompt, Confirm
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

# Load environment variables
load_dotenv()

console = Console()

class UIComponent(BaseModel):
    """Definition of a UI component"""
    name: str = Field(description="Name of the component")
    type: str = Field(description="Type of component (button, form, modal, etc.)")
    properties: Dict[str, Any] = Field(description="Component properties")
    styling: Dict[str, str] = Field(description="CSS styling properties")
    interactions: List[str] = Field(description="User interactions supported")

class UILayoutSpec(BaseModel):
    """Complete UI layout specification"""
    title: str = Field(description="Title of the UI")
    description: str = Field(description="Description of the UI purpose")
    layout_type: str = Field(description="Layout type (grid, flexbox, etc.)")
    components: List[UIComponent] = Field(description="List of UI components")
    color_scheme: Dict[str, str] = Field(description="Color scheme definition")
    responsive_breakpoints: Dict[str, str] = Field(description="Responsive design breakpoints")

class UIAgentCapabilities(BaseModel):
    """Capabilities of the UI agent"""
    supported_frameworks: List[str] = Field(description="Supported UI frameworks")
    component_types: List[str] = Field(description="Types of components it can create")
    styling_approaches: List[str] = Field(description="Styling approaches supported")
    interaction_patterns: List[str] = Field(description="Interaction patterns supported")
    accessibility_features: List[str] = Field(description="Accessibility features included")

class GeneratedUICode(BaseModel):
    """Generated UI code output"""
    html_code: str = Field(description="Generated HTML code")
    css_code: str = Field(description="Generated CSS code")
    javascript_code: str = Field(description="Generated JavaScript code")
    framework_specific_code: Optional[str] = Field(description="Framework-specific code (React, Vue, etc.)")
    component_documentation: str = Field(description="Documentation for the components")
    usage_examples: List[str] = Field(description="Usage examples")

class UIAgentOrchestrator:
    """Beautiful UI Agent Creation and Management System"""
    
    def __init__(self):
        self.console = Console()
        self.model = create_openrouter_model()
        
        # Create specialized UI agents
        self.agents = self._create_ui_agents()
        
        # UI generation history
        self.generation_history: List[Dict[str, Any]] = []
    
    def _create_ui_agents(self) -> Dict[str, Agent]:
        """Create specialized UI agents"""
        return {
            'ui_designer': Agent(
                model=self.model,
                system_prompt="""You are a UI/UX design expert specializing in creating beautiful, 
                functional user interfaces. You excel at:
                - Modern design principles and best practices
                - Color theory and typography
                - User experience optimization
                - Responsive design patterns
                - Accessibility standards
                Focus on creating visually appealing and user-friendly interfaces."""
            ),
            
            'frontend_developer': Agent(
                model=self.model,
                system_prompt="""You are a senior frontend developer expert in multiple frameworks.
                You specialize in:
                - Clean, semantic HTML structure
                - Modern CSS with Flexbox/Grid
                - JavaScript ES6+ best practices
                - React, Vue, Angular frameworks
                - Performance optimization
                - Cross-browser compatibility
                Create production-ready, maintainable code."""
            ),
            
            'accessibility_expert': Agent(
                model=self.model,
                system_prompt="""You are an accessibility expert focused on inclusive design.
                Your expertise includes:
                - WCAG 2.1 AA compliance
                - Screen reader compatibility
                - Keyboard navigation
                - Color contrast optimization
                - Semantic HTML structure
                - ARIA attributes and roles
                Ensure all interfaces are accessible to users with disabilities."""
            ),
            
            'interaction_designer': Agent(
                model=self.model,
                system_prompt="""You are an interaction design specialist focused on user behavior.
                You excel at:
                - Micro-interactions and animations
                - User flow optimization
                - Gesture and touch interactions
                - State management patterns
                - Feedback and loading states
                - Progressive enhancement
                Create engaging, intuitive user experiences."""
            )
        }
    
    def display_banner(self):
        """Display beautiful banner"""
        banner = Text("🎨 UI AGENT CREATOR", style="bold cyan")
        banner.append("\nBeautiful Interface Generation System", style="dim")
        
        panel = Panel(
            banner,
            border_style="cyan",
            padding=(1, 2),
            title="✨ Advanced UI Generation",
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
    
    def get_ui_requirements(self) -> Dict[str, Any]:
        """Interactive UI requirements gathering"""
        self.console.print("[bold yellow]📋 UI Requirements Gathering[/bold yellow]")
        self.console.print()
        
        # Basic requirements
        ui_type = Prompt.ask(
            "What type of UI do you want to create?",
            choices=["dashboard", "landing-page", "form", "modal", "navigation", "card-layout", "data-table", "custom"],
            default="dashboard"
        )
        
        title = Prompt.ask("Enter the UI title", default="My Beautiful UI")
        
        description = Prompt.ask("Describe the UI purpose", default="A modern, responsive user interface")
        
        # Framework preference
        framework = Prompt.ask(
            "Preferred framework?",
            choices=["vanilla", "react", "vue", "angular", "svelte"],
            default="react"
        )
        
        # Styling approach
        styling = Prompt.ask(
            "Styling approach?",
            choices=["css", "scss", "tailwind", "styled-components", "emotion"],
            default="css"
        )
        
        # Color scheme
        color_scheme = Prompt.ask(
            "Color scheme preference?",
            choices=["modern-blue", "dark-mode", "minimal-gray", "vibrant-purple", "nature-green", "custom"],
            default="modern-blue"
        )
        
        # Advanced features
        include_animations = Confirm.ask("Include animations and micro-interactions?", default=True)
        include_responsive = Confirm.ask("Make it responsive?", default=True)
        include_accessibility = Confirm.ask("Include accessibility features?", default=True)
        
        return {
            "ui_type": ui_type,
            "title": title,
            "description": description,
            "framework": framework,
            "styling": styling,
            "color_scheme": color_scheme,
            "include_animations": include_animations,
            "include_responsive": include_responsive,
            "include_accessibility": include_accessibility,
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
        
        # Progress bars
        progress_table = Table(show_header=False, box=None, padding=(0, 1))
        progress_table.add_column("Agent", style="cyan", width=20)
        progress_table.add_column("Progress", width=40)
        progress_table.add_column("Status", style="green", width=20)
        
        agents_progress = {
            "🎨 UI Designer": {"progress": 0, "status": "⏳ Waiting..."},
            "💻 Frontend Developer": {"progress": 0, "status": "⏳ Waiting..."},
            "♿ Accessibility Expert": {"progress": 0, "status": "⏳ Waiting..."},
            "🎭 Interaction Designer": {"progress": 0, "status": "⏳ Waiting..."}
        }
        
        # Status panel
        status_text = Text("🚀 Initializing UI generation...", style="bold yellow")
        status_panel = Panel(status_text, border_style="yellow", title="Current Status")
        
        with Live(layout, refresh_per_second=4, screen=True):
            layout["header"].update(header)
            
            # Step 1: UI Design
            agents_progress["🎨 UI Designer"]["status"] = "🔄 Designing..."
            self._update_progress_display(layout, progress_table, agents_progress, "Creating visual design...")
            
            design_result = await self._run_ui_designer(requirements)
            agents_progress["🎨 UI Designer"]["progress"] = 100
            agents_progress["🎨 UI Designer"]["status"] = "✅ Complete"
            
            # Step 2: Frontend Development
            agents_progress["💻 Frontend Developer"]["status"] = "🔄 Coding..."
            self._update_progress_display(layout, progress_table, agents_progress, "Generating code...")
            
            code_result = await self._run_frontend_developer(requirements, design_result)
            agents_progress["💻 Frontend Developer"]["progress"] = 100
            agents_progress["💻 Frontend Developer"]["status"] = "✅ Complete"
            
            # Step 3: Accessibility
            if requirements["include_accessibility"]:
                agents_progress["♿ Accessibility Expert"]["status"] = "🔄 Optimizing..."
                self._update_progress_display(layout, progress_table, agents_progress, "Adding accessibility features...")
                
                accessibility_result = await self._run_accessibility_expert(requirements, code_result)
                agents_progress["♿ Accessibility Expert"]["progress"] = 100
                agents_progress["♿ Accessibility Expert"]["status"] = "✅ Complete"
            else:
                agents_progress["♿ Accessibility Expert"]["status"] = "⏭️ Skipped"
                accessibility_result = {}
            
            # Step 4: Interactions
            if requirements["include_animations"]:
                agents_progress["🎭 Interaction Designer"]["status"] = "🔄 Animating..."
                self._update_progress_display(layout, progress_table, agents_progress, "Adding interactions...")
                
                interaction_result = await self._run_interaction_designer(requirements, code_result)
                agents_progress["🎭 Interaction Designer"]["progress"] = 100
                agents_progress["🎭 Interaction Designer"]["status"] = "✅ Complete"
            else:
                agents_progress["🎭 Interaction Designer"]["status"] = "⏭️ Skipped"
                interaction_result = {}
            
            # Final update
            self._update_progress_display(layout, progress_table, agents_progress, "🎉 Generation complete!")
            
            # Small delay to show completion
            await asyncio.sleep(1)
        
        return {
            "requirements": requirements,
            "design": design_result,
            "code": code_result,
            "accessibility": accessibility_result,
            "interactions": interaction_result,
            "generation_time": datetime.now().isoformat()
        }
    
    def _update_progress_display(self, layout, progress_table, agents_progress, status_message):
        """Update progress display"""
        # Clear and rebuild progress table
        progress_table.rows.clear()
        
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
        
        try:
            result = await self.agents['ui_designer'].run(prompt)
            return result.data
        except Exception as e:
            return f"Design generation failed: {str(e)}"
    
    async def _run_frontend_developer(self, requirements: Dict[str, Any], design: str) -> str:
        """Run frontend developer agent"""
        prompt = f"""
        Based on this design specification:
        {design}
        
        Generate complete frontend code for:
        - Framework: {requirements['framework']}
        - Styling: {requirements['styling']}
        - Type: {requirements['ui_type']}
        
        Include HTML, CSS, and JavaScript code with proper structure and best practices.
        """
        
        try:
            result = await self.agents['frontend_developer'].run(prompt)
            return result.data
        except Exception as e:
            return f"Code generation failed: {str(e)}"
    
    async def _run_accessibility_expert(self, requirements: Dict[str, Any], code: str) -> str:
        """Run accessibility expert agent"""
        prompt = f"""
        Review and enhance this code for accessibility:
        {code[:1000]}...
        
        Add WCAG 2.1 AA compliance features, ARIA attributes, keyboard navigation, and screen reader support.
        """
        
        try:
            result = await self.agents['accessibility_expert'].run(prompt)
            return result.data
        except Exception as e:
            return f"Accessibility enhancement failed: {str(e)}"
    
    async def _run_interaction_designer(self, requirements: Dict[str, Any], code: str) -> str:
        """Run interaction designer agent"""
        prompt = f"""
        Add beautiful interactions and animations to this UI:
        {code[:1000]}...
        
        Include micro-interactions, hover effects, loading states, and smooth transitions.
        """
        
        try:
            result = await self.agents['interaction_designer'].run(prompt)
            return result.data
        except Exception as e:
            return f"Interaction design failed: {str(e)}"
    
    def display_results(self, results: Dict[str, Any]):
        """Display beautiful results"""
        self.console.print("\n" + "="*80)
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
            ("🎨 Design Specification", results["design"]),
            ("💻 Generated Code", results["code"]),
            ("♿ Accessibility Features", results["accessibility"]),
            ("🎭 Interactions & Animations", results["interactions"])
        ]
        
        for title, content in sections:
            if content and not content.startswith("Error") and not content.startswith("failed"):
                self.console.print(f"\n[bold cyan]{title}:[/bold cyan]")
                # Show first 500 chars of content
                preview = content[:500] + "..." if len(content) > 500 else content
                self.console.print(Panel(
                    preview,
                    border_style="blue",
                    padding=(1, 2)
                ))
        
        # Save option
        save_files = Confirm.ask("\n💾 Save generated files to disk?", default=True)
        if save_files:
            self.save_generated_files(results)
    
    def save_generated_files(self, results: Dict[str, Any]):
        """Save generated files to disk"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_name = f"generated_ui_{timestamp}"
        
        try:
            os.makedirs(folder_name, exist_ok=True)
            
            # Save requirements
            with open(f"{folder_name}/requirements.json", "w") as f:
                json.dump(results["requirements"], f, indent=2)
            
            # Save design spec
            with open(f"{folder_name}/design_spec.md", "w") as f:
                f.write(results["design"])
            
            # Save code
            with open(f"{folder_name}/generated_code.txt", "w") as f:
                f.write(results["code"])
            
            # Save accessibility notes
            if results["accessibility"]:
                with open(f"{folder_name}/accessibility_notes.md", "w") as f:
                    f.write(results["accessibility"])
            
            # Save interaction notes
            if results["interactions"]:
                with open(f"{folder_name}/interactions_notes.md", "w") as f:
                    f.write(results["interactions"])
            
            self.console.print(f"[bold green]✅ Files saved to: {folder_name}/[/bold green]")
            
        except Exception as e:
            self.console.print(f"[bold red]❌ Error saving files: {str(e)}[/bold red]")

async def main():
    """Main UI Agent Creator"""
    orchestrator = UIAgentOrchestrator()
    
    # Display banner and capabilities
    orchestrator.display_banner()
    orchestrator.display_capabilities()
    
    # Get requirements
    requirements = orchestrator.get_ui_requirements()
    
    console.print(f"\n[bold yellow]🚀 Starting UI generation for: {requirements['title']}[/bold yellow]")
    console.print()
    
    try:
        # Generate UI
        results = await orchestrator.generate_ui_with_progress(requirements)
        
        # Display results
        orchestrator.display_results(results)
        
    except KeyboardInterrupt:
        console.print("\n[yellow]UI generation interrupted by user.[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error during UI generation: {str(e)}[/red]")
        console.print("\n[dim]This might be due to API limits or model availability.[/dim]")
        
        # Offer to try with simple mode
        try_simple = Confirm.ask("Would you like to try with a simpler approach?", default=True)
        if try_simple:
            console.print("\n[cyan]💡 Tip: Try using the simple_grok_heavy.py for basic functionality[/cyan]")

if __name__ == "__main__":
    asyncio.run(main())
