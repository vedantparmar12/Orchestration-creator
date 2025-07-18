import streamlit as st
import os
from typing import Dict, Any
import json
from dotenv import load_dotenv, set_key

class EnvironmentManager:
    """UI Component for managing environment variables"""
    def __init__(self):
        self.env_file = ".env"
        load_dotenv(self.env_file)

    def render(self):
        """Render the environment manager UI"""
        st.header("🔧 Environment Manager")

        tab1, tab2, tab3 = st.tabs(["API Keys", "Database", "Advanced"])

        with tab1:
            self._render_api_keys()

        with tab2:
            self._render_database_config()

        with tab3:
            self._render_advanced_config()

    def _render_api_keys(self):
        """Render API keys configuration"""
        st.subheader("API Keys Configuration")

        openai_key = st.text_input(
            "OpenAI API Key",
            value=os.getenv("OPENAI_API_KEY", ""),
            type="password",
            help="Your OpenAI API key for GPT models"
        )

        anthropic_key = st.text_input(
            "Anthropic API Key",
            value=os.getenv("ANTHROPIC_API_KEY", ""),
            type="password",
            help="Your Anthropic API key for Claude models"
        )

        google_key = st.text_input(
            "Google API Key",
            value=os.getenv("GOOGLE_API_KEY", ""),
            type="password",
            help="Your Google API key for Gemini models"
        )

        logfire_token = st.text_input(
            "Logfire Token",
            value=os.getenv("LOGFIRE_TOKEN", ""),
            type="password",
            help="Your Pydantic Logfire token for monitoring"
        )

        if st.button("Save API Keys"):
            self._save_env_var("OPENAI_API_KEY", openai_key)
            self._save_env_var("ANTHROPIC_API_KEY", anthropic_key)
            self._save_env_var("GOOGLE_API_KEY", google_key)
            self._save_env_var("LOGFIRE_TOKEN", logfire_token)
            st.success("API keys saved successfully!")

    def _render_database_config(self):
        """Render database configuration"""
        st.subheader("Database Configuration")

        supabase_url = st.text_input(
            "Supabase URL",
            value=os.getenv("SUPABASE_URL", ""),
            help="Your Supabase project URL"
        )

        supabase_key = st.text_input(
            "Supabase Key",
            value=os.getenv("SUPABASE_KEY", ""),
            type="password",
            help="Your Supabase anon key"
        )

        redis_url = st.text_input(
            "Redis URL",
            value=os.getenv("REDIS_URL", "redis://localhost:6379"),
            help="Redis connection URL"
        )

        if st.button("Save Database Config"):
            self._save_env_var("SUPABASE_URL", supabase_url)
            self._save_env_var("SUPABASE_KEY", supabase_key)
            self._save_env_var("REDIS_URL", redis_url)
            st.success("Database configuration saved successfully!")

    def _render_advanced_config(self):
        """Render advanced configuration"""
        st.subheader("Advanced Configuration")

        model_provider = st.selectbox(
            "Default Model Provider",
            ["openai:gpt-4o", "anthropic:claude-3-5-sonnet-20241022", "google:gemini-pro"],
            index=0,
            help="Default model provider for agents"
        )

        max_parallel_agents = st.number_input(
            "Max Parallel Agents",
            min_value=1,
            max_value=10,
            value=int(os.getenv("MAX_PARALLEL_AGENTS", "4")),
            help="Maximum number of agents to run in parallel"
        )

        max_refinement_cycles = st.number_input(
            "Max Refinement Cycles",
            min_value=1,
            max_value=10,
            value=int(os.getenv("MAX_REFINEMENT_CYCLES", "3")),
            help="Maximum number of refinement cycles"
        )

        validation_timeout = st.number_input(
            "Validation Timeout (seconds)",
            min_value=30,
            max_value=600,
            value=int(os.getenv("VALIDATION_TIMEOUT", "300")),
            help="Timeout for validation operations"
        )

        if st.button("Save Advanced Config"):
            self._save_env_var("MODEL_PROVIDER", model_provider)
            self._save_env_var("MAX_PARALLEL_AGENTS", str(max_parallel_agents))
            self._save_env_var("MAX_REFINEMENT_CYCLES", str(max_refinement_cycles))
            self._save_env_var("VALIDATION_TIMEOUT", str(validation_timeout))
            st.success("Advanced configuration saved successfully!")

    def _save_env_var(self, key: str, value: str):
        """Save environment variable to .env file"""
        if value:
            set_key(self.env_file, key, value)
            os.environ[key] = value

    def get_env_status(self) - Dict[str, bool]:
        """Get status of required environment variables"""
        required_vars = [
            "OPENAI_API_KEY",
            "SUPABASE_URL",
            "SUPABASE_KEY"
        ]

        return {
            var: bool(os.getenv(var)) for var in required_vars
        }

    def render_status_indicator(self):
        """Render environment status indicator"""
        status = self.get_env_status()

        st.subheader("Environment Status")

        for var, is_set in status.items():
            if is_set:
                st.success(f"✅ {var}")
            else:
                st.error(f"❌ {var}")

        all_set = all(status.values())
        if all_set:
            st.success("🎉 All required environment variables are configured!")
        else:
            st.warning("⚠️ Some required environment variables are missing.")
