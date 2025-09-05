#!/usr/bin/env python3
"""
AI-Powered Java & Spring Boot Upgrader Agent
Main entry point for the autonomous upgrade agent.
"""

import argparse
import json
import os
import sys
from typing import Dict, Any

from dotenv import load_dotenv
from agent.workflow import create_upgrade_workflow
from agent.state import UpgradeState

# Load environment variables
load_dotenv()

def parse_arguments() -> Dict[str, Any]:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="AI-Powered Java & Spring Boot Upgrader Agent"
    )
    
    # Required arguments
    parser.add_argument(
        "--repository-url",
        required=True,
        help="SSH or HTTPS URL of the Git repository"
    )
    parser.add_argument(
        "--base-branch",
        required=True,
        help="Starting branch to work from (e.g., main)"
    )
    
    # Optional arguments
    parser.add_argument(
        "--target-version",
        help="Desired Java or Spring Boot version"
    )
    parser.add_argument(
        "--llm-model",
        default="gpt-4",
        help="LLM model to use (default: gpt-4)"
    )
    parser.add_argument(
        "--max-attempts",
        type=int,
        default=5,
        help="Maximum troubleshooting attempts (default: 5)"
    )
    parser.add_argument(
        "--new-branch-name",
        help="Name for the new feature branch"
    )
    
    return vars(parser.parse_args())

def validate_environment():
    """Validate required environment variables and tools."""
    required_env_vars = [
        "OPENAI_API_KEY",
        "GITHUB_TOKEN"
    ]
    
    missing_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these environment variables before running the agent.")
        sys.exit(1)

def main():
    """Main execution function."""
    try:
        # Validate environment
        validate_environment()
        
        # Parse arguments
        args = parse_arguments()
        
        # Create initial state
        initial_state = UpgradeState(
            repository_url=args["repository_url"],
            base_branch=args["base_branch"],
            target_version=args.get("target_version"),
            llm_model=args["llm_model"],
            max_attempts=args["max_attempts"],
            new_branch_name=args.get("new_branch_name"),
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
        
        # Create and run workflow
        workflow = create_upgrade_workflow()
        
        # Execute the workflow
        final_state = workflow.invoke(initial_state)
        
        # Output final result
        result = {
            "pull_request_url": final_state.pull_request_url,
            "summary_report": final_state.summary_report
        }
        
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        error_result = {
            "error": str(e),
            "pull_request_url": "",
            "summary_report": f"Agent failed with error: {str(e)}"
        }
        print(json.dumps(error_result, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()
