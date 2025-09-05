"""
State management for the upgrade agent workflow.
"""

from typing import List, Optional
from dataclasses import dataclass

@dataclass
class UpgradeState:
    """State object that flows through the LangGraph workflow."""
    
    # Input parameters
    repository_url: str
    base_branch: str
    target_version: Optional[str]
    llm_model: str
    max_attempts: int
    new_branch_name: Optional[str]
    
    # Workflow state
    current_attempt: int
    recipes: List[str]
    build_errors: List[str]
    workspace_path: str
    build_tool: str  # "maven" or "gradle"
    
    # Project information
    current_java_version: str
    current_spring_boot_version: str
    
    # Output
    pull_request_url: str
    summary_report: str
    
    # Internal tracking
    setup_complete: bool = False
    analysis_complete: bool = False
    openrewrite_installed: bool = False
    build_successful: bool = False
    
    def increment_attempt(self):
        """Increment the troubleshooting attempt counter."""
        self.current_attempt += 1
    
    def add_recipe(self, recipe: str):
        """Add a recipe to the list."""
        if recipe not in self.recipes:
            self.recipes.append(recipe)
    
    def add_build_error(self, error: str):
        """Add a build error to the list."""
        self.build_errors.append(error)
    
    def clear_build_errors(self):
        """Clear the build errors list."""
        self.build_errors = []
    
    def has_reached_max_attempts(self) -> bool:
        """Check if maximum troubleshooting attempts have been reached."""
        return self.current_attempt >= self.max_attempts
