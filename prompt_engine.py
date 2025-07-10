import re
import json
from typing import Dict, List, Optional

class PromptEngine:
    def __init__(self):
        self.templates = self._load_templates()
        self.components = self._load_components()
        self.ai_adapters = self._load_ai_adapters()
    
    def _load_templates(self) -> Dict:
        """Load base prompt templates for different categories"""
        return {
            "content_generation": {
                "structure": "[ROLE_DEFINITION]\n\n[TASK_DESCRIPTION]\n\n[CONTEXT]\n\n[SEO_KEYWORDS]\n\n[OUTPUT_FORMAT]",
                "description": "For blog posts, articles, and written content"
            },
            "image_generation": {
                "structure": "[SUBJECT], [STYLE], [COMPOSITION], [LIGHTING], [QUALITY], [PARAMETERS]",
                "description": "For AI art and image generation"
            },
            "code_generation": {
                "structure": "[ROLE_DEFINITION]\n\n[TASK_DESCRIPTION]\n\n[REQUIREMENTS]\n\n[CONSTRAINTS]\n\n[OUTPUT_FORMAT]",
                "description": "For programming and code-related tasks"
            },
            "data_analysis": {
                "structure": "[ROLE_DEFINITION]\n\n[TASK_DESCRIPTION]\n\n[DATA_CONTEXT]\n\n[ANALYSIS_GOALS]\n\n[OUTPUT_FORMAT]",
                "description": "For data analysis and insights"
            },
            "marketing": {
                "structure": "[ROLE_DEFINITION]\n\n[TASK_DESCRIPTION]\n\n[TARGET_AUDIENCE]\n\n[BRAND_CONTEXT]\n\n[SEO_KEYWORDS]\n\n[OUTPUT_FORMAT]",
                "description": "For marketing copy and campaigns"
            }
        }
    
    def _load_components(self) -> Dict:
        """Load modular prompt components"""
        return {
            "ROLE_DEFINITION": {
                "creative": "You are a creative and imaginative content creator with expertise in storytelling and engaging writing.",
                "technical": "You are a technical expert and professional writer with deep knowledge in your field.",
                "marketing": "You are an expert marketing strategist and copywriter with proven success in driving engagement.",
                "research": "You are a thorough researcher and academic writer with expertise in data analysis and evidence-based writing.",
                "seo": "You are an expert SEO strategist and content creator with specialization in search engine optimization."
            },
            "TASK_DESCRIPTION": {
                "improve": "Your task is to analyze and significantly improve the following prompt by enhancing its clarity, structure, and effectiveness.",
                "generate": "Your task is to create comprehensive, high-quality content based on the following requirements.",
                "analyze": "Your task is to thoroughly analyze the given content and provide detailed insights.",
                "optimize": "Your task is to optimize the following content for better performance and engagement."
            },
            "OUTPUT_FORMAT": {
                "structured": "Structure your output with clear headings, subheadings, and organized sections.",
                "markdown": "Format your output using proper Markdown syntax with headers, lists, and emphasis.",
                "code": "Provide your output as clean, well-commented code with proper formatting.",
                "list": "Present your output as a well-organized list with clear bullet points or numbering."
            },
            "QUALITY_MODIFIERS": {
                "high_quality": "ultra-detailed, high resolution, professional quality",
                "artistic": "artistic, creative, visually striking",
                "photorealistic": "photorealistic, lifelike, natural lighting",
                "cinematic": "cinematic lighting, dramatic composition, film-like quality"
            }
        }
    
    def _load_ai_adapters(self) -> Dict:
        """Load AI-specific prompt adaptations"""
        return {
            "chatgpt": {
                "prefix": "",
                "suffix": "",
                "style": "conversational",
                "max_length": 4000,
                "supports_roles": True,
                "supports_system": True
            },
            "claude": {
                "prefix": "",
                "suffix": "",
                "style": "detailed",
                "max_length": 8000,
                "supports_roles": True,
                "supports_system": True
            },
            "gemini": {
                "prefix": "",
                "suffix": "",
                "style": "structured",
                "max_length": 3000,
                "supports_roles": True,
                "supports_system": False
            },
            "midjourney": {
                "prefix": "",
                "suffix": "",
                "style": "keyword_based",
                "max_length": 500,
                "supports_roles": False,
                "supports_system": False,
                "parameters": ["--ar", "--style", "--quality", "--chaos", "--seed"]
            },
            "dalle": {
                "prefix": "",
                "suffix": "",
                "style": "descriptive",
                "max_length": 400,
                "supports_roles": False,
                "supports_system": False
            }
        }
    
    def generate_prompt(self, user_input: str, ai_tool: str, output_style: str, 
                       category: str, seo_keywords: Optional[str] = None,
                       operation: str = "generate") -> Dict:
        """Generate or improve a prompt based on user input"""
        
        # Determine the appropriate template
        template = self.templates.get(category, self.templates["content_generation"])
        
        # Get AI-specific adapter
        adapter = self.ai_adapters.get(ai_tool.lower(), self.ai_adapters["chatgpt"])
        
        # Build the prompt based on AI tool type
        if adapter["style"] == "keyword_based":
            # For image generation tools like Midjourney
            generated_prompt = self._generate_image_prompt(user_input, output_style, seo_keywords)
        else:
            # For text generation tools
            generated_prompt = self._generate_text_prompt(
                user_input, template, output_style, seo_keywords, operation, adapter
            )
        
        # Analyze the prompt
        analysis = self._analyze_prompt(generated_prompt, ai_tool, category)
        
        # Score the prompt
        score = self._score_prompt(generated_prompt, ai_tool, category)
        
        return {
            "generated_prompt": generated_prompt,
            "analysis": analysis,
            "score": score,
            "template_used": template["description"],
            "ai_tool": ai_tool,
            "category": category
        }
    
    def _generate_text_prompt(self, user_input: str, template: Dict, output_style: str,
                             seo_keywords: Optional[str], operation: str, adapter: Dict) -> str:
        """Generate a text-based prompt for conversational AI tools"""
        
        structure = template["structure"]
        components = self.components
        
        # Replace components in the template
        if "[ROLE_DEFINITION]" in structure:
            role = components["ROLE_DEFINITION"].get(output_style, 
                   components["ROLE_DEFINITION"]["technical"])
            structure = structure.replace("[ROLE_DEFINITION]", f"### ROLE\n{role}")
        
        if "[TASK_DESCRIPTION]" in structure:
            task = components["TASK_DESCRIPTION"].get(operation,
                   components["TASK_DESCRIPTION"]["generate"])
            structure = structure.replace("[TASK_DESCRIPTION]", f"### TASK\n{task}")
        
        if "[CONTEXT]" in structure:
            context = f"### CONTEXT\n{user_input}"
            structure = structure.replace("[CONTEXT]", context)
        
        if "[TARGET_AUDIENCE]" in structure:
            audience = "### TARGET AUDIENCE\nThe target audience should be considered based on the content goals and context provided."
            structure = structure.replace("[TARGET_AUDIENCE]", audience)
        
        if "[BRAND_CONTEXT]" in structure:
            brand = "### BRAND CONTEXT\nMaintain a professional and engaging tone that aligns with the brand voice."
            structure = structure.replace("[BRAND_CONTEXT]", brand)
        
        if "[REQUIREMENTS]" in structure:
            requirements = f"### REQUIREMENTS\n{user_input}"
            structure = structure.replace("[REQUIREMENTS]", requirements)
        
        if "[CONSTRAINTS]" in structure:
            constraints = "### CONSTRAINTS\nFollow best practices and ensure code quality, readability, and maintainability."
            structure = structure.replace("[CONSTRAINTS]", constraints)
        
        if "[DATA_CONTEXT]" in structure:
            data_context = f"### DATA CONTEXT\n{user_input}"
            structure = structure.replace("[DATA_CONTEXT]", data_context)
        
        if "[ANALYSIS_GOALS]" in structure:
            goals = "### ANALYSIS GOALS\nProvide actionable insights and clear recommendations based on the data."
            structure = structure.replace("[ANALYSIS_GOALS]", goals)
        
        if "[SEO_KEYWORDS]" in structure and seo_keywords:
            keywords = f"### SEO KEYWORDS\nNaturally incorporate these keywords: {seo_keywords}"
            structure = structure.replace("[SEO_KEYWORDS]", keywords)
        elif "[SEO_KEYWORDS]" in structure:
            structure = structure.replace("[SEO_KEYWORDS]", "")
        
        if "[OUTPUT_FORMAT]" in structure:
            output_format = components["OUTPUT_FORMAT"].get("structured",
                           components["OUTPUT_FORMAT"]["structured"])
            structure = structure.replace("[OUTPUT_FORMAT]", f"### OUTPUT FORMAT\n{output_format}")
        
        return structure.strip()
    
    def _generate_image_prompt(self, user_input: str, output_style: str, 
                              seo_keywords: Optional[str]) -> str:
        """Generate an image prompt for tools like Midjourney"""
        
        # Extract key elements from user input
        subject = user_input
        
        # Add style modifiers based on output_style
        style_modifiers = {
            "creative": "artistic, imaginative, unique perspective",
            "technical": "precise, detailed, technical illustration",
            "marketing": "professional, eye-catching, commercial quality",
            "research": "scientific, accurate, informative visualization"
        }
        
        style = style_modifiers.get(output_style, "high quality, detailed")
        
        # Add quality modifiers
        quality = self.components["QUALITY_MODIFIERS"]["high_quality"]
        
        # Combine elements
        prompt_parts = [subject, style, quality]
        
        # Add SEO keywords if provided
        if seo_keywords:
            prompt_parts.append(f"related to {seo_keywords}")
        
        # Add Midjourney parameters
        prompt = ", ".join(prompt_parts) + " --ar 16:9 --style raw --quality 2"
        
        return prompt
    
    def _analyze_prompt(self, prompt: str, ai_tool: str, category: str) -> str:
        """Analyze the generated prompt and provide feedback"""
        
        analysis_points = []
        
        # Check structure
        if "###" in prompt or "**" in prompt:
            analysis_points.append("✓ Well-structured with clear sections and formatting")
        
        # Check length
        word_count = len(prompt.split())
        if word_count > 50:
            analysis_points.append(f"✓ Comprehensive prompt with {word_count} words for detailed guidance")
        elif word_count < 20:
            analysis_points.append(f"⚠ Concise prompt with {word_count} words - consider adding more detail")
        
        # Check for role definition
        if "role" in prompt.lower() or "expert" in prompt.lower():
            analysis_points.append("✓ Includes clear role definition for better AI understanding")
        
        # Check for specific instructions
        if "task" in prompt.lower() or "create" in prompt.lower():
            analysis_points.append("✓ Contains specific task instructions")
        
        # Check for output format
        if "format" in prompt.lower() or "structure" in prompt.lower():
            analysis_points.append("✓ Specifies desired output format")
        
        # AI-specific analysis
        adapter = self.ai_adapters.get(ai_tool.lower(), {})
        if adapter.get("style") == "keyword_based":
            analysis_points.append("✓ Optimized for image generation with descriptive keywords")
            if "--" in prompt:
                analysis_points.append("✓ Includes technical parameters for enhanced control")
        
        return "\n".join(analysis_points)
    
    def _score_prompt(self, prompt: str, ai_tool: str, category: str) -> int:
        """Score the prompt quality from 1-100"""
        
        score = 60  # Base score
        
        # Length scoring
        word_count = len(prompt.split())
        if 30 <= word_count <= 200:
            score += 10
        elif word_count > 200:
            score += 5
        
        # Structure scoring
        if "###" in prompt:
            score += 15
        if "ROLE" in prompt.upper():
            score += 10
        if "TASK" in prompt.upper():
            score += 10
        
        # Specificity scoring
        specific_words = ["specific", "detailed", "comprehensive", "professional", "expert"]
        for word in specific_words:
            if word in prompt.lower():
                score += 2
        
        # AI tool optimization
        adapter = self.ai_adapters.get(ai_tool.lower(), {})
        if adapter.get("style") == "keyword_based" and "," in prompt:
            score += 10
        
        # Cap the score at 100
        return min(score, 100)
    
    def improve_existing_prompt(self, existing_prompt: str, ai_tool: str, 
                               output_style: str, category: str) -> Dict:
        """Improve an existing prompt"""
        
        # Analyze the existing prompt
        issues = self._identify_prompt_issues(existing_prompt)
        
        # Apply improvements
        improved_prompt = self._apply_improvements(existing_prompt, issues, ai_tool, output_style)
        
        # Generate analysis
        analysis = self._analyze_improvements(existing_prompt, improved_prompt, issues)
        
        # Score the improved prompt
        score = self._score_prompt(improved_prompt, ai_tool, category)
        
        return {
            "generated_prompt": improved_prompt,
            "analysis": analysis,
            "score": score,
            "improvements_made": issues,
            "ai_tool": ai_tool,
            "category": category
        }
    
    def _identify_prompt_issues(self, prompt: str) -> List[str]:
        """Identify issues with an existing prompt"""
        issues = []
        
        if len(prompt.split()) < 10:
            issues.append("Too brief - needs more detail")
        
        if not any(word in prompt.lower() for word in ["you are", "role", "expert", "specialist"]):
            issues.append("Missing role definition")
        
        if not any(word in prompt.lower() for word in ["create", "generate", "write", "task"]):
            issues.append("Unclear task definition")
        
        if "###" not in prompt and "**" not in prompt:
            issues.append("Poor structure - needs formatting")
        
        if prompt.count(".") < 2:
            issues.append("Needs more detailed instructions")
        
        return issues
    
    def _apply_improvements(self, prompt: str, issues: List[str], ai_tool: str, output_style: str) -> str:
        """Apply improvements to the prompt"""
        
        improved = prompt
        
        # Add role definition if missing
        if "Missing role definition" in issues:
            role = self.components["ROLE_DEFINITION"].get(output_style, 
                   self.components["ROLE_DEFINITION"]["technical"])
            improved = f"### ROLE\n{role}\n\n### TASK\n{improved}"
        
        # Add structure if missing
        if "Poor structure - needs formatting" in issues:
            # Add basic structure
            if "### TASK" not in improved:
                improved = f"### TASK\n{improved}"
            
            improved += "\n\n### OUTPUT FORMAT\nProvide a well-structured, comprehensive response with clear formatting."
        
        # Add more detail if too brief
        if "Too brief - needs more detail" in issues:
            improved += "\n\nPlease ensure your response is thorough, detailed, and addresses all aspects of the request."
        
        return improved
    
    def _analyze_improvements(self, original: str, improved: str, issues: List[str]) -> str:
        """Analyze the improvements made"""
        
        analysis = ["### Improvements Made:"]
        
        for issue in issues:
            if issue == "Missing role definition":
                analysis.append("✓ Added clear role definition for better AI understanding")
            elif issue == "Poor structure - needs formatting":
                analysis.append("✓ Improved structure with clear sections and formatting")
            elif issue == "Too brief - needs more detail":
                analysis.append("✓ Enhanced with additional detail and context")
            elif issue == "Unclear task definition":
                analysis.append("✓ Clarified task instructions and expectations")
        
        word_increase = len(improved.split()) - len(original.split())
        if word_increase > 0:
            analysis.append(f"✓ Expanded from {len(original.split())} to {len(improved.split())} words (+{word_increase})")
        
        return "\n".join(analysis)

