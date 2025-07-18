import streamlit as st
from typing import Dict, List, Any
import json
import os

class MCPConfigUI:
    """UI component for MCP configuration interface"""
    
    def __init__(self):
        self.config_file = "config/mcp_config.json"
        self.mcp_config = self._load_mcp_config()
    
    def render(self):
        """Render the MCP configuration UI"""
        st.header("🔗 MCP Configuration")
        
        tab1, tab2, tab3 = st.tabs(["Server Configuration", "Tool Mappings", "Client Settings"])
        
        with tab1:
            self._render_server_config()
        
        with tab2:
            self._render_tool_mappings()
        
        with tab3:
            self._render_client_settings()
    
    def _render_server_config(self):
        """Render MCP server configuration"""
        st.subheader("MCP Server Configuration")
        
        # Server basic settings
        col1, col2 = st.columns(2)
        
        with col1:
            server_name = st.text_input(
                "Server Name",
                value=self.mcp_config.get("server_name", "enhanced-agentic-workflow"),
                help="Name of the MCP server"
            )
            
            server_version = st.text_input(
                "Server Version",
                value=self.mcp_config.get("server_version", "1.0.0"),
                help="Version of the MCP server"
            )
            
            server_description = st.text_area(
                "Server Description",
                value=self.mcp_config.get("server_description", "Enhanced Agentic Workflow MCP Server"),
                help="Description of the MCP server"
            )
        
        with col2:
            server_port = st.number_input(
                "Server Port",
                min_value=1000,
                max_value=65535,
                value=self.mcp_config.get("server_port", 8080),
                help="Port for the MCP server"
            )
            
            enable_logging = st.checkbox(
                "Enable Logging",
                value=self.mcp_config.get("enable_logging", True),
                help="Enable server logging"
            )
            
            log_level = st.selectbox(
                "Log Level",
                ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                index=1,
                help="Server log level"
            )
        
        # Server capabilities
        st.subheader("Server Capabilities")
        
        col1, col2 = st.columns(2)
        
        with col1:
            capabilities = st.multiselect(
                "Supported Capabilities",
                ["tools", "resources", "prompts", "sampling"],
                default=self.mcp_config.get("capabilities", ["tools", "resources"]),
                help="Capabilities supported by the server"
            )
        
        with col2:
            max_connections = st.number_input(
                "Max Concurrent Connections",
                min_value=1,
                max_value=100,
                value=self.mcp_config.get("max_connections", 10),
                help="Maximum number of concurrent connections"
            )
        
        # Save server configuration
        if st.button("Save Server Configuration"):
            self.mcp_config.update({
                "server_name": server_name,
                "server_version": server_version,
                "server_description": server_description,
                "server_port": server_port,
                "enable_logging": enable_logging,
                "log_level": log_level,
                "capabilities": capabilities,
                "max_connections": max_connections
            })
            self._save_mcp_config()
            st.success("Server configuration saved successfully!")
    
    def _render_tool_mappings(self):
        """Render tool mappings configuration"""
        st.subheader("Tool Mappings")
        
        # Display existing mappings
        tool_mappings = self.mcp_config.get("tool_mappings", {})
        
        if tool_mappings:
            st.write("**Current Tool Mappings:**")
            for tool_name, mapping in tool_mappings.items():
                with st.expander(f"🔧 {tool_name}"):
                    st.json(mapping)
                    if st.button(f"Remove {tool_name}", key=f"remove_{tool_name}"):
                        del tool_mappings[tool_name]
                        self.mcp_config["tool_mappings"] = tool_mappings
                        self._save_mcp_config()
                        st.rerun()
        else:
            st.info("No tool mappings configured yet.")
        
        # Add new tool mapping
        st.subheader("Add New Tool Mapping")
        
        with st.form("add_tool_mapping"):
            col1, col2 = st.columns(2)
            
            with col1:
                tool_name = st.text_input("Tool Name")
                tool_description = st.text_area("Tool Description")
                tool_schema = st.text_area(
                    "Tool Schema (JSON)",
                    placeholder='{"type": "object", "properties": {"param1": {"type": "string"}}}',
                    height=150
                )
            
            with col2:
                handler_function = st.text_input("Handler Function")
                timeout = st.number_input("Timeout (seconds)", min_value=1, max_value=300, value=30)
                enabled = st.checkbox("Enabled", value=True)
            
            submitted = st.form_submit_button("Add Tool Mapping")
            
            if submitted:
                if tool_name and tool_description and handler_function:
                    try:
                        schema = json.loads(tool_schema) if tool_schema else {}
                        
                        new_mapping = {
                            "description": tool_description,
                            "schema": schema,
                            "handler": handler_function,
                            "timeout": timeout,
                            "enabled": enabled
                        }
                        
                        if "tool_mappings" not in self.mcp_config:
                            self.mcp_config["tool_mappings"] = {}
                        
                        self.mcp_config["tool_mappings"][tool_name] = new_mapping
                        self._save_mcp_config()
                        st.success(f"Tool mapping for '{tool_name}' added successfully!")
                        st.rerun()
                        
                    except json.JSONDecodeError:
                        st.error("Invalid JSON in tool schema")
                else:
                    st.error("Please fill in all required fields")
    
    def _render_client_settings(self):
        """Render client settings configuration"""
        st.subheader("Client Settings")
        
        # Connection settings
        st.subheader("Connection Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            connection_timeout = st.number_input(
                "Connection Timeout (seconds)",
                min_value=1,
                max_value=60,
                value=self.mcp_config.get("connection_timeout", 30),
                help="Timeout for client connections"
            )
            
            retry_attempts = st.number_input(
                "Retry Attempts",
                min_value=0,
                max_value=10,
                value=self.mcp_config.get("retry_attempts", 3),
                help="Number of retry attempts on failure"
            )
        
        with col2:
            keep_alive = st.checkbox(
                "Keep Alive",
                value=self.mcp_config.get("keep_alive", True),
                help="Keep connection alive"
            )
            
            heartbeat_interval = st.number_input(
                "Heartbeat Interval (seconds)",
                min_value=1,
                max_value=300,
                value=self.mcp_config.get("heartbeat_interval", 60),
                help="Interval for heartbeat messages"
            )
        
        # Security settings
        st.subheader("Security Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            enable_tls = st.checkbox(
                "Enable TLS",
                value=self.mcp_config.get("enable_tls", False),
                help="Enable TLS encryption"
            )
            
            if enable_tls:
                cert_file = st.text_input(
                    "Certificate File",
                    value=self.mcp_config.get("cert_file", ""),
                    help="Path to TLS certificate file"
                )
                
                key_file = st.text_input(
                    "Key File",
                    value=self.mcp_config.get("key_file", ""),
                    help="Path to TLS key file"
                )
        
        with col2:
            require_auth = st.checkbox(
                "Require Authentication",
                value=self.mcp_config.get("require_auth", False),
                help="Require client authentication"
            )
            
            if require_auth:
                auth_token = st.text_input(
                    "Authentication Token",
                    value=self.mcp_config.get("auth_token", ""),
                    type="password",
                    help="Authentication token for clients"
                )
        
        # Performance settings
        st.subheader("Performance Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            max_request_size = st.number_input(
                "Max Request Size (MB)",
                min_value=1,
                max_value=100,
                value=self.mcp_config.get("max_request_size", 10),
                help="Maximum request size in megabytes"
            )
        
        with col2:
            rate_limit = st.number_input(
                "Rate Limit (requests/minute)",
                min_value=1,
                max_value=1000,
                value=self.mcp_config.get("rate_limit", 100),
                help="Rate limit for requests per minute"
            )
        
        # Save client settings
        if st.button("Save Client Settings"):
            self.mcp_config.update({
                "connection_timeout": connection_timeout,
                "retry_attempts": retry_attempts,
                "keep_alive": keep_alive,
                "heartbeat_interval": heartbeat_interval,
                "enable_tls": enable_tls,
                "require_auth": require_auth,
                "max_request_size": max_request_size,
                "rate_limit": rate_limit
            })
            
            if enable_tls:
                self.mcp_config.update({
                    "cert_file": cert_file,
                    "key_file": key_file
                })
            
            if require_auth:
                self.mcp_config["auth_token"] = auth_token
            
            self._save_mcp_config()
            st.success("Client settings saved successfully!")
        
        # Configuration export/import
        st.divider()
        st.subheader("Configuration Export/Import")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Export Configuration"):
                config_json = json.dumps(self.mcp_config, indent=2)
                st.download_button(
                    label="Download Configuration",
                    data=config_json,
                    file_name="mcp_config.json",
                    mime="application/json"
                )
        
        with col2:
            uploaded_file = st.file_uploader(
                "Import Configuration",
                type="json",
                help="Upload a JSON configuration file"
            )
            
            if uploaded_file is not None:
                try:
                    config_data = json.load(uploaded_file)
                    self.mcp_config.update(config_data)
                    self._save_mcp_config()
                    st.success("Configuration imported successfully!")
                    st.rerun()
                except json.JSONDecodeError:
                    st.error("Invalid JSON file")
    
    def _load_mcp_config(self) -> Dict[str, Any]:
        """Load MCP configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                st.error(f"Error loading MCP config: {str(e)}")
                return self._get_default_config()
        else:
            return self._get_default_config()
    
    def _save_mcp_config(self):
        """Save MCP configuration to file"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.mcp_config, f, indent=2)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default MCP configuration"""
        return {
            "server_name": "enhanced-agentic-workflow",
            "server_version": "1.0.0",
            "server_description": "Enhanced Agentic Workflow MCP Server",
            "server_port": 8080,
            "enable_logging": True,
            "log_level": "INFO",
            "capabilities": ["tools", "resources"],
            "max_connections": 10,
            "tool_mappings": {},
            "connection_timeout": 30,
            "retry_attempts": 3,
            "keep_alive": True,
            "heartbeat_interval": 60,
            "enable_tls": False,
            "require_auth": False,
            "max_request_size": 10,
            "rate_limit": 100
        }
    
    def get_config(self) -> Dict[str, Any]:
        """Get current MCP configuration"""
        return self.mcp_config
    
    def validate_config(self) -> List[str]:
        """Validate MCP configuration and return any errors"""
        errors = []
        
        # Validate required fields
        required_fields = ["server_name", "server_version", "server_port"]
        for field in required_fields:
            if field not in self.mcp_config:
                errors.append(f"Missing required field: {field}")
        
        # Validate port range
        port = self.mcp_config.get("server_port", 0)
        if not (1000 <= port <= 65535):
            errors.append("Server port must be between 1000 and 65535")
        
        # Validate capabilities
        valid_capabilities = ["tools", "resources", "prompts", "sampling"]
        capabilities = self.mcp_config.get("capabilities", [])
        for cap in capabilities:
            if cap not in valid_capabilities:
                errors.append(f"Invalid capability: {cap}")
        
        # Validate tool mappings
        tool_mappings = self.mcp_config.get("tool_mappings", {})
        for tool_name, mapping in tool_mappings.items():
            if not isinstance(mapping, dict):
                errors.append(f"Invalid mapping for tool: {tool_name}")
            elif "handler" not in mapping:
                errors.append(f"Missing handler for tool: {tool_name}")
        
        return errors
