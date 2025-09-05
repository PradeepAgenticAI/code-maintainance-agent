"""
Custom tools for the upgrade agent workflow.
"""

import os
import subprocess
import shutil
import tempfile
import requests
import zipfile
from pathlib import Path
from typing import List, Tuple, Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

class GitTool(BaseTool):
    """Tool for Git operations."""
    
    name = "git_tool"
    description = "Performs Git operations like clone, branch creation, commit, and push"
    
    def _run(self, operation: str, **kwargs) -> str:
        """Execute Git operations."""
        try:
            if operation == "clone":
                return self._clone_repository(kwargs["url"], kwargs["path"])
            elif operation == "create_branch":
                return self._create_branch(kwargs["branch_name"], kwargs["repo_path"])
            elif operation == "commit_and_push":
                return self._commit_and_push(kwargs["repo_path"], kwargs["branch_name"], kwargs["message"])
            else:
                return f"Unknown Git operation: {operation}"
        except Exception as e:
            return f"Git operation failed: {str(e)}"
    
    def _clone_repository(self, url: str, path: str) -> str:
        """Clone a repository."""
        cmd = ["git", "clone", url, path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Failed to clone repository: {result.stderr}")
        return f"Successfully cloned repository to {path}"
    
    def _create_branch(self, branch_name: str, repo_path: str) -> str:
        """Create and checkout a new branch."""
        cmd = ["git", "checkout", "-b", branch_name]
        result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Failed to create branch: {result.stderr}")
        return f"Successfully created and checked out branch: {branch_name}"
    
    def _commit_and_push(self, repo_path: str, branch_name: str, message: str) -> str:
        """Commit changes and push to remote."""
        # Add all changes
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
        
        # Commit changes
        cmd = ["git", "commit", "-m", message]
        result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Failed to commit: {result.stderr}")
        
        # Push branch
        cmd = ["git", "push", "origin", branch_name]
        result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Failed to push: {result.stderr}")
        
        return f"Successfully committed and pushed changes to {branch_name}"

class OpenRewriteTool(BaseTool):
    """Tool for OpenRewrite CLI operations."""
    
    name = "openrewrite_tool"
    description = "Installs OpenRewrite CLI and applies recipes"
    
    def _run(self, operation: str, **kwargs) -> str:
        """Execute OpenRewrite operations."""
        try:
            if operation == "install":
                return self._install_openrewrite()
            elif operation == "apply_recipes":
                return self._apply_recipes(kwargs["repo_path"], kwargs["recipes"])
            else:
                return f"Unknown OpenRewrite operation: {operation}"
        except Exception as e:
            return f"OpenRewrite operation failed: {str(e)}"
    
    def _install_openrewrite(self) -> str:
        """Install OpenRewrite CLI."""
        # Check if already installed
        if shutil.which("rewrite"):
            return "OpenRewrite CLI is already installed"
        
        # Download and install OpenRewrite CLI
        download_url = "https://github.com/openrewrite/rewrite-cli/releases/latest/download/rewrite-cli.zip"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = os.path.join(temp_dir, "rewrite-cli.zip")
            
            # Download
            response = requests.get(download_url)
            response.raise_for_status()
            
            with open(zip_path, "wb") as f:
                f.write(response.content)
            
            # Extract
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Find the executable and copy to a location in PATH
            rewrite_exe = None
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.startswith("rewrite") and (file.endswith(".exe") or file.endswith(".jar")):
                        rewrite_exe = os.path.join(root, file)
                        break
                if rewrite_exe:
                    break
            
            if not rewrite_exe:
                raise Exception("Could not find rewrite executable in downloaded package")
            
            # Copy to a directory in PATH (or create a wrapper script)
            install_dir = os.path.expanduser("~/.local/bin")
            os.makedirs(install_dir, exist_ok=True)
            
            if rewrite_exe.endswith(".jar"):
                # Create a wrapper script for JAR
                wrapper_script = os.path.join(install_dir, "rewrite")
                shutil.copy(rewrite_exe, os.path.join(install_dir, "rewrite.jar"))
                
                with open(wrapper_script, "w") as f:
                    f.write(f"#!/bin/bash\njava -jar {os.path.join(install_dir, 'rewrite.jar')} \"$@\"\n")
                os.chmod(wrapper_script, 0o755)
            else:
                # Copy executable directly
                shutil.copy(rewrite_exe, os.path.join(install_dir, "rewrite"))
                os.chmod(os.path.join(install_dir, "rewrite"), 0o755)
        
        return f"OpenRewrite CLI installed successfully to {install_dir}"
    
    def _apply_recipes(self, repo_path: str, recipes: List[str]) -> str:
        """Apply OpenRewrite recipes to the project."""
        if not recipes:
            return "No recipes to apply"
        
        results = []
        for recipe in recipes:
            cmd = ["rewrite", "run", "--recipe", recipe]
            result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True)
            
            if result.returncode == 0:
                results.append(f"Successfully applied recipe: {recipe}")
            else:
                results.append(f"Failed to apply recipe {recipe}: {result.stderr}")
        
        return "\n".join(results)

class BuildTool(BaseTool):
    """Tool for build operations (Maven/Gradle)."""
    
    name = "build_tool"
    description = "Detects build tool and runs build/test commands"
    
    def _run(self, operation: str, **kwargs) -> str:
        """Execute build operations."""
        try:
            if operation == "detect":
                return self._detect_build_tool(kwargs["repo_path"])
            elif operation == "build_and_test":
                return self._build_and_test(kwargs["repo_path"], kwargs["build_tool"])
            else:
                return f"Unknown build operation: {operation}"
        except Exception as e:
            return f"Build operation failed: {str(e)}"
    
    def _detect_build_tool(self, repo_path: str) -> str:
        """Detect whether project uses Maven or Gradle."""
        pom_xml = os.path.join(repo_path, "pom.xml")
        build_gradle = os.path.join(repo_path, "build.gradle")
        build_gradle_kts = os.path.join(repo_path, "build.gradle.kts")
        
        if os.path.exists(pom_xml):
            return "maven"
        elif os.path.exists(build_gradle) or os.path.exists(build_gradle_kts):
            return "gradle"
        else:
            raise Exception("Could not detect build tool (no pom.xml or build.gradle found)")
    
    def _build_and_test(self, repo_path: str, build_tool: str) -> str:
        """Run build and test commands."""
        if build_tool == "maven":
            cmd = ["mvn", "clean", "verify"]
        elif build_tool == "gradle":
            cmd = ["./gradlew", "clean", "build"] if os.path.exists(os.path.join(repo_path, "gradlew")) else ["gradle", "clean", "build"]
        else:
            raise Exception(f"Unsupported build tool: {build_tool}")
        
        result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True)
        
        output = {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode
        }
        
        return str(output)

class ProjectAnalysisTool(BaseTool):
    """Tool for analyzing project structure and versions."""
    
    name = "project_analysis_tool"
    description = "Analyzes project to extract current Java and Spring Boot versions"
    
    def _run(self, repo_path: str, build_tool: str) -> dict:
        """Analyze project to extract version information."""
        try:
            if build_tool == "maven":
                return self._analyze_maven_project(repo_path)
            elif build_tool == "gradle":
                return self._analyze_gradle_project(repo_path)
            else:
                raise Exception(f"Unsupported build tool: {build_tool}")
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_maven_project(self, repo_path: str) -> dict:
        """Analyze Maven project."""
        pom_path = os.path.join(repo_path, "pom.xml")
        
        if not os.path.exists(pom_path):
            raise Exception("pom.xml not found")
        
        with open(pom_path, 'r') as f:
            pom_content = f.read()
        
        # Extract versions using simple string parsing
        # In a real implementation, you'd use XML parsing
        java_version = self._extract_java_version_from_maven(pom_content)
        spring_boot_version = self._extract_spring_boot_version_from_maven(pom_content)
        
        return {
            "java_version": java_version,
            "spring_boot_version": spring_boot_version,
            "build_file_content": pom_content
        }
    
    def _analyze_gradle_project(self, repo_path: str) -> dict:
        """Analyze Gradle project."""
        build_gradle_path = os.path.join(repo_path, "build.gradle")
        build_gradle_kts_path = os.path.join(repo_path, "build.gradle.kts")
        
        build_file = None
        if os.path.exists(build_gradle_path):
            build_file = build_gradle_path
        elif os.path.exists(build_gradle_kts_path):
            build_file = build_gradle_kts_path
        else:
            raise Exception("No build.gradle or build.gradle.kts found")
        
        with open(build_file, 'r') as f:
            build_content = f.read()
        
        java_version = self._extract_java_version_from_gradle(build_content)
        spring_boot_version = self._extract_spring_boot_version_from_gradle(build_content)
        
        return {
            "java_version": java_version,
            "spring_boot_version": spring_boot_version,
            "build_file_content": build_content
        }
    
    def _extract_java_version_from_maven(self, pom_content: str) -> str:
        """Extract Java version from Maven POM."""
        # Simple regex-based extraction
        import re
        
        patterns = [
            r'<maven\.compiler\.source>(\d+)</maven\.compiler\.source>',
            r'<maven\.compiler\.target>(\d+)</maven\.compiler\.target>',
            r'<java\.version>(\d+)</java\.version>'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, pom_content)
            if match:
                return match.group(1)
        
        return "unknown"
    
    def _extract_spring_boot_version_from_maven(self, pom_content: str) -> str:
        """Extract Spring Boot version from Maven POM."""
        import re
        
        patterns = [
            r'<spring-boot\.version>([^<]+)</spring-boot\.version>',
            r'<version>([^<]+)</version>.*spring-boot-starter-parent',
            r'spring-boot-starter-parent.*<version>([^<]+)</version>'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, pom_content, re.DOTALL)
            if match:
                return match.group(1)
        
        return "unknown"
    
    def _extract_java_version_from_gradle(self, build_content: str) -> str:
        """Extract Java version from Gradle build file."""
        import re
        
        patterns = [
            r'sourceCompatibility\s*=\s*["\']?(\d+)["\']?',
            r'targetCompatibility\s*=\s*["\']?(\d+)["\']?',
            r'java\s*{\s*sourceCompatibility\s*=\s*["\']?(\d+)["\']?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, build_content)
            if match:
                return match.group(1)
        
        return "unknown"
    
    def _extract_spring_boot_version_from_gradle(self, build_content: str) -> str:
        """Extract Spring Boot version from Gradle build file."""
        import re
        
        patterns = [
            r'org\.springframework\.boot["\']?\s*version\s*["\']([^"\']+)["\']',
            r'spring-boot-gradle-plugin["\']?\s*version\s*["\']([^"\']+)["\']'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, build_content)
            if match:
                return match.group(1)
        
        return "unknown"
