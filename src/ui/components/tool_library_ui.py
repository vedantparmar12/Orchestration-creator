import streamlit as st
from typing import Dict, List, Any
import json
import os

class ToolLibraryUI:
    """UI component for tool library browser and manager"""
    
    def __init__(self):
        self.tools_data = self._load_tools_data()
        self.categories = self._get_categories()
    
    def render(self):
        """Render the tool library UI"""
        st.header("⚙️ Tool Library")
        st.subheader("Browse and manage available tools")
        
        # Tool library tabs
        tab1, tab2, tab3 = st.tabs(["🔍 Browse Tools", "🛠️ Tool Builder", "📊 Analytics"])
        
        with tab1:
            self._render_tool_browser()
        
        with tab2:
            self._render_tool_builder()
        
        with tab3:
            self._render_analytics()
    
    def _render_tool_browser(self):
        """Render the tool browser"""
        # Search and filter
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            search_query = st.text_input("🔍 Search tools...", placeholder="Enter tool name or description")
        
        with col2:
            category_filter = st.selectbox("Category", ["All"] + self.categories)
        
        with col3:
            mcp_filter = st.selectbox("MCP Compatible", ["All", "Yes", "No"])
        
        # Display tools
        filtered_tools = self._filter_tools(search_query, category_filter, mcp_filter)
        
        # Statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Tools", len(self.tools_data))
        with col2:
            mcp_count = len([t for t in self.tools_data if t.get('mcp_compatible', False)])
            st.metric("MCP Compatible", mcp_count)
        with col3:
            st.metric("Filtered Results", len(filtered_tools))
        
        if filtered_tools:
            st.subheader(f"Available Tools ({len(filtered_tools)})")
            
            # Display tools in grid
            cols = st.columns(3)
            for i, tool in enumerate(filtered_tools):
                with cols[i % 3]:
                    self._render_tool_card(tool)
        else:
            st.info("No tools found matching your criteria.")
    
    def _render_tool_builder(self):
        """Render the tool builder"""
        st.subheader("Create Custom Tools")
        self._render_add_tool_form()
    
    def _render_analytics(self):
        """Render analytics dashboard"""
        st.subheader("Tool Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Category distribution
            category_counts = {}
            for tool in self.tools_data:
                cat = tool['category']
                category_counts[cat] = category_counts.get(cat, 0) + 1
            
            st.subheader("Tools by Category")
            for category, count in category_counts.items():
                st.write(f"**{category.replace('_', ' ').title()}:** {count} tools")
        
        with col2:
            # MCP compatibility
            mcp_compatible = len([t for t in self.tools_data if t.get('mcp_compatible', False)])
            total_tools = len(self.tools_data)
            
            st.subheader("MCP Compatibility")
            st.write(f"**Compatible:** {mcp_compatible} tools")
            st.write(f"**Not Compatible:** {total_tools - mcp_compatible} tools")
            st.write(f"**Compatibility Rate:** {mcp_compatible/total_tools*100:.1f}%")
    
    def _render_tool_card(self, tool: Dict[str, Any]):
        """Render a single tool card"""
        with st.container():
            st.markdown(f"""
            <div style="border: 1px solid #ddd; border-radius: 8px; padding: 16px; margin: 8px 0;">
                <h4>{tool['name']}</h4>
                <p><strong>Category:</strong> {tool['category']}</p>
                <p>{tool['description']}</p>
                <p><strong>MCP Compatible:</strong> {'✅' if tool.get('mcp_compatible', False) else '❌'}</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"View Details", key=f"view_{tool['id']}"):
                    self._show_tool_details(tool)
            
            with col2:
                if st.button(f"Install", key=f"install_{tool['id']}"):
                    self._install_tool(tool)
    
    def _render_add_tool_form(self):
        """Render form to add new tool"""
        with st.form("add_tool_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Tool Name")
                category = st.selectbox("Category", self.categories)
                description = st.text_area("Description")
            
            with col2:
                parameters = st.text_area("Parameters (JSON)", placeholder='{"param1": "type", "param2": "type"}')
                mcp_compatible = st.checkbox("MCP Compatible")
                dependencies = st.text_area("Dependencies", placeholder="dependency1, dependency2")
            
            implementation = st.text_area("Implementation Code", height=200)
            
            submitted = st.form_submit_button("Add Tool")
            
            if submitted:
                if name and category and description and implementation:
                    self._add_tool({
                        "name": name,
                        "category": category,
                        "description": description,
                        "parameters": parameters,
                        "mcp_compatible": mcp_compatible,
                        "dependencies": dependencies.split(", ") if dependencies else [],
                        "implementation": implementation
                    })
                    st.success(f"Tool '{name}' added successfully!")
                else:
                    st.error("Please fill in all required fields.")
    
    def _show_tool_details(self, tool: Dict[str, Any]):
        """Show detailed information about a tool"""
        st.modal("Tool Details")
        with st.container():
            st.markdown(f"### {tool['name']}")
            st.write(f"**Category:** {tool['category']}")
            st.write(f"**Description:** {tool['description']}")
            st.write(f"**MCP Compatible:** {'Yes' if tool.get('mcp_compatible', False) else 'No'}")
            
            if tool.get('parameters'):
                st.write("**Parameters:**")
                try:
                    params = json.loads(tool['parameters']) if isinstance(tool['parameters'], str) else tool['parameters']
                    st.json(params)
                except:
                    st.write(tool['parameters'])
            
            if tool.get('dependencies'):
                st.write("**Dependencies:**")
                for dep in tool['dependencies']:
                    st.write(f"- {dep}")
            
            if tool.get('implementation'):
                st.write("**Implementation:**")
                st.code(tool['implementation'], language='python')
    
    def _install_tool(self, tool: Dict[str, Any]):
        """Install a tool"""
        # Simulate tool installation
        st.success(f"Tool '{tool['name']}' installed successfully!")
    
    def _filter_tools(self, search_query: str, category_filter: str, mcp_filter: str = "All") -> List[Dict[str, Any]]:
        """Filter tools based on search query, category, and MCP compatibility"""
        filtered = self.tools_data
        
        if search_query:
            filtered = [
                tool for tool in filtered
                if search_query.lower() in tool['name'].lower() or 
                   search_query.lower() in tool['description'].lower()
            ]
        
        if category_filter != "All":
            filtered = [
                tool for tool in filtered
                if tool['category'] == category_filter
            ]
        
        if mcp_filter != "All":
            if mcp_filter == "Yes":
                filtered = [tool for tool in filtered if tool.get('mcp_compatible', False)]
            elif mcp_filter == "No":
                filtered = [tool for tool in filtered if not tool.get('mcp_compatible', False)]
        
        return filtered
    
    def _add_tool(self, tool_data: Dict[str, Any]):
        """Add a new tool to the library"""
        # Generate unique ID
        tool_data['id'] = f"tool_{len(self.tools_data) + 1}"
        
        # Add to tools data
        self.tools_data.append(tool_data)
        
        # Save to file (in a real implementation)
        self._save_tools_data()
    
    def _load_tools_data(self) -> List[Dict[str, Any]]:
        """Load tools data from file or return sample data"""
        # In a real implementation, this would load from a file or database
        return [
            {
                "id": "tool_1",
                "name": "Web Scraper",
                "category": "web_scraping",
                "description": "Advanced web scraping tool with JavaScript support",
                "parameters": '{"url": "string", "selector": "string", "timeout": "int"}',
                "mcp_compatible": True,
                "dependencies": ["requests", "beautifulsoup4", "selenium"],
                "implementation": "def scrape_web(url, selector, timeout=30):\n    # Implementation here\n    pass"
            },
            {
                "id": "tool_2",
                "name": "File Processor",
                "category": "file_operations",
                "description": "Process various file formats with advanced parsing",
                "parameters": '{"file_path": "string", "format": "string"}',
                "mcp_compatible": False,
                "dependencies": ["pandas", "openpyxl"],
                "implementation": "def process_file(file_path, format):\n    # Implementation here\n    pass"
            },
            {
                "id": "tool_3",
                "name": "API Client",
                "category": "api_clients",
                "description": "Generic REST API client with authentication",
                "parameters": '{"base_url": "string", "auth_type": "string", "headers": "dict"}',
                "mcp_compatible": True,
                "dependencies": ["httpx", "requests"],
                "implementation": "class APIClient:\n    def __init__(self, base_url, auth_type, headers):\n        # Implementation here\n        pass"
            },
            {
                "id": "tool_4",
                "name": "Data Analyzer",
                "category": "data_processing",
                "description": "Statistical analysis and visualization tool",
                "parameters": '{"data": "DataFrame", "analysis_type": "string"}',
                "mcp_compatible": False,
                "dependencies": ["pandas", "numpy", "matplotlib", "seaborn"],
                "implementation": "def analyze_data(data, analysis_type):\n    # Implementation here\n    pass"
            }
        ]
    
    def _save_tools_data(self):
        """Save tools data to file"""
        # In a real implementation, this would save to a file or database
        os.makedirs("config", exist_ok=True)
        with open("config/tools.json", "w") as f:
            json.dump(self.tools_data, f, indent=2)
    
    def _get_categories(self) -> List[str]:
        """Get unique categories from tools data"""
        categories = set()
        for tool in self.tools_data:
            categories.add(tool['category'])
        return sorted(list(categories))
    
    def get_tool_by_id(self, tool_id: str) -> Dict[str, Any]:
        """Get tool by ID"""
        for tool in self.tools_data:
            if tool['id'] == tool_id:
                return tool
        return None
    
    def get_tools_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get tools by category"""
        return [tool for tool in self.tools_data if tool['category'] == category]
    
    def get_mcp_compatible_tools(self) -> List[Dict[str, Any]]:
        """Get MCP compatible tools"""
        return [tool for tool in self.tools_data if tool.get('mcp_compatible', False)]
