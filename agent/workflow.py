"""
LangGraph workflow implementation for the upgrade agent.
"""

import os
import tempfile
import json
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langchain.tools import BaseTool

from .state import UpgradeState
from .tools import GitTool, OpenRewriteTool, BuildTool, ProjectAnalysisTool
from .llm_chains import UpgradeAnalysisChain, TroubleshootingChain
from .github_integration import GitHubIntegration

def setup_node(state: UpgradeState) -> UpgradeState:
    """Setup node: Install OpenRewrite CLI and clone repository."""
    print("🚀 Starting setup phase...")
    
    # Install OpenRewrite CLI
    openrewrite_tool = OpenRewriteTool()
    install_result = openrewrite_tool._run("install")
    print(f"OpenRewrite installation: {install_result}")
    state.openrewrite_installed = True
    
    # Create temporary workspace
    workspace = tempfile.mkdtemp(prefix="upgrade_agent_")
    state.workspace_path = workspace
    
    # Generate branch name if not provided
    if not state.new_branch_name:
        state.new_branch_name = f"upgrade-java-springboot-{state.target_version or 'latest'}"
    
    # Clone repository
    git_tool = GitTool()
    clone_result = git_tool._run("clone", url=state.repository_url, path=workspace)
    print(f"Repository clone: {clone_result}")
    
    # Create new branch
    branch_result = git_tool._run("create_branch", 
                                 branch_name=state.new_branch_name, 
                                 repo_path=workspace)
    print(f"Branch creation: {branch_result}")
    
    state.setup_complete = True
    return state

def analysis_node(state: UpgradeState) -> UpgradeState:
    """Analysis node: Detect build tool and analyze project."""
    print("🧠 Starting analysis phase...")
    
    # Detect build tool
    build_tool = BuildTool()
    build_tool_result = build_tool._run("detect", repo_path=state.workspace_path)
    state.build_tool = build_tool_result
    print(f"Detected build tool: {state.build_tool}")
    
    # Analyze project
    analysis_tool = ProjectAnalysisTool()
    project_info = analysis_tool._run(state.workspace_path, state.build_tool)
    
    if "error" in project_info:
        print(f"Project analysis error: {project_info['error']}")
        state.summary_report = f"Analysis failed: {project_info['error']}"
        return state
    
    state.current_java_version = project_info.get("java_version", "unknown")
    state.current_spring_boot_version = project_info.get("spring_boot_version", "unknown")
    
    print(f"Current Java version: {state.current_java_version}")
    print(f"Current Spring Boot version: {state.current_spring_boot_version}")
    
    # Create upgrade strategy using LLM
    analysis_chain = UpgradeAnalysisChain(state.llm_model)
    
    analysis_input = {
        "build_tool": state.build_tool,
        "current_java_version": state.current_java_version,
        "current_spring_boot_version": state.current_spring_boot_version,
        "target_version": state.target_version or "latest stable",
        "build_file_content": project_info.get("build_file_content", "")[:2000]  # Truncate for token limits
    }
    
    strategy_result = analysis_chain.analyze_project(analysis_input)
    
    if strategy_result["success"]:
        print(f"Upgrade strategy created with {len(strategy_result['recipes'])} recipes")
        state.recipes = strategy_result["recipes"]
        state.summary_report = strategy_result["strategy"]
    else:
        print(f"Strategy creation failed: {strategy_result.get('error', 'Unknown error')}")
        state.summary_report = f"Strategy creation failed: {strategy_result.get('error', 'Unknown error')}"
    
    state.analysis_complete = True
    return state

def apply_recipes_node(state: UpgradeState) -> UpgradeState:
    """Apply Recipes node: Execute OpenRewrite recipes."""
    print(f"🛠️ Applying {len(state.recipes)} recipes...")
    
    if not state.recipes:
        print("No recipes to apply")
        return state
    
    openrewrite_tool = OpenRewriteTool()
    apply_result = openrewrite_tool._run("apply_recipes", 
                                        repo_path=state.workspace_path, 
                                        recipes=state.recipes)
    
    print(f"Recipe application result: {apply_result}")
    return state

def verification_node(state: UpgradeState) -> UpgradeState:
    """Verification node: Build and test the project."""
    print("⚙️ Starting verification phase...")
    
    # Clear previous build errors
    state.clear_build_errors()
    
    # Run build and test
    build_tool = BuildTool()
    build_result_str = build_tool._run("build_and_test", 
                                      repo_path=state.workspace_path, 
                                      build_tool=state.build_tool)
    
    # Parse build result
    try:
        build_result = eval(build_result_str)  # Convert string representation back to dict
        state.build_successful = build_result["success"]
        
        if not state.build_successful:
            # Extract errors from stderr
            stderr = build_result.get("stderr", "")
            if stderr:
                state.add_build_error(stderr)
            
            print(f"Build failed with {len(state.build_errors)} errors")
        else:
            print("Build successful!")
            
    except Exception as e:
        print(f"Error parsing build result: {e}")
        state.build_successful = False
        state.add_build_error(f"Build result parsing error: {e}")
    
    return state

def should_troubleshoot(state: UpgradeState) -> str:
    """Router function to determine next step after verification."""
    if state.build_successful:
        return "finalization"
    elif state.has_reached_max_attempts():
        print(f"Maximum attempts ({state.max_attempts}) reached. Moving to finalization with errors.")
        return "finalization"
    else:
        return "troubleshooting"

def troubleshooting_node(state: UpgradeState) -> UpgradeState:
    """Troubleshooting node: Generate fixes for build errors."""
    print(f"🩺 Starting troubleshooting phase (attempt {state.current_attempt + 1}/{state.max_attempts})...")
    
    state.increment_attempt()
    
    if not state.build_errors:
        print("No build errors to troubleshoot")
        return state
    
    # Use LLM to generate fix
    troubleshooting_chain = TroubleshootingChain(state.llm_model)
    
    error_info = {
        "build_errors": "\n".join(state.build_errors),
        "build_tool": state.build_tool,
        "java_version": state.current_java_version,
        "spring_boot_version": state.current_spring_boot_version
    }
    
    fix_result = troubleshooting_chain.generate_fix(error_info)
    
    if fix_result["success"] and fix_result["recipe"]:
        print(f"Generated fix recipe: {fix_result['recipe']}")
        state.add_recipe(fix_result["recipe"])
    else:
        print(f"Failed to generate fix: {fix_result.get('error', 'Unknown error')}")
    
    return state

def finalization_node(state: UpgradeState) -> UpgradeState:
    """Finalization node: Commit changes and create pull request."""
    print("✅ Starting finalization phase...")
    
    # Commit and push changes
    git_tool = GitTool()
    commit_message = f"Automated upgrade: Java {state.current_java_version} -> {state.target_version or 'latest'}"
    
    try:
        commit_result = git_tool._run("commit_and_push",
                                     repo_path=state.workspace_path,
                                     branch_name=state.new_branch_name,
                                     message=commit_message)
        print(f"Commit and push: {commit_result}")
    except Exception as e:
        print(f"Commit/push failed: {e}")
        state.summary_report += f"\nCommit/push failed: {e}"
    
    # Create pull request
    try:
        github_integration = GitHubIntegration()
        
        pr_title = github_integration.generate_pr_title(
            state.current_java_version,
            state.current_spring_boot_version,
            state.target_version or "latest"
        )
        
        pr_body = github_integration.generate_pr_body(
            state.summary_report,
            state.recipes,
            state.current_attempt
        )
        
        pr_result = github_integration.create_pull_request(
            repository_url=state.repository_url,
            base_branch=state.base_branch,
            feature_branch=state.new_branch_name,
            title=pr_title,
            body=pr_body
        )
        
        if pr_result["success"]:
            state.pull_request_url = pr_result["pull_request_url"]
            print(f"Pull request created: {state.pull_request_url}")
        else:
            print(f"Pull request creation failed: {pr_result['message']}")
            state.summary_report += f"\nPull request creation failed: {pr_result['message']}"
            
    except Exception as e:
        print(f"GitHub integration failed: {e}")
        state.summary_report += f"\nGitHub integration failed: {e}"
    
    # Clean up workspace
    try:
        import shutil
        shutil.rmtree(state.workspace_path)
        print("Workspace cleaned up")
    except Exception as e:
        print(f"Workspace cleanup failed: {e}")
    
    return state

def create_upgrade_workflow() -> StateGraph:
    """Create the LangGraph workflow for the upgrade agent."""
    
    # Create the graph
    workflow = StateGraph(UpgradeState)
    
    # Add nodes
    workflow.add_node("setup", setup_node)
    workflow.add_node("analysis", analysis_node)
    workflow.add_node("apply_recipes", apply_recipes_node)
    workflow.add_node("verification", verification_node)
    workflow.add_node("troubleshooting", troubleshooting_node)
    workflow.add_node("finalization", finalization_node)
    
    # Add edges
    workflow.add_edge("setup", "analysis")
    workflow.add_edge("analysis", "apply_recipes")
    workflow.add_edge("apply_recipes", "verification")
    
    # Conditional edge after verification
    workflow.add_conditional_edges(
        "verification",
        should_troubleshoot,
        {
            "troubleshooting": "troubleshooting",
            "finalization": "finalization"
        }
    )
    
    # Loop back from troubleshooting to apply_recipes
    workflow.add_edge("troubleshooting", "apply_recipes")
    
    # End after finalization
    workflow.add_edge("finalization", END)
    
    # Set entry point
    workflow.set_entry_point("setup")
    
    return workflow.compile()
