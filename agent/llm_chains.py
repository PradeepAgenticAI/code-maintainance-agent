"""
LLM chains for analysis and recipe generation.
"""

from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.chains import LLMChain
from typing import List, Dict, Any
import os

class UpgradeAnalysisChain:
    """Chain for analyzing projects and creating upgrade strategies."""
    
    def __init__(self, model_name: str = "gpt-4"):
        self.llm = ChatOpenAI(
            model_name=model_name,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.1
        )
        
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert Java and Spring Boot upgrade specialist. 
            Analyze the provided project information and create a comprehensive upgrade strategy.
            
            Focus on:
            1. Current versions vs target versions
            2. Breaking changes and compatibility issues
            3. Required OpenRewrite recipes
            4. Potential risks and mitigation strategies
            
            Provide your response in a structured format with specific OpenRewrite recipes."""),
            ("human", """
            Project Analysis:
            - Build Tool: {build_tool}
            - Current Java Version: {current_java_version}
            - Current Spring Boot Version: {current_spring_boot_version}
            - Target Version: {target_version}
            - Build File Content: {build_file_content}
            
            Please provide:
            1. Upgrade strategy summary
            2. List of OpenRewrite recipes to apply
            3. Potential issues to watch for
            """)
        ])
        
        self.analysis_chain = LLMChain(
            llm=self.llm,
            prompt=self.analysis_prompt
        )
    
    def analyze_project(self, project_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze project and generate upgrade strategy."""
        try:
            result = self.analysis_chain.run(**project_info)
            
            # Parse the result to extract recipes
            recipes = self._extract_recipes_from_analysis(result)
            
            return {
                "strategy": result,
                "recipes": recipes,
                "success": True
            }
        except Exception as e:
            return {
                "strategy": f"Analysis failed: {str(e)}",
                "recipes": [],
                "success": False,
                "error": str(e)
            }
    
    def _extract_recipes_from_analysis(self, analysis_text: str) -> List[str]:
        """Extract OpenRewrite recipes from analysis text."""
        recipes = []
        
        # Common recipes based on upgrade patterns
        if "java" in analysis_text.lower():
            if "11" in analysis_text or "17" in analysis_text or "21" in analysis_text:
                recipes.extend([
                    "org.openrewrite.java.migrate.UpgradeToJava11",
                    "org.openrewrite.java.migrate.UpgradeToJava17",
                    "org.openrewrite.java.migrate.UpgradeToJava21"
                ])
        
        if "spring boot" in analysis_text.lower():
            recipes.extend([
                "org.openrewrite.java.spring.boot2.UpgradeSpringBoot_2_7",
                "org.openrewrite.java.spring.boot3.UpgradeSpringBoot_3_0",
                "org.openrewrite.java.spring.boot3.UpgradeSpringBoot_3_1",
                "org.openrewrite.java.spring.boot3.UpgradeSpringBoot_3_2"
            ])
        
        # Extract any explicitly mentioned recipes
        import re
        recipe_pattern = r'org\.openrewrite\.[a-zA-Z0-9._]+'
        found_recipes = re.findall(recipe_pattern, analysis_text)
        recipes.extend(found_recipes)
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(recipes))

class TroubleshootingChain:
    """Chain for generating custom OpenRewrite recipes from build errors."""
    
    def __init__(self, model_name: str = "gpt-4"):
        self.llm = ChatOpenAI(
            model_name=model_name,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.1
        )
        
        self.troubleshooting_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert in OpenRewrite recipes and Java/Spring Boot migration issues.
            Given build errors, create a custom OpenRewrite recipe to fix the specific issues.
            
            Focus on:
            1. Understanding the root cause of the error
            2. Creating targeted fixes using OpenRewrite patterns
            3. Avoiding overly broad changes that might break other code
            
            Provide a specific OpenRewrite recipe or transformation that addresses the error."""),
            ("human", """
            Build Errors:
            {build_errors}
            
            Project Context:
            - Build Tool: {build_tool}
            - Java Version: {java_version}
            - Spring Boot Version: {spring_boot_version}
            
            Please provide:
            1. Analysis of the error
            2. A custom OpenRewrite recipe or specific transformation
            3. Explanation of the fix
            """)
        ])
        
        self.troubleshooting_chain = LLMChain(
            llm=self.llm,
            prompt=self.troubleshooting_prompt
        )
    
    def generate_fix(self, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a custom fix for build errors."""
        try:
            result = self.troubleshooting_chain.run(**error_info)
            
            # Extract recipe from the result
            recipe = self._extract_recipe_from_fix(result)
            
            return {
                "analysis": result,
                "recipe": recipe,
                "success": True
            }
        except Exception as e:
            return {
                "analysis": f"Troubleshooting failed: {str(e)}",
                "recipe": "",
                "success": False,
                "error": str(e)
            }
    
    def _extract_recipe_from_fix(self, fix_text: str) -> str:
        """Extract recipe name from fix analysis."""
        # Look for OpenRewrite recipe patterns
        import re
        recipe_pattern = r'org\.openrewrite\.[a-zA-Z0-9._]+'
        recipes = re.findall(recipe_pattern, fix_text)
        
        if recipes:
            return recipes[0]
        
        # If no standard recipe found, create a generic custom recipe name
        return "custom.fix.BuildErrorFix"

class RecipeGeneratorChain:
    """Chain for generating custom OpenRewrite recipes."""
    
    def __init__(self, model_name: str = "gpt-4"):
        self.llm = ChatOpenAI(
            model_name=model_name,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.2
        )
        
        self.recipe_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert OpenRewrite recipe developer.
            Create a custom OpenRewrite recipe in YAML format to address specific code transformation needs.
            
            The recipe should:
            1. Be syntactically correct OpenRewrite YAML
            2. Target the specific issue described
            3. Include proper metadata (name, displayName, description)
            4. Use appropriate visitors and preconditions
            """),
            ("human", """
            Create an OpenRewrite recipe to fix this issue:
            {issue_description}
            
            Context:
            - Error Details: {error_details}
            - Project Type: {project_type}
            - Target Framework: {target_framework}
            
            Please provide a complete OpenRewrite recipe in YAML format.
            """)
        ])
        
        self.recipe_chain = LLMChain(
            llm=self.llm,
            prompt=self.recipe_prompt
        )
    
    def generate_custom_recipe(self, recipe_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a custom OpenRewrite recipe."""
        try:
            result = self.recipe_chain.run(**recipe_info)
            
            return {
                "recipe_yaml": result,
                "success": True
            }
        except Exception as e:
            return {
                "recipe_yaml": "",
                "success": False,
                "error": str(e)
            }
