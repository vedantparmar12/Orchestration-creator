import streamlit as st
import httpx
import json
from typing import Dict, List, Any, Optional

class AgentBuilder:
    """UI component for visual agent creation"""
    
    def __init__(self):
        self.api_base_url = st.session_state.get('api_base_url', 'http://localhost:8080')
        self.agent_templates = self._load_agent_templates()
        self.available_tools = self._load_available_tools()
    
    def render(self):
        """Render the agent builder UI"""
        st.header("🤖 Agent Builder")
        st.subheader("Create and customize AI agents visually")
        
        # Agent creation tabs
        tab1, tab2, tab3 = st.tabs(["🛠️ Build Agent", "📋 Templates", "📊 Active Agents"])
        
        with tab1:
            self._render_agent_creation()
        
        with tab2:
            self._render_template_browser()
        
        with tab3:
            self._render_active_agents()
    
    def _render_agent_creation(self):
        """Render agent creation interface"""
        st.subheader("Build Your Agent")
        
        # Agent configuration form
        with st.form("agent_creation_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Basic agent info
                agent_name = st.text_input("Agent Name", placeholder="My Custom Agent")
                agent_type = st.selectbox(
                    "Agent Type",
                    ["Coder Agent", "Research Agent", "Analysis Agent", "Synthesis Agent", "Custom Agent"]
                )
                
                # Model selection
                model_provider = st.selectbox(
                    "Model Provider",
                    ["openai:gpt-4o", "anthropic:claude-3-5-sonnet-20241022", "google:gemini-pro"]
                )
                
                # Template selection
                template_names = list(self.agent_templates.keys())
                selected_template = st.selectbox(
                    "Base Template (Optional)",
                    ["None"] + template_names
                )
            
            with col2:
                # Requirements
                requirements = st.text_area(
                    "Agent Requirements",
                    placeholder="Describe what your agent should do...",
                    height=100
                )
                
                # Tool selection
                selected_tools = st.multiselect(
                    "Available Tools",
                    self.available_tools
                )
                
                # Advanced settings
                with st.expander("Advanced Settings"):
                    max_tokens = st.slider("Max Tokens", 100, 4000, 1000)
                    temperature = st.slider("Temperature", 0.0, 2.0, 0.7)
                    enable_memory = st.checkbox("Enable Memory", value=True)
                    enable_tools = st.checkbox("Enable Tools", value=True)
            
            # System prompt customization
            st.subheader("System Prompt")
            system_prompt = st.text_area(
                "Custom System Prompt (Optional)",
                placeholder="You are a helpful assistant...",
                height=150
            )
            
            # Create agent button
            submitted = st.form_submit_button("🚀 Create Agent")
            
            if submitted:
                if agent_name and agent_type and requirements:
                    self._create_agent({
                        "name": agent_name,
                        "type": agent_type,
                        "requirements": requirements,
                        "model_provider": model_provider,
                        "template": selected_template if selected_template != "None" else None,
                        "tools": selected_tools,
                        "system_prompt": system_prompt,
                        "config": {
                            "max_tokens": max_tokens,
                            "temperature": temperature,
                            "enable_memory": enable_memory,
                            "enable_tools": enable_tools
                        }
                    })
                else:
                    st.error("Please fill in all required fields!")
    
    def _render_template_browser(self):
        """Render template browser"""
        st.subheader("Agent Templates")
        
        # Template search
        search_query = st.text_input("🔍 Search Templates", placeholder="Search templates...")
        
        # Template grid
        filtered_templates = self.agent_templates
        if search_query:
            filtered_templates = {
                k: v for k, v in self.agent_templates.items() 
                if search_query.lower() in k.lower() or search_query.lower() in v.get('description', '').lower()
            }
        
        # Display templates in cards
        cols = st.columns(3)
        for i, (template_name, template_data) in enumerate(filtered_templates.items()):
            with cols[i % 3]:
                with st.container():
                    st.markdown(f"### {template_name}")
                    st.write(template_data.get('description', 'No description available'))
                    
                    # Template details
                    st.markdown(f"**Category:** {template_data.get('category', 'General')}")
                    st.markdown(f"**Tools:** {', '.join(template_data.get('tools', []))}")
                    
                    if st.button(f"Use Template", key=f"use_{template_name}"):
                        st.session_state.selected_template = template_name
                        st.success(f"Selected template: {template_name}")
    
    def _render_active_agents(self):
        """Render active agents list"""
        st.subheader("Active Agents")
        
        try:
            # Fetch active agents from API
            response = httpx.get(f"{self.api_base_url}/api/v1/agents/stats", timeout=5)
            if response.status_code == 200:
                stats = response.json()
                
                # Display agent statistics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Active Agents", stats.get('active_agents', 0))
                
                with col2:
                    st.metric("Total Templates", stats.get('total_templates', 0))
                
                with col3:
                    st.metric("MCP Compatible Tools", stats.get('mcp_compatible_tools', 0))
                
                # Sample active agents list
                st.subheader("Agent List")
                
                # Create sample agent data
                sample_agents = [
                    {"id": "agent-001", "name": "Code Assistant", "type": "Coder Agent", "status": "active", "created": "2024-01-17"},
                    {"id": "agent-002", "name": "Research Helper", "type": "Research Agent", "status": "idle", "created": "2024-01-16"},
                    {"id": "agent-003", "name": "Data Analyzer", "type": "Analysis Agent", "status": "active", "created": "2024-01-15"}
                ]
                
                for agent in sample_agents:
                    with st.container():
                        col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
                        
                        with col1:
                            st.write(f"**{agent['name']}**")
                            st.write(f"ID: {agent['id']}")
                        
                        with col2:
                            st.write(agent['type'])
                        
                        with col3:
                            status_color = "🟢" if agent['status'] == 'active' else "🟡"
                            st.write(f"{status_color} {agent['status']}")
                        
                        with col4:
                            st.write(agent['created'])
                        
                        with col5:
                            if st.button("⚙️", key=f"config_{agent['id']}"):
                                st.info(f"Configure {agent['name']}")
                        
                        st.markdown("---")
            
            else:
                st.error(f"Failed to fetch agent data: HTTP {response.status_code}")
        
        except Exception as e:
            st.error(f"Error fetching agent data: {str(e)}")
    
    def _create_agent(self, agent_config: Dict[str, Any]):
        """Create agent based on configuration"""
        try:
            # Prepare API request
            request_data = {
                "agent_type": agent_config['type'],
                "requirements": agent_config['requirements'],
                "tools": agent_config['tools'],
                "configuration": agent_config['config']
            }
            
            if agent_config['template']:
                request_data['template_id'] = agent_config['template']
            
            # Make API request
            response = httpx.post(
                f"{self.api_base_url}/api/v1/generate-agent",
                json=request_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                st.success(f"✅ Agent creation started! ID: {result['agent_id']}")
                
                # Display creation details
                with st.expander("Creation Details"):
                    st.json(result)
                
                # Show progress
                with st.spinner("Creating agent..."):
                    # Check status after a moment
                    import time
                    time.sleep(2)
                    
                    status_response = httpx.get(
                        f"{self.api_base_url}/api/v1/agents/{result['agent_id']}/status",
                        timeout=10
                    )
                    
                    if status_response.status_code == 200:
                        status = status_response.json()
                        if status['status'] == 'completed':
                            st.success("🎉 Agent created successfully!")
                        elif status['status'] == 'in_progress':
                            st.info("⏳ Agent creation in progress...")
                        else:
                            st.warning(f"⚠️ Status: {status['status']}")
            else:
                st.error(f"❌ Failed to create agent: HTTP {response.status_code}")
                st.error(response.text)
        
        except Exception as e:
            st.error(f"❌ Error creating agent: {str(e)}")
    
    def _load_agent_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load agent templates from API"""
        try:
            response = httpx.get(f"{self.api_base_url}/api/v1/agents/templates", timeout=5)
            if response.status_code == 200:
                templates = response.json()
                return {t['name']: t for t in templates}
            else:
                # Fallback to static templates
                return self._get_fallback_templates()
        except Exception:
            return self._get_fallback_templates()
    
    def _get_fallback_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get fallback templates when API is unavailable"""
        return {
            "Coder Agent": {
                "description": "Specialized in code generation, review, and debugging",
                "category": "Development",
                "tools": ["code_analyzer", "syntax_checker", "git_tools"]
            },
            "Research Agent": {
                "description": "Conducts in-depth research and analysis",
                "category": "Research",
                "tools": ["web_search", "document_analyzer", "summarizer"]
            },
            "Analysis Agent": {
                "description": "Performs data analysis and generates insights",
                "category": "Analytics",
                "tools": ["data_processor", "chart_generator", "statistical_analyzer"]
            },
            "Synthesis Agent": {
                "description": "Combines multiple inputs into coherent outputs",
                "category": "Coordination",
                "tools": ["content_merger", "summarizer", "formatter"]
            }
        }
    
    def _load_available_tools(self) -> List[str]:
        """Load available tools from API"""
        try:
            response = httpx.get(f"{self.api_base_url}/api/v1/agents/tools", timeout=5)
            if response.status_code == 200:
                tools = response.json()
                return [tool['name'] for tool in tools]
            else:
                return self._get_fallback_tools()
        except Exception:
            return self._get_fallback_tools()
    
    def _get_fallback_tools(self) -> List[str]:
        """Get fallback tools when API is unavailable"""
        return [
            "web_search", "code_analyzer", "document_processor",
            "data_visualizer", "api_client", "file_manager",
            "git_tools", "database_connector", "email_sender",
            "image_processor", "text_summarizer", "translator"
        ]
