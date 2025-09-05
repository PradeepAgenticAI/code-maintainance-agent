#!/usr/bin/env python3
"""
Gradio UI for the AI-Powered Java & Spring Boot Upgrader Agent
"""

import gradio as gr
import json
import os
import threading
import time
from typing import Dict, Any, Generator
from dotenv import load_dotenv

from agent.workflow import create_upgrade_workflow
from agent.state import UpgradeState

# Load environment variables
load_dotenv()

class AgentUI:
    def __init__(self):
        self.current_execution = None
        self.execution_thread = None
        self.progress_messages = []
        self.is_running = False

    def validate_inputs(self, repo_url: str, base_branch: str, openai_key: str, github_token: str) -> tuple:
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
        
        return len(errors) == 0, "; ".join(errors)

    def run_agent(self, repo_url: str, base_branch: str, target_version: str, 
                  llm_model: str, max_attempts: int, branch_name: str,
                  openai_key: str, github_token: str) -> Generator[tuple, None, None]:
        """Run the agent with progress updates."""
        
        # Validate inputs
        is_valid, error_msg = self.validate_inputs(repo_url, base_branch, openai_key, github_token)
        if not is_valid:
            yield f"❌ Validation Error: {error_msg}", "", "", False
            return

        # Set environment variables temporarily
        original_openai_key = os.environ.get("OPENAI_API_KEY")
        original_github_token = os.environ.get("GITHUB_TOKEN")
        
        os.environ["OPENAI_API_KEY"] = openai_key
        os.environ["GITHUB_TOKEN"] = github_token

        try:
            self.is_running = True
            self.progress_messages = []
            
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

            # Create workflow
            workflow = create_upgrade_workflow()
            
            # Track progress through workflow execution
            progress_steps = [
                "🚀 Setting up environment and cloning repository...",
                "🧠 Analyzing project structure and versions...",
                "🛠️ Applying OpenRewrite recipes...",
                "⚙️ Building and testing project...",
                "🩺 Troubleshooting any build issues...",
                "✅ Finalizing and creating pull request..."
            ]
            
            current_step = 0
            
            # Start execution in a separate thread to allow progress updates
            def execute_workflow():
                try:
                    self.current_execution = workflow.invoke(initial_state)
                except Exception as e:
                    self.current_execution = {"error": str(e)}

            self.execution_thread = threading.Thread(target=execute_workflow)
            self.execution_thread.start()
            
            # Provide progress updates while execution is running
            while self.execution_thread.is_alive():
                if current_step < len(progress_steps):
                    progress_msg = progress_steps[current_step]
                    yield progress_msg, "", "", True
                    current_step += 1
                    time.sleep(3)  # Wait between progress updates
                else:
                    yield "🔄 Processing...", "", "", True
                    time.sleep(2)
            
            # Wait for thread to complete
            self.execution_thread.join()
            
            # Process results
            if hasattr(self.current_execution, 'pull_request_url'):
                final_state = self.current_execution
                
                # Prepare results
                result_json = {
                    "pull_request_url": final_state.pull_request_url,
                    "summary_report": final_state.summary_report,
                    "recipes_applied": final_state.recipes,
                    "build_tool": final_state.build_tool,
                    "java_version": final_state.current_java_version,
                    "spring_boot_version": final_state.current_spring_boot_version,
                    "attempts": final_state.current_attempt
                }
                
                success_msg = "✅ Agent execution completed successfully!"
                if final_state.pull_request_url:
                    success_msg += f"\n🔗 Pull Request: {final_state.pull_request_url}"
                
                yield success_msg, json.dumps(result_json, indent=2), final_state.pull_request_url, False
                
            else:
                error_msg = "❌ Agent execution failed"
                if isinstance(self.current_execution, dict) and "error" in self.current_execution:
                    error_msg += f": {self.current_execution['error']}"
                
                yield error_msg, "", "", False

        except Exception as e:
            yield f"❌ Execution failed: {str(e)}", "", "", False
        
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
            
            self.is_running = False

def create_gradio_interface():
    """Create the Gradio interface."""
    agent_ui = AgentUI()
    
    with gr.Blocks(title="Java & Spring Boot Upgrader Agent", theme=gr.themes.Soft()) as interface:
        gr.Markdown("""
        # 🤖 AI-Powered Java & Spring Boot Upgrader Agent
        
        This agent automatically upgrades Java and Spring Boot projects using OpenRewrite recipes and AI-powered analysis.
        """)
        
        with gr.Row():
            with gr.Column(scale=2):
                gr.Markdown("### 📋 Project Configuration")
                
                repo_url = gr.Textbox(
                    label="Repository URL",
                    placeholder="https://github.com/owner/repo.git",
                    info="GitHub repository URL (HTTPS or SSH)"
                )
                
                base_branch = gr.Textbox(
                    label="Base Branch",
                    value="main",
                    placeholder="main",
                    info="Branch to upgrade from"
                )
                
                target_version = gr.Textbox(
                    label="Target Version (Optional)",
                    placeholder="Java 17, Spring Boot 3.2, etc.",
                    info="Desired Java or Spring Boot version"
                )
                
                with gr.Row():
                    llm_model = gr.Dropdown(
                        label="LLM Model",
                        choices=["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
                        value="gpt-4",
                        info="AI model for analysis"
                    )
                    
                    max_attempts = gr.Slider(
                        label="Max Troubleshooting Attempts",
                        minimum=1,
                        maximum=10,
                        value=5,
                        step=1,
                        info="Maximum retry attempts for build fixes"
                    )
                
                branch_name = gr.Textbox(
                    label="New Branch Name (Optional)",
                    placeholder="upgrade-java-springboot",
                    info="Name for the feature branch (auto-generated if empty)"
                )
                
                gr.Markdown("### 🔐 API Credentials")
                
                openai_key = gr.Textbox(
                    label="OpenAI API Key",
                    type="password",
                    placeholder="sk-...",
                    info="Your OpenAI API key"
                )
                
                github_token = gr.Textbox(
                    label="GitHub Token",
                    type="password",
                    placeholder="ghp_...",
                    info="GitHub Personal Access Token with repo permissions"
                )
                
                run_btn = gr.Button("🚀 Start Upgrade", variant="primary", size="lg")
            
            with gr.Column(scale=3):
                gr.Markdown("### 📊 Execution Progress")
                
                progress_output = gr.Textbox(
                    label="Status",
                    lines=3,
                    interactive=False,
                    show_copy_button=True
                )
                
                gr.Markdown("### 📄 Results")
                
                results_output = gr.Code(
                    label="Execution Results (JSON)",
                    language="json",
                    lines=15,
                    interactive=False
                )
                
                pr_link = gr.Textbox(
                    label="Pull Request URL",
                    interactive=False,
                    show_copy_button=True
                )
                
                # Hidden component to track if agent is running
                is_running = gr.State(False)
        
        # Event handlers
        run_btn.click(
            fn=agent_ui.run_agent,
            inputs=[repo_url, base_branch, target_version, llm_model, max_attempts, 
                   branch_name, openai_key, github_token],
            outputs=[progress_output, results_output, pr_link, is_running],
            show_progress=True
        )
        
        # Add examples
        gr.Markdown("### 💡 Example Configurations")
        
        examples = gr.Examples(
            examples=[
                [
                    "https://github.com/spring-projects/spring-petclinic.git",
                    "main",
                    "Java 17",
                    "gpt-4",
                    5,
                    "upgrade-to-java17",
                    "",
                    ""
                ],
                [
                    "https://github.com/your-org/spring-boot-app.git",
                    "develop",
                    "Spring Boot 3.2",
                    "gpt-4",
                    3,
                    "upgrade-springboot-3.2",
                    "",
                    ""
                ]
            ],
            inputs=[repo_url, base_branch, target_version, llm_model, max_attempts, 
                   branch_name, openai_key, github_token]
        )
        
        gr.Markdown("""
        ### 📝 Instructions
        1. **Fill in the project configuration** with your repository details
        2. **Add your API credentials** (OpenAI API key and GitHub token)
        3. **Click "Start Upgrade"** to begin the automated upgrade process
        4. **Monitor the progress** in real-time
        5. **Review the pull request** created by the agent
        
        ### 🔒 Security Note
        Your API keys are only used during execution and are not stored anywhere.
        """)
    
    return interface

def main():
    """Launch the Gradio interface."""
    interface = create_gradio_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        show_tips=True
    )

if __name__ == "__main__":
    main()
