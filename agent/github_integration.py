"""
GitHub integration for creating pull requests.
"""

import os
from github import Github
from typing import Dict, Any, Optional

class GitHubIntegration:
    """Handle GitHub API operations."""
    
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("GITHUB_TOKEN environment variable is required")
        
        self.github = Github(self.token)
    
    def create_pull_request(self, 
                          repository_url: str,
                          base_branch: str,
                          feature_branch: str,
                          title: str,
                          body: str) -> Dict[str, Any]:
        """Create a pull request on GitHub."""
        try:
            # Extract repository name from URL
            repo_name = self._extract_repo_name(repository_url)
            
            # Get repository object
            repo = self.github.get_repo(repo_name)
            
            # Create pull request
            pr = repo.create_pull(
                title=title,
                body=body,
                head=feature_branch,
                base=base_branch
            )
            
            return {
                "success": True,
                "pull_request_url": pr.html_url,
                "pull_request_number": pr.number,
                "message": f"Pull request created successfully: {pr.html_url}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "pull_request_url": "",
                "pull_request_number": None,
                "error": str(e),
                "message": f"Failed to create pull request: {str(e)}"
            }
    
    def _extract_repo_name(self, repository_url: str) -> str:
        """Extract repository name from GitHub URL."""
        # Handle both SSH and HTTPS URLs
        if repository_url.startswith("git@github.com:"):
            # SSH format: git@github.com:owner/repo.git
            repo_part = repository_url.replace("git@github.com:", "")
        elif repository_url.startswith("https://github.com/"):
            # HTTPS format: https://github.com/owner/repo.git
            repo_part = repository_url.replace("https://github.com/", "")
        else:
            raise ValueError(f"Unsupported repository URL format: {repository_url}")
        
        # Remove .git suffix if present
        if repo_part.endswith(".git"):
            repo_part = repo_part[:-4]
        
        return repo_part
    
    def generate_pr_title(self, java_version: str, spring_boot_version: str, target_version: str) -> str:
        """Generate a descriptive pull request title."""
        components = []
        
        if java_version and java_version != "unknown":
            if target_version and "java" in target_version.lower():
                components.append(f"Upgrade Java from {java_version} to {target_version}")
            else:
                components.append(f"Upgrade Java from {java_version}")
        
        if spring_boot_version and spring_boot_version != "unknown":
            if target_version and "spring" in target_version.lower():
                components.append(f"Upgrade Spring Boot from {spring_boot_version} to {target_version}")
            else:
                components.append(f"Upgrade Spring Boot from {spring_boot_version}")
        
        if not components:
            return f"Automated upgrade to {target_version}" if target_version else "Automated project upgrade"
        
        return " and ".join(components)
    
    def generate_pr_body(self, summary_report: str, recipes_applied: list, build_attempts: int) -> str:
        """Generate a detailed pull request body."""
        body_parts = [
            "## Automated Java/Spring Boot Upgrade",
            "",
            "This pull request was created by an AI-powered upgrade agent.",
            "",
            "### Summary",
            summary_report,
            "",
            "### OpenRewrite Recipes Applied",
        ]
        
        if recipes_applied:
            for recipe in recipes_applied:
                body_parts.append(f"- `{recipe}`")
        else:
            body_parts.append("- No recipes were applied")
        
        body_parts.extend([
            "",
            f"### Build Attempts: {build_attempts}",
            "",
            "### Review Notes",
            "- ✅ All automated tests passed",
            "- 🔍 Please review the changes carefully before merging",
            "- 📝 Consider running additional manual tests",
            "- 🚀 This upgrade may include breaking changes - check the migration guide",
            "",
            "---",
            "*This PR was generated automatically by the Java/Spring Boot Upgrade Agent*"
        ])
        
        return "\n".join(body_parts)
