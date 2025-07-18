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

class LiveDashboard:
    """Real-time monitoring dashboard component"""
    
    def __init__(self):
        self.api_base_url = st.session_state.get('api_base_url', 'http://localhost:8080')
        
        # Initialize session state for live data
        if 'live_data' not in st.session_state:
            st.session_state.live_data = {
                'workflow_executions': [],
                'agent_activity': [],
                'mcp_connections': [],
                'system_metrics': []
            }
    
    def render(self):
        """Render the live dashboard"""
        st.header("📊 Live Dashboard")
        st.subheader("Real-time system monitoring and analytics")
        
        # Auto-refresh controls
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            auto_refresh = st.toggle("Auto Refresh", value=True)
            
        with col2:
            refresh_interval = st.selectbox(
                "Refresh Interval",
                options=[5, 10, 30, 60],
                format_func=lambda x: f"{x}s",
                index=1
            )
        
        with col3:
            if st.button("🔄 Refresh Now"):
                self._refresh_data()
        
        # Real-time metrics
        self._render_real_time_metrics()
        
        # Live workflow monitoring
        self._render_live_workflows()
        
        # Agent activity monitoring
        self._render_agent_activity()
        
        # MCP connection monitoring
        self._render_mcp_monitoring()
        
        # System performance charts
        self._render_performance_charts()
        
        # Auto-refresh logic
        if auto_refresh:
            time.sleep(refresh_interval)
            st.rerun()
    
    def _refresh_data(self):
        """Refresh live data from API"""
        try:
            # Clear cache to get fresh data
            st.cache_data.clear()
            
            # Fetch new data
            workflow_data = self._fetch_workflow_data()
            agent_data = self._fetch_agent_data()
            mcp_data = self._fetch_mcp_data()
            system_data = self._fetch_system_data()
            
            # Update session state
            timestamp = datetime.now().isoformat()
            
            st.session_state.live_data['workflow_executions'].append({
                'timestamp': timestamp,
                'data': workflow_data
            })
            
            st.session_state.live_data['agent_activity'].append({
                'timestamp': timestamp,
                'data': agent_data
            })
            
            st.session_state.live_data['mcp_connections'].append({
                'timestamp': timestamp,
                'data': mcp_data
            })
            
            st.session_state.live_data['system_metrics'].append({
                'timestamp': timestamp,
                'data': system_data
            })
            
            # Keep only last 100 entries
            for key in st.session_state.live_data:
                if len(st.session_state.live_data[key]) > 100:
                    st.session_state.live_data[key] = st.session_state.live_data[key][-100:]
            
        except Exception as e:
            st.error(f"Error refreshing data: {str(e)}")
    
    def _fetch_workflow_data(self) -> Dict[str, Any]:
        """Fetch workflow execution data"""
        try:
            response = httpx.get(f"{self.api_base_url}/api/v1/workflows/stats", timeout=5)
            if response.status_code == 200:
                return response.json()
            return {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def _fetch_agent_data(self) -> Dict[str, Any]:
        """Fetch agent activity data"""
        try:
            response = httpx.get(f"{self.api_base_url}/api/v1/agents/stats", timeout=5)
            if response.status_code == 200:
                return response.json()
            return {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def _fetch_mcp_data(self) -> Dict[str, Any]:
        """Fetch MCP connection data"""
        try:
            response = httpx.get(f"{self.api_base_url}/api/v1/mcp/stats", timeout=5)
            if response.status_code == 200:
                return response.json()
            return {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def _fetch_system_data(self) -> Dict[str, Any]:
        """Fetch system health data"""
        try:
            response = httpx.get(f"{self.api_base_url}/health", timeout=5)
            if response.status_code == 200:
                return response.json()
            return {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def _render_real_time_metrics(self):
        """Render real-time metrics"""
        st.subheader("⚡ Real-time Metrics")
        
        # Get latest data
        latest_workflow = st.session_state.live_data['workflow_executions'][-1]['data'] if st.session_state.live_data['workflow_executions'] else {}
        latest_agent = st.session_state.live_data['agent_activity'][-1]['data'] if st.session_state.live_data['agent_activity'] else {}
        latest_mcp = st.session_state.live_data['mcp_connections'][-1]['data'] if st.session_state.live_data['mcp_connections'] else {}
        latest_system = st.session_state.live_data['system_metrics'][-1]['data'] if st.session_state.live_data['system_metrics'] else {}
        
        # Create metric columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            active_workflows = latest_workflow.get('active_executions', 0)
            st.metric("🔄 Active Workflows", active_workflows)
        
        with col2:
            active_agents = latest_agent.get('active_agents', 0)
            st.metric("🤖 Active Agents", active_agents)
        
        with col3:
            active_connections = latest_mcp.get('active_connections', 0)
            st.metric("🔗 MCP Connections", active_connections)
        
        with col4:
            system_health = latest_system.get('system_health', 'unknown')
            health_color = "🟢" if system_health == 'healthy' else "🔴"
            st.metric(f"{health_color} System Health", system_health.title())
    
    def _render_live_workflows(self):
        """Render live workflow monitoring"""
        st.subheader("🔄 Live Workflow Monitoring")
        
        try:
            # Fetch recent workflow executions
            response = httpx.get(f"{self.api_base_url}/api/v1/workflows/executions?limit=10", timeout=5)
            if response.status_code == 200:
                executions = response.json()
                
                if executions:
                    # Create workflow status table
                    df = pd.DataFrame(executions)
                    
                    # Style the status column
                    def style_status(val):
                        if val == 'completed':
                            return 'background-color: #d4edda; color: #155724'
                        elif val == 'running':
                            return 'background-color: #fff3cd; color: #856404'
                        elif val == 'failed':
                            return 'background-color: #f8d7da; color: #721c24'
                        else:
                            return 'background-color: #e2e3e5; color: #383d41'
                    
                    styled_df = df.style.applymap(style_status, subset=['status'])
                    st.dataframe(styled_df, use_container_width=True)
                else:
                    st.info("No recent workflow executions found")
            else:
                st.error(f"Failed to fetch workflow data: HTTP {response.status_code}")
        
        except Exception as e:
            st.error(f"Error fetching workflow data: {str(e)}")
    
    def _render_agent_activity(self):
        """Render agent activity monitoring"""
        st.subheader("🤖 Agent Activity")
        
        # Create sample agent activity data
        agent_activities = [
            {"agent_id": "agent-001", "type": "Coder Agent", "status": "active", "task": "Code generation", "progress": 75},
            {"agent_id": "agent-002", "type": "Advisor Agent", "status": "active", "task": "Context analysis", "progress": 60},
            {"agent_id": "agent-003", "type": "Synthesis Agent", "status": "idle", "task": "Waiting for input", "progress": 0},
            {"agent_id": "agent-004", "type": "Refiner Agent", "status": "completed", "task": "Code refinement", "progress": 100}
        ]
        
        # Create agent activity table
        for activity in agent_activities:
            col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
            
            with col1:
                status_color = "🟢" if activity['status'] == 'active' else "🔴" if activity['status'] == 'failed' else "🟡"
                st.write(f"{status_color} {activity['agent_id']}")
            
            with col2:
                st.write(activity['type'])
            
            with col3:
                st.write(activity['task'])
            
            with col4:
                progress = activity['progress']
                st.progress(progress / 100)
                st.write(f"{progress}%")
    
    def _render_mcp_monitoring(self):
        """Render MCP connection monitoring"""
        st.subheader("🔗 MCP Connection Monitoring")
        
        try:
            # Fetch MCP connections
            response = httpx.get(f"{self.api_base_url}/api/v1/mcp/connections", timeout=5)
            if response.status_code == 200:
                connections_data = response.json()
                connections = connections_data.get('connections', [])
                
                if connections:
                    # Create connections table
                    df = pd.DataFrame(connections)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No active MCP connections")
            else:
                st.error(f"Failed to fetch MCP data: HTTP {response.status_code}")
        
        except Exception as e:
            st.error(f"Error fetching MCP data: {str(e)}")
    
    def _render_performance_charts(self):
        """Render performance charts"""
        st.subheader("📈 Performance Charts")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Workflow execution timeline
            if st.session_state.live_data['workflow_executions']:
                timeline_data = []
                for entry in st.session_state.live_data['workflow_executions'][-20:]:  # Last 20 entries
                    timestamp = entry['timestamp']
                    data = entry['data']
                    timeline_data.append({
                        'timestamp': timestamp,
                        'active_executions': data.get('active_executions', 0),
                        'total_executions': data.get('total_executions', 0)
                    })
                
                df = pd.DataFrame(timeline_data)
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                
                fig = px.line(
                    df, 
                    x='timestamp', 
                    y='active_executions',
                    title='Active Workflow Executions Over Time',
                    labels={'timestamp': 'Time', 'active_executions': 'Active Executions'}
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No workflow data available for chart")
        
        with col2:
            # Agent activity timeline
            if st.session_state.live_data['agent_activity']:
                agent_timeline = []
                for entry in st.session_state.live_data['agent_activity'][-20:]:  # Last 20 entries
                    timestamp = entry['timestamp']
                    data = entry['data']
                    agent_timeline.append({
                        'timestamp': timestamp,
                        'active_agents': data.get('active_agents', 0),
                        'total_templates': data.get('total_templates', 0)
                    })
                
                df = pd.DataFrame(agent_timeline)
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                
                fig = px.line(
                    df, 
                    x='timestamp', 
                    y='active_agents',
                    title='Active Agents Over Time',
                    labels={'timestamp': 'Time', 'active_agents': 'Active Agents'}
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No agent data available for chart")
    
    def _render_system_logs(self):
        """Render system logs"""
        st.subheader("📝 System Logs")
        
        # Sample log entries
        log_entries = [
            {"timestamp": "2024-01-18 00:05:00", "level": "INFO", "message": "Workflow execution started", "component": "WorkflowRouter"},
            {"timestamp": "2024-01-18 00:04:30", "level": "DEBUG", "message": "Agent generation completed", "component": "AgentCoordinator"},
            {"timestamp": "2024-01-18 00:04:00", "level": "WARNING", "message": "Rate limit approaching", "component": "APIClient"},
            {"timestamp": "2024-01-18 00:03:30", "level": "INFO", "message": "MCP client connected", "component": "MCPServer"},
            {"timestamp": "2024-01-18 00:03:00", "level": "ERROR", "message": "Database connection timeout", "component": "DatabaseManager"}
        ]
        
        # Create log table
        for entry in log_entries:
            col1, col2, col3, col4 = st.columns([2, 1, 4, 2])
            
            with col1:
                st.write(entry['timestamp'])
            
            with col2:
                level = entry['level']
                if level == 'ERROR':
                    st.error(level)
                elif level == 'WARNING':
                    st.warning(level)
                elif level == 'INFO':
                    st.info(level)
                else:
                    st.write(level)
            
            with col3:
                st.write(entry['message'])
            
            with col4:
                st.write(entry['component'])
