import streamlit as st
import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import json
import os

@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    name: str
    type: str
    host: str
    port: int
    username: str
    password: str
    database: str
    ssl_mode: str = "require"

class DatabaseSetup:
    """UI component for database setup and configuration"""
    
    def __init__(self):
        self.config_file = "config/database.json"
        self.configs: Dict[str, DatabaseConfig] = {}
        self._load_configs()
    
    def render(self):
        """Render the database setup UI"""
        st.header("🗄️ Database Setup")
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "Vector Database", 
            "Redis Cache", 
            "PostgreSQL", 
            "Connection Status"
        ])
        
        with tab1:
            self._render_vector_db_setup()
        
        with tab2:
            self._render_redis_setup()
        
        with tab3:
            self._render_postgresql_setup()
        
        with tab4:
            self._render_connection_status()
    
    def _render_vector_db_setup(self):
        """Render vector database setup (Supabase)"""
        st.subheader("Vector Database (Supabase)")
        
        st.info("Supabase is used for vector similarity search in knowledge retrieval.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            supabase_url = st.text_input(
                "Supabase URL",
                value=os.getenv("SUPABASE_URL", ""),
                help="Your Supabase project URL (https://xxx.supabase.co)"
            )
        
        with col2:
            supabase_key = st.text_input(
                "Supabase Anon Key",
                value=os.getenv("SUPABASE_KEY", ""),
                type="password",
                help="Your Supabase anonymous key"
            )
        
        # Advanced Supabase settings
        with st.expander("Advanced Supabase Settings"):
            vector_table = st.text_input(
                "Vector Table Name",
                value="embeddings",
                help="Name of the table storing vector embeddings"
            )
            
            embedding_dimension = st.number_input(
                "Embedding Dimension",
                min_value=512,
                max_value=3072,
                value=1536,
                help="Dimension of the embedding vectors"
            )
            
            similarity_threshold = st.slider(
                "Similarity Threshold",
                min_value=0.0,
                max_value=1.0,
                value=0.8,
                help="Minimum similarity score for search results"
            )
        
        if st.button("Test Supabase Connection"):
            if supabase_url and supabase_key:
                try:
                    # Test connection
                    from supabase import create_client
                    client = create_client(supabase_url, supabase_key)
                    # Simple test query
                    response = client.table("test").select("*").limit(1).execute()
                    st.success("✅ Supabase connection successful!")
                except Exception as e:
                    st.error(f"❌ Supabase connection failed: {str(e)}")
            else:
                st.warning("Please enter both URL and key")
        
        if st.button("Save Supabase Config"):
            config = {
                "url": supabase_url,
                "key": supabase_key,
                "vector_table": vector_table,
                "embedding_dimension": embedding_dimension,
                "similarity_threshold": similarity_threshold
            }
            self._save_config("supabase", config)
            st.success("Supabase configuration saved!")
    
    def _render_redis_setup(self):
        """Render Redis cache setup"""
        st.subheader("Redis Cache")
        
        st.info("Redis is used for caching and session management.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            redis_host = st.text_input(
                "Redis Host",
                value="localhost",
                help="Redis server hostname"
            )
            
            redis_port = st.number_input(
                "Redis Port",
                min_value=1,
                max_value=65535,
                value=6379,
                help="Redis server port"
            )
        
        with col2:
            redis_password = st.text_input(
                "Redis Password",
                value="",
                type="password",
                help="Redis password (leave empty if no auth)"
            )
            
            redis_db = st.number_input(
                "Redis Database",
                min_value=0,
                max_value=15,
                value=0,
                help="Redis database number"
            )
        
        # Advanced Redis settings
        with st.expander("Advanced Redis Settings"):
            max_connections = st.number_input(
                "Max Connections",
                min_value=1,
                max_value=100,
                value=10,
                help="Maximum number of Redis connections"
            )
            
            connection_timeout = st.number_input(
                "Connection Timeout (seconds)",
                min_value=1,
                max_value=60,
                value=5,
                help="Connection timeout in seconds"
            )
            
            enable_ssl = st.checkbox(
                "Enable SSL",
                value=False,
                help="Enable SSL/TLS encryption"
            )
        
        if st.button("Test Redis Connection"):
            try:
                import redis
                r = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    password=redis_password if redis_password else None,
                    db=redis_db,
                    ssl=enable_ssl,
                    socket_connect_timeout=connection_timeout
                )
                r.ping()
                st.success("✅ Redis connection successful!")
            except Exception as e:
                st.error(f"❌ Redis connection failed: {str(e)}")
        
        if st.button("Save Redis Config"):
            config = {
                "host": redis_host,
                "port": redis_port,
                "password": redis_password,
                "db": redis_db,
                "max_connections": max_connections,
                "connection_timeout": connection_timeout,
                "ssl": enable_ssl
            }
            self._save_config("redis", config)
            st.success("Redis configuration saved!")
    
    def _render_postgresql_setup(self):
        """Render PostgreSQL setup"""
        st.subheader("PostgreSQL Database")
        
        st.info("PostgreSQL is used for structured data storage and workflow state.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            pg_host = st.text_input(
                "PostgreSQL Host",
                value="localhost",
                help="PostgreSQL server hostname"
            )
            
            pg_port = st.number_input(
                "PostgreSQL Port",
                min_value=1,
                max_value=65535,
                value=5432,
                help="PostgreSQL server port"
            )
            
            pg_database = st.text_input(
                "Database Name",
                value="agentic_workflow",
                help="Name of the PostgreSQL database"
            )
        
        with col2:
            pg_username = st.text_input(
                "Username",
                value="postgres",
                help="PostgreSQL username"
            )
            
            pg_password = st.text_input(
                "Password",
                value="",
                type="password",
                help="PostgreSQL password"
            )
            
            ssl_mode = st.selectbox(
                "SSL Mode",
                ["disable", "allow", "prefer", "require", "verify-ca", "verify-full"],
                index=3,
                help="SSL mode for PostgreSQL connection"
            )
        
        # Advanced PostgreSQL settings
        with st.expander("Advanced PostgreSQL Settings"):
            max_connections = st.number_input(
                "Max Connections",
                min_value=1,
                max_value=100,
                value=20,
                help="Maximum number of database connections"
            )
            
            connection_timeout = st.number_input(
                "Connection Timeout (seconds)",
                min_value=1,
                max_value=60,
                value=10,
                help="Connection timeout in seconds"
            )
            
            enable_migrations = st.checkbox(
                "Auto-run Migrations",
                value=True,
                help="Automatically run database migrations on startup"
            )
        
        if st.button("Test PostgreSQL Connection"):
            try:
                import psycopg2
                conn = psycopg2.connect(
                    host=pg_host,
                    port=pg_port,
                    database=pg_database,
                    user=pg_username,
                    password=pg_password,
                    sslmode=ssl_mode,
                    connect_timeout=connection_timeout
                )
                conn.close()
                st.success("✅ PostgreSQL connection successful!")
            except Exception as e:
                st.error(f"❌ PostgreSQL connection failed: {str(e)}")
        
        if st.button("Save PostgreSQL Config"):
            config = {
                "host": pg_host,
                "port": pg_port,
                "database": pg_database,
                "username": pg_username,
                "password": pg_password,
                "ssl_mode": ssl_mode,
                "max_connections": max_connections,
                "connection_timeout": connection_timeout,
                "enable_migrations": enable_migrations
            }
            self._save_config("postgresql", config)
            st.success("PostgreSQL configuration saved!")
    
    def _render_connection_status(self):
        """Render connection status for all databases"""
        st.subheader("Connection Status")
        
        # Check all database connections
        databases = ["supabase", "redis", "postgresql"]
        
        for db in databases:
            with st.expander(f"{db.title()} Status"):
                config = self._get_config(db)
                if config:
                    st.json(config)
                    
                    # Connection test button
                    if st.button(f"Test {db.title()} Connection", key=f"test_{db}"):
                        status = self._test_connection(db, config)
                        if status:
                            st.success(f"✅ {db.title()} connection successful!")
                        else:
                            st.error(f"❌ {db.title()} connection failed!")
                else:
                    st.warning(f"No configuration found for {db.title()}")
    
    def _load_configs(self):
        """Load database configurations from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.configs = json.load(f)
            except Exception as e:
                st.error(f"Error loading database configs: {str(e)}")
                self.configs = {}
    
    def _save_config(self, db_name: str, config: Dict[str, Any]):
        """Save database configuration"""
        self.configs[db_name] = config
        
        # Ensure config directory exists
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        with open(self.config_file, 'w') as f:
            json.dump(self.configs, f, indent=2)
    
    def _get_config(self, db_name: str) -> Optional[Dict[str, Any]]:
        """Get database configuration"""
        return self.configs.get(db_name)
    
    def _test_connection(self, db_name: str, config: Dict[str, Any]) -> bool:
        """Test database connection"""
        try:
            if db_name == "supabase":
                from supabase import create_client
                client = create_client(config["url"], config["key"])
                client.table("test").select("*").limit(1).execute()
                return True
            
            elif db_name == "redis":
                import redis
                r = redis.Redis(
                    host=config["host"],
                    port=config["port"],
                    password=config.get("password") if config.get("password") else None,
                    db=config["db"],
                    ssl=config.get("ssl", False),
                    socket_connect_timeout=config.get("connection_timeout", 5)
                )
                r.ping()
                return True
            
            elif db_name == "postgresql":
                import psycopg2
                conn = psycopg2.connect(
                    host=config["host"],
                    port=config["port"],
                    database=config["database"],
                    user=config["username"],
                    password=config["password"],
                    sslmode=config.get("ssl_mode", "prefer"),
                    connect_timeout=config.get("connection_timeout", 10)
                )
                conn.close()
                return True
            
            return False
        except Exception as e:
            st.error(f"Connection test failed: {str(e)}")
            return False
    
    def get_all_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get all database configurations"""
        return self.configs
    
    def is_configured(self, db_name: str) -> bool:
        """Check if database is configured"""
        return db_name in self.configs and bool(self.configs[db_name])
