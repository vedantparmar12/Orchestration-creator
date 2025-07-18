from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich.table import Table
from typing import Dict, Any, Optional
import time

class ProgressDisplay:
    """Real-time progress visualization for Grok heavy mode"""
    
    def __init__(self):
        self.console = Console()
        self.start_time = time.time()
        self.agent_status = {
            'research_agent': {'status': 'waiting', 'message': 'Waiting to start...'},
            'analysis_agent': {'status': 'waiting', 'message': 'Waiting to start...'},
            'perspective_agent': {'status': 'waiting', 'message': 'Waiting to start...'},
            'verification_agent': {'status': 'waiting', 'message': 'Waiting to start...'}
        }
        self.questions = None
        self.current_phase = "initializing"
    
    def update_progress(self, event_type: str, data: Any):
        """Update progress based on event type"""
        if event_type == "question_generation":
            self._update_phase("🎯 Generating Research Questions", data)
        
        elif event_type == "questions_generated":
            self.questions = data
            self._display_generated_questions()
        
        elif event_type == "parallel_execution":
            self._update_phase("🔀 Parallel Agent Execution", data)
            self._start_live_agent_display()
        
        elif event_type.endswith("_started"):
            agent_name = event_type.replace("_started", "")
            self._update_agent_status(agent_name, "running", data)
        
        elif event_type.endswith("_completed"):
            agent_name = event_type.replace("_completed", "")
            self._update_agent_status(agent_name, "completed", data)
        
        elif event_type.endswith("_failed"):
            agent_name = event_type.replace("_failed", "")
            self._update_agent_status(agent_name, "failed", data)
        
        elif event_type == "synthesis":
            self._update_phase("🔄 Intelligent Synthesis", data)
        
        elif event_type == "deep_reflection":
            self._update_phase("🧠 Phase 5: Deep Reflection", data)
        
        elif event_type == "complete":
            self._update_phase("✅ Analysis Complete", "Finalizing results...")
    
    def _update_phase(self, phase_name: str, message: str):
        """Update current phase display"""
        self.current_phase = phase_name
        
        # Clear screen and display current phase
        self.console.clear()
        self._display_header()
        
        phase_panel = Panel(
            f"[bold cyan]{phase_name}[/bold cyan]\n{message}",
            border_style="cyan",
            padding=(1, 2)
        )
        self.console.print(phase_panel)
    
    def _display_header(self):
        """Display header with elapsed time"""
        elapsed = time.time() - self.start_time
        header = f"🚀 GROK HEAVY MODE - Elapsed: {elapsed:.1f}s"
        
        self.console.print(Panel(
            Text(header, style="bold white"),
            border_style="blue",
            padding=(0, 2)
        ))
        self.console.print()
    
    def _display_generated_questions(self):
        """Display the generated research questions"""
        self.console.print("\n[bold green]🎯 Generated Research Questions:[/bold green]")
        
        questions_table = Table(show_header=True, header_style="bold magenta")
        questions_table.add_column("Agent", style="cyan", width=20)
        questions_table.add_column("Research Question", style="white")
        
        questions_table.add_row(
            "🔍 Research Agent",
            self.questions.research_question
        )
        questions_table.add_row(
            "📊 Analysis Agent", 
            self.questions.analysis_question
        )
        questions_table.add_row(
            "👁️ Perspective Agent",
            self.questions.perspective_question
        )
        questions_table.add_row(
            "✅ Verification Agent",
            self.questions.verification_question
        )
        
        self.console.print(questions_table)
        self.console.print()
    
    def _start_live_agent_display(self):
        """Start live display of agent execution"""
        self.console.print("[bold yellow]⚡ Live Agent Execution Status:[/bold yellow]")
        self._update_agent_display()
    
    def _update_agent_status(self, agent_name: str, status: str, message: str):
        """Update individual agent status"""
        if agent_name in self.agent_status:
            self.agent_status[agent_name] = {
                'status': status,
                'message': message
            }
            self._update_agent_display()
    
    def _update_agent_display(self):
        """Update the live agent status display"""
        # Create status panels for each agent
        agent_panels = []
        
        for agent_name, info in self.agent_status.items():
            status = info['status']
            message = info['message']
            
            # Choose emoji and color based on status
            if status == 'waiting':
                emoji = "⏳"
                color = "dim"
            elif status == 'running':
                emoji = "🔄"
                color = "yellow"
            elif status == 'completed':
                emoji = "✅"
                color = "green"
            elif status == 'failed':
                emoji = "❌"
                color = "red"
            else:
                emoji = "❓"
                color = "white"
            
            # Create agent panel
            agent_display_name = agent_name.replace('_', ' ').title()
            panel_content = f"{emoji} {agent_display_name}\n[{color}]{message}[/{color}]"
            
            panel = Panel(
                panel_content,
                border_style=color,
                padding=(0, 1),
                width=25
            )
            agent_panels.append(panel)
        
        # Display agents in columns
        columns = Columns(agent_panels, equal=True, expand=True)
        
        # Clear previous agent display and show updated status
        self.console.print("\033[K", end="")  # Clear line
        self.console.print(columns)
    
    def display_final_result(self, result: Any):
        """Display the final comprehensive result"""
        self.console.clear()
        self._display_header()
        
        # Display completion message
        completion_time = time.time() - self.start_time
        completion_panel = Panel(
            f"[bold green]✅ Phase 5 Analysis Complete![/bold green]\n"
            f"Total time: {completion_time:.1f} seconds\n"
            f"Agents executed: 4\n"
            f"Synthesis: Comprehensive + Deep Reflection\n"
            f"Enhancement: Phase 5 Deep Insights",
            title="🎉 Grok Heavy Analysis Complete",
            border_style="green",
            padding=(1, 2)
        )
        self.console.print(completion_panel)
        self.console.print()
        
        # Display final synthesized result
        result_panel = Panel(
            f"[bold white]{result.comprehensive_analysis}[/bold white]\n\n"
            f"[bold cyan]Key Insights:[/bold cyan]\n" +
            "\n".join(f"• {insight}" for insight in result.key_insights) + "\n\n"
            f"[bold yellow]Confidence Score:[/bold yellow] {result.confidence_score:.1%}\n"
            f"[bold magenta]Sources:[/bold magenta] {len(result.sources)} sources analyzed",
            title="📋 Comprehensive Analysis Result",
            border_style="blue",
            padding=(1, 2)
        )
        self.console.print(result_panel)
