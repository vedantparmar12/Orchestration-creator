import streamlit as st
import asyncio
import json
import httpx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
from typing import Dict, List, Any, Optional

# Import UI components
from .components.environment_manager import EnvironmentManager
from .components.database_setup import DatabaseSetup
from .components.agent_builder import AgentBuilder
from .components.tool_library_ui import ToolLibraryUI
from .components.mcp_config_ui import MCPConfigUI
from .components.live_dashboard import LiveDashboard

# Configure page
st.set_page_config(
    page_title="Enhanced Agentic Workflow Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    padding: 1rem;
    border-radius: 10px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
}

.metric-card {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #667eea;
    margin: 0.5rem 0;
}

.status-healthy {
    color: #28a745;
    font-weight: bold;
}

.status-warning {
    color: #ffc107;
    font-weight: bold;
}

.status-error {
    color: #dc3545;
    font-weight: bold;
}

.nav-link {
    padding: 0.5rem 1rem;
    margin: 0.25rem 0;
    border-radius: 5px;
    text-decoration: none;
    display: block;
    color: #495057;
    border: 1px solid #dee2e6;
}

.nav-link:hover {
    background-color: #e9ecef;
    color: #495057;
}

.nav-link.active {
    background-color: #667eea;
    color: white;
    border-color: #667eea;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'System Management'

if 'api_base_url' not in st.session_state:
    st.session_state.api_base_url = 'http://localhost:8080'

if 'system_health' not in st.session_state:
    st.session_state.system_health = None

if 'last_health_check' not in st.session_state:
    st.session_state.last_health_check = None

# Helper functions
@st.cache_data(ttl=30)
def get_system_health():
    """Get system health status"""
    try:
        response = httpx.get(f"{st.session_state.api_base_url}/health", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return {"system_health": "error", "message": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"system_health": "error", "message": str(e)}

@st.cache_data(ttl=60)
def get_agent_stats():
    """Get agent statistics"""
    try:
        response = httpx.get(f"{st.session_state.api_base_url}/api/v1/agents/stats", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

@st.cache_data(ttl=60)
def get_workflow_stats():
    """Get workflow statistics"""
    try:
        response = httpx.get(f"{st.session_state.api_base_url}/api/v1/workflows/stats", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

@st.cache_data(ttl=60)
def get_mcp_stats():
    """Get MCP statistics"""
    try:
        response = httpx.get(f"{st.session_state.api_base_url}/api/v1/mcp/stats", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def display_main_header():
    """Display main dashboard header"""
    st.markdown("""
    <div class="main-header">
        <h1>🚀 Enhanced Agentic Workflow Dashboard</h1>
        <p>Comprehensive system management and monitoring</p>
    </div>
    """, unsafe_allow_html=True)

def display_system_overview():
    """Display system overview metrics"""
    st.header("📊 System Overview")
    
    # Get system health
    health_data = get_system_health()
    agent_stats = get_agent_stats()
    workflow_stats = get_workflow_stats()
    mcp_stats = get_mcp_stats()
    
    # Create metrics columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        health_status = health_data.get('system_health', 'unknown')
        if health_status == 'healthy':
            st.metric("🟢 System Health", "Healthy", "All systems operational")
        elif health_status == 'warning':
            st.metric("🟡 System Health", "Warning", "Some issues detected")
        else:
            st.metric("🔴 System Health", "Error", health_data.get('message', 'Unknown error'))
    
    with col2:
        active_agents = agent_stats.get('active_agents', 0) if 'error' not in agent_stats else 0
        total_templates = agent_stats.get('total_templates', 0) if 'error' not in agent_stats else 0
        st.metric("🤖 Active Agents", active_agents, f"{total_templates} templates available")
    
    with col3:
        active_workflows = workflow_stats.get('active_executions', 0) if 'error' not in workflow_stats else 0
        total_executions = workflow_stats.get('total_executions', 0) if 'error' not in workflow_stats else 0
        st.metric("⚡ Active Workflows", active_workflows, f"{total_executions} total executions")
    
    with col4:
        active_connections = mcp_stats.get('active_connections', 0) if 'error' not in mcp_stats else 0
        total_connections = mcp_stats.get('total_connections', 0) if 'error' not in mcp_stats else 0
        st.metric("🔗 MCP Connections", active_connections, f"{total_connections} total connections")

def display_performance_charts():
    """Display performance charts"""
    st.header("📈 Performance Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Sample data for demonstration
        workflow_data = {
            'Template': ['Grok Heavy', 'Multi-Agent', 'Single Agent'],
            'Executions': [45, 32, 78],
            'Success Rate': [0.95, 0.88, 0.92]
        }
        
        fig = px.bar(
            workflow_data,
            x='Template',
            y='Executions',
            color='Success Rate',
            color_continuous_scale='RdYlGn',
            title='Workflow Execution Statistics'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Sample time series data
        dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
        performance_data = pd.DataFrame({
            'Date': dates,
            'Response Time': [200 + i*5 + (i%7)*20 for i in range(30)],
            'Success Rate': [0.95 + (i%5)*0.01 for i in range(30)]
        })
        
        fig = px.line(
            performance_data,
            x='Date',
            y='Response Time',
            title='Average Response Time (ms)'
        )
        st.plotly_chart(fig, use_container_width=True)

def display_recent_activity():
    """Display recent system activity"""
    st.header("📋 Recent Activity")
    
    # Sample activity data
    activity_data = [
        {"timestamp": "2024-01-18 00:00:00", "type": "Agent Created", "description": "New coding agent generated", "status": "success"},
        {"timestamp": "2024-01-17 23:58:00", "type": "Workflow Executed", "description": "Grok Heavy analysis completed", "status": "success"},
        {"timestamp": "2024-01-17 23:55:00", "type": "MCP Connection", "description": "VS Code client connected", "status": "info"},
        {"timestamp": "2024-01-17 23:52:00", "type": "Tool Added", "description": "Web scraping tool registered", "status": "success"},
        {"timestamp": "2024-01-17 23:50:00", "type": "Workflow Failed", "description": "Multi-agent workflow timeout", "status": "error"},
    ]
    
    df = pd.DataFrame(activity_data)
    
    # Style the dataframe
    def style_status(val):
        if val == 'success':
            return 'color: #28a745; font-weight: bold'
        elif val == 'error':
            return 'color: #dc3545; font-weight: bold'
        else:
            return 'color: #17a2b8; font-weight: bold'
    
    styled_df = df.style.applymap(style_status, subset=['status'])
    st.dataframe(styled_df, use_container_width=True)

def display_navigation():
    """Display navigation sidebar"""
    st.sidebar.title("🎛️ Navigation")
    
    pages = [
        ("🏠 System Management", "System Management"),
        ("🤖 Agent Builder", "Agent Builder"),
        ("⚙️ Tools Library", "Tools Library"),
        ("🗄️ Database Setup", "Database Setup"),
        ("🔧 Environment Manager", "Environment Manager"),
        ("🔗 MCP Configuration", "MCP Configuration"),
        ("📊 Live Dashboard", "Live Dashboard")
    ]
    
    for page_name, page_key in pages:
        if st.sidebar.button(page_name, key=page_key, use_container_width=True):
            st.session_state.current_page = page_key
            st.rerun()
    
    # System status in sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 System Status")
    
    health_data = get_system_health()
    health_status = health_data.get('system_health', 'unknown')
    
    if health_status == 'healthy':
        st.sidebar.success("✅ System Healthy")
    elif health_status == 'warning':
        st.sidebar.warning("⚠️ System Warning")
    else:
        st.sidebar.error("❌ System Error")
    
    # Quick actions
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚡ Quick Actions")
    
    if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    if st.sidebar.button("🧹 Clear Cache", use_container_width=True):
        st.cache_data.clear()
        st.success("Cache cleared successfully!")
    
    # Configuration
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Configuration")
    
    new_api_url = st.sidebar.text_input(
        "API Base URL",
        value=st.session_state.api_base_url,
        help="Base URL for the FastAPI service"
    )
    
    if new_api_url != st.session_state.api_base_url:
        st.session_state.api_base_url = new_api_url
        st.cache_data.clear()
        st.rerun()

def main():
    """Main dashboard function"""
    display_main_header()
    display_navigation()
    
    # Route to appropriate page
    if st.session_state.current_page == "System Management":
        display_system_overview()
        display_performance_charts()
        display_recent_activity()
    
    elif st.session_state.current_page == "Agent Builder":
        agent_builder = AgentBuilder()
        agent_builder.render()
    
    elif st.session_state.current_page == "Tools Library":
        tool_library = ToolLibraryUI()
        tool_library.render()
    
    elif st.session_state.current_page == "Database Setup":
        database_setup = DatabaseSetup()
        database_setup.render()
    
    elif st.session_state.current_page == "Environment Manager":
        env_manager = EnvironmentManager()
        env_manager.render()
    
    elif st.session_state.current_page == "MCP Configuration":
        mcp_config = MCPConfigUI()
        mcp_config.render()
    
    elif st.session_state.current_page == "Live Dashboard":
        live_dashboard = LiveDashboard()
        live_dashboard.render()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>Enhanced Agentic Workflow Dashboard v1.0.0</p>
        <p>Built with Streamlit • Powered by FastAPI • Enhanced with Pydantic AI</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
