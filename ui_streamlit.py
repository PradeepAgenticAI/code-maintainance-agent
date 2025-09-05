#!/usr/bin/env python3
"""
Streamlit UI for the AI-Powered Java & Spring Boot Upgrader Agent
"""

import streamlit as st
import json
import os
import threading
import time
from typing import Dict, Any
from dotenv import load_dotenv

from agent.workflow import create_upgrade_workflow
from agent.state import UpgradeState

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Java & Spring Boot Upgrader Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def validate_inputs(repo_url: str, base_branch: str, openai_key: str, github_token: str) -> tuple:
    """Validate required inputs."""
    errors = []
    
    if not repo_url.strip():
        errors.append("Repository URL is required")
    elif not (repo_url.startswith("https://github.com/") or repo_url.startswith("git@github.com:")):
        errors.append("Repository URL must be a GitHub URL")
        
    if not base_branch.strip():
        errors.append("Base branch is required")
        
    if not openai_key.strip():
        errors.append("OpenAI API Key is required")
        
    if not github_token.strip():
        errors.append("GitHub Token is required")
    
    return len(errors) == 0, errors

def run_agent_execution(repo_url: str, base_branch: str, target_version: str, 
                       llm_model: str, max_attempts: int, branch_name: str,
                       openai_key: str, github_token: str):
    """Execute the agent workflow."""
    
    # Set environment variables temporarily
    original_openai_key = os.environ.get("OPENAI_API_KEY")
    original_github_token = os.environ.get("GITHUB_TOKEN")
    
    os.environ["OPENAI_API_KEY"] = openai_key
    os.environ["GITHUB_TOKEN"] = github_token

    try:
        # Create initial state
        initial_state = UpgradeState(
            repository_url=repo_url.strip(),
            base_branch=base_branch.strip(),
            target_version=target_version.strip() if target_version.strip() else None,
            llm_model=llm_model,
            max_attempts=max_attempts,
            new_branch_name=branch_name.strip() if branch_name.strip() else None,
            current_attempt=0,
            recipes=[],
            build_errors=[],
            workspace_path="",
            build_tool="",
            current_java_version="",
            current_spring_boot_version="",
            pull_request_url="",
            summary_report=""
        )

        # Create and execute workflow
        workflow = create_upgrade_workflow()
        final_state = workflow.invoke(initial_state)
        
        return final_state, None
        
    except Exception as e:
        return None, str(e)
    
    finally:
        # Restore original environment variables
        if original_openai_key:
            os.environ["OPENAI_API_KEY"] = original_openai_key
        elif "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]
            
        if original_github_token:
            os.environ["GITHUB_TOKEN"] = original_github_token
        elif "GITHUB_TOKEN" in os.environ:
            del os.environ["GITHUB_TOKEN"]

def main():
    """Main Streamlit application."""
    
    # Header
    st.title("🤖 AI-Powered Java & Spring Boot Upgrader Agent")
    st.markdown("""
    This agent automatically upgrades Java and Spring Boot projects using OpenRewrite recipes and AI-powered analysis.
    """)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("📋 Configuration")
        
        # Project settings
        st.subheader("Project Settings")
        repo_url = st.text_input(
            "Repository URL",
            placeholder="https://github.com/owner/repo.git",
            help="GitHub repository URL (HTTPS or SSH)"
        )
        
        base_branch = st.text_input(
            "Base Branch",
            value="main",
            help="Branch to upgrade from"
        )
        
        target_version = st.text_input(
            "Target Version (Optional)",
            placeholder="Java 17, Spring Boot 3.2, etc.",
            help="Desired Java or Spring Boot version"
        )
        
        # Advanced settings
        st.subheader("Advanced Settings")
        llm_model = st.selectbox(
            "LLM Model",
            options=["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
            index=0,
            help="AI model for analysis"
        )
        
        max_attempts = st.slider(
            "Max Troubleshooting Attempts",
            min_value=1,
            max_value=10,
            value=5,
            help="Maximum retry attempts for build fixes"
        )
        
        branch_name = st.text_input(
            "New Branch Name (Optional)",
            placeholder="upgrade-java-springboot",
            help="Name for the feature branch (auto-generated if empty)"
        )
        
        # API credentials
        st.subheader("🔐 API Credentials")
        openai_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Your OpenAI API key"
        )
        
        github_token = st.text_input(
            "GitHub Token",
            type="password",
            help="GitHub Personal Access Token with repo permissions"
        )
        
        # Run button
        run_button = st.button("🚀 Start Upgrade", type="primary", use_container_width=True)
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📊 Execution Status")
        status_container = st.container()
        
    with col2:
        st.subheader("📄 Results")
        results_container = st.container()
    
    # Handle execution
    if run_button:
        # Validate inputs
        is_valid, errors = validate_inputs(repo_url, base_branch, openai_key, github_token)
        
        if not is_valid:
            with status_container:
                st.error("❌ Validation Errors:")
                for error in errors:
                    st.error(f"• {error}")
        else:
            # Initialize session state for tracking execution
            if 'execution_state' not in st.session_state:
                st.session_state.execution_state = 'idle'
            
            # Start execution
            st.session_state.execution_state = 'running'
            
            with status_container:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Progress steps
                steps = [
                    "🚀 Setting up environment and cloning repository...",
                    "🧠 Analyzing project structure and versions...",
                    "🛠️ Applying OpenRewrite recipes...",
                    "⚙️ Building and testing project...",
                    "🩺 Troubleshooting any build issues...",
                    "✅ Finalizing and creating pull request..."
                ]
                
                # Show progress
                for i, step in enumerate(steps):
                    progress_bar.progress((i + 1) / len(steps))
                    status_text.text(step)
                    time.sleep(1)  # Brief pause for visual effect
                
                status_text.text("🔄 Executing agent workflow...")
                
                # Execute the agent
                final_state, error = run_agent_execution(
                    repo_url, base_branch, target_version, llm_model, 
                    max_attempts, branch_name, openai_key, github_token
                )
                
                if error:
                    progress_bar.progress(0)
                    status_text.error(f"❌ Execution failed: {error}")
                    st.session_state.execution_state = 'failed'
                    
                elif final_state:
                    progress_bar.progress(1.0)
                    status_text.success("✅ Agent execution completed successfully!")
                    st.session_state.execution_state = 'completed'
                    st.session_state.final_state = final_state
                    
                    # Show results
                    with results_container:
                        if final_state.pull_request_url:
                            st.success(f"🔗 **Pull Request Created:** {final_state.pull_request_url}")
                            st.markdown(f"[Open Pull Request]({final_state.pull_request_url})")
                        
                        # Results JSON
                        result_data = {
                            "pull_request_url": final_state.pull_request_url,
                            "summary_report": final_state.summary_report,
                            "recipes_applied": final_state.recipes,
                            "build_tool": final_state.build_tool,
                            "java_version": final_state.current_java_version,
                            "spring_boot_version": final_state.current_spring_boot_version,
                            "attempts": final_state.current_attempt
                        }
                        
                        st.subheader("📋 Execution Summary")
                        st.json(result_data)
                        
                        # Summary report
                        if final_state.summary_report:
                            st.subheader("📝 Detailed Report")
                            st.text_area("Summary Report", final_state.summary_report, height=200)
                        
                        # Applied recipes
                        if final_state.recipes:
                            st.subheader("🛠️ Applied Recipes")
                            for recipe in final_state.recipes:
                                st.code(recipe)
    
    # Show examples
    st.markdown("---")
    st.subheader("💡 Example Configurations")
    
    example_col1, example_col2 = st.columns(2)
    
    with example_col1:
        st.markdown("**Spring PetClinic Upgrade:**")
        st.code("""
Repository URL: https://github.com/spring-projects/spring-petclinic.git
Base Branch: main
Target Version: Java 17
        """)
    
    with example_col2:
        st.markdown("**Spring Boot App Upgrade:**")
        st.code("""
Repository URL: https://github.com/your-org/spring-boot-app.git
Base Branch: develop
Target Version: Spring Boot 3.2
        """)
    
    # Instructions
    st.markdown("---")
    st.subheader("📝 Instructions")
    st.markdown("""
    1. **Fill in the configuration** in the sidebar with your repository details
    2. **Add your API credentials** (OpenAI API key and GitHub token)
    3. **Click "Start Upgrade"** to begin the automated upgrade process
    4. **Monitor the progress** and review the results
    5. **Check the pull request** created by the agent
    
    ### 🔒 Security Note
    Your API keys are only used during execution and are not stored anywhere.
    """)

if __name__ == "__main__":
    main()
