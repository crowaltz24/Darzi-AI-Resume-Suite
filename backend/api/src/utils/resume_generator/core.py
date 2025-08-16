"""
Resume Generator Core Module

This module provides the main ResumeGenerator class for generating LaTeX resumes using LLM.
"""

import logging
from typing import Dict, List, Optional, Any
from ..llm.manager import LLMManager

logger = logging.getLogger(__name__)


class ResumeGenerator:
    """
    Resume generator that uses LLM to create LaTeX code based on resume data and templates.
    """
    
    def __init__(self):
        """Initialize the resume generator with LLM manager."""
        self.llm_manager = LLMManager()
    
    def generate_resume(
        self,
        user_resume: Dict[str, Any],
        resume_template: str,
        extra_info: Optional[Dict[str, str]] = None,
        ats_score: Optional[int] = None,
        improvement_suggestions: Optional[List[str]] = None,
        preferred_provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate resume LaTeX code using LLM.
        
        Args:
            user_resume (Dict[str, Any]): Parsed resume data containing personal info, 
                                        experience, education, skills, etc.
            resume_template (str): LaTeX template code for the resume
            extra_info (Optional[Dict[str, str]]): Additional information like LinkedIn, 
                                                 GitHub, portfolio links, etc.
            ats_score (Optional[int]): Current ATS compatibility score (0-100)
            improvement_suggestions (Optional[List[str]]): List of ATS improvement suggestions
            preferred_provider (Optional[str]): Preferred LLM provider to use
            
        Returns:
            Dict[str, Any]: Response containing:
                - success (bool): Whether generation was successful
                - latex_code (str): Generated LaTeX code
                - provider_used (str): LLM provider that was used
                - error (str): Error message if generation failed
                - metadata (Dict): Additional metadata about generation
        """
        try:
            # Validate inputs
            if not user_resume:
                return {
                    "success": False,
                    "error": "User resume data is required",
                    "latex_code": None,
                    "provider_used": None,
                    "metadata": {}
                }
            
            if not resume_template:
                return {
                    "success": False,
                    "error": "Resume template is required",
                    "latex_code": None,
                    "provider_used": None,
                    "metadata": {}
                }
            
            # Check LLM availability
            available_providers = self.llm_manager.get_available_providers()
            if not available_providers:
                return {
                    "success": False,
                    "error": "No LLM providers available",
                    "latex_code": None,
                    "provider_used": None,
                    "metadata": {"available_providers": []}
                }
            
            # Create the prompt for LLM
            prompt = self._create_resume_generation_prompt(
                user_resume=user_resume,
                resume_template=resume_template,
                extra_info=extra_info,
                ats_score=ats_score,
                improvement_suggestions=improvement_suggestions
            )
            
            # Generate LaTeX code using LLM
            result = self.llm_manager.generate_text(
                prompt=prompt,
                preferred_provider=preferred_provider
            )
            
            if result["success"]:
                # Extract LaTeX code from LLM response
                latex_code = self._extract_latex_code(result["content"])
                
                return {
                    "success": True,
                    "latex_code": latex_code,
                    "provider_used": result["provider_used"],
                    "error": None,
                    "metadata": {
                        "prompt_length": len(prompt),
                        "response_length": len(result["content"]),
                        "available_providers": available_providers,
                        "generation_method": "llm"
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"LLM generation failed: {result.get('error', 'Unknown error')}",
                    "latex_code": None,
                    "provider_used": result.get("provider_used"),
                    "metadata": {
                        "available_providers": available_providers,
                        "generation_method": "llm"
                    }
                }
                
        except Exception as e:
            logger.error(f"Error generating resume: {str(e)}")
            return {
                "success": False,
                "error": f"Resume generation failed: {str(e)}",
                "latex_code": None,
                "provider_used": None,
                "metadata": {}
            }
    
    def _create_resume_generation_prompt(
        self,
        user_resume: Dict[str, Any],
        resume_template: str,
        extra_info: Optional[Dict[str, str]] = None,
        ats_score: Optional[int] = None,
        improvement_suggestions: Optional[List[str]] = None
    ) -> str:
        """
        Create a comprehensive prompt for LLM to generate resume LaTeX code.
        
        Args:
            user_resume: Parsed resume data
            resume_template: LaTeX template
            extra_info: Additional information
            ats_score: Current ATS score
            improvement_suggestions: ATS improvement suggestions
            
        Returns:
            str: Complete prompt for LLM
        """
        
        prompt_parts = [
            "You are an expert LaTeX resume generator. Your task is to create a professional resume in LaTeX format using the provided template and user data.",
            "",
            "**INSTRUCTIONS:**",
            "1. Use the provided LaTeX template as the base structure",
            "2. Fill in the template with the user's resume data",
            "3. Maintain professional formatting and LaTeX syntax",
            "4. Ensure all LaTeX commands are properly escaped",
            "5. If ATS suggestions are provided, incorporate them to improve ATS compatibility",
            "6. Add any extra information provided (LinkedIn, GitHub, etc.) in appropriate sections",
            "7. Return ONLY the complete LaTeX code, no explanations or comments",
            "",
            "**USER RESUME DATA:**"
        ]
        
        # Add user resume data
        if isinstance(user_resume, dict):
            # Contact Information
            contact_info = user_resume.get('contact_information', {})
            if contact_info:
                prompt_parts.append("Contact Information:")
                prompt_parts.append(f"- Name: {contact_info.get('full_name', 'N/A')}")
                prompt_parts.append(f"- Email: {contact_info.get('email', 'N/A')}")
                prompt_parts.append(f"- Phone: {contact_info.get('phone', 'N/A')}")
                prompt_parts.append(f"- Location: {contact_info.get('location', 'N/A')}")
                if contact_info.get('linkedin'):
                    prompt_parts.append(f"- LinkedIn: {contact_info['linkedin']}")
                if contact_info.get('github'):
                    prompt_parts.append(f"- GitHub: {contact_info['github']}")
                prompt_parts.append("")
            
            # Professional Summary
            summary = user_resume.get('professional_summary', '')
            if summary:
                prompt_parts.append(f"Professional Summary: {summary}")
                prompt_parts.append("")
            
            # Work Experience
            experience = user_resume.get('work_experience', [])
            if experience:
                prompt_parts.append("Work Experience:")
                for i, exp in enumerate(experience, 1):
                    prompt_parts.append(f"{i}. {exp.get('position', 'Position')} at {exp.get('company', 'Company')}")
                    prompt_parts.append(f"   Duration: {exp.get('duration', 'N/A')}")
                    prompt_parts.append(f"   Location: {exp.get('location', 'N/A')}")
                    if exp.get('description'):
                        prompt_parts.append(f"   Description: {exp['description']}")
                    if exp.get('responsibilities'):
                        responsibilities = exp['responsibilities']
                        if isinstance(responsibilities, list):
                            prompt_parts.append("   Responsibilities:")
                            for resp in responsibilities:
                                prompt_parts.append(f"   - {resp}")
                        else:
                            prompt_parts.append(f"   Responsibilities: {responsibilities}")
                    if exp.get('achievements'):
                        achievements = exp['achievements']
                        if isinstance(achievements, list):
                            prompt_parts.append("   Achievements:")
                            for ach in achievements:
                                prompt_parts.append(f"   - {ach}")
                        else:
                            prompt_parts.append(f"   Achievements: {achievements}")
                    prompt_parts.append("")
            
            # Education
            education = user_resume.get('education', [])
            if education:
                prompt_parts.append("Education:")
                for i, edu in enumerate(education, 1):
                    prompt_parts.append(f"{i}. {edu.get('degree', 'Degree')} from {edu.get('institution', 'Institution')}")
                    prompt_parts.append(f"   Field: {edu.get('field_of_study', 'N/A')}")
                    prompt_parts.append(f"   Year: {edu.get('graduation_year', edu.get('graduation_date', 'N/A'))}")
                    if edu.get('gpa'):
                        prompt_parts.append(f"   GPA: {edu['gpa']}")
                    if edu.get('honors'):
                        prompt_parts.append(f"   Honors: {edu['honors']}")
                    prompt_parts.append("")
            
            # Skills
            skills = user_resume.get('skills', {})
            if skills:
                prompt_parts.append("Skills:")
                for skill_category, skill_list in skills.items():
                    if skill_list:
                        prompt_parts.append(f"- {skill_category.replace('_', ' ').title()}:")
                        if isinstance(skill_list, list):
                            prompt_parts.append(f"  {', '.join(skill_list)}")
                        else:
                            prompt_parts.append(f"  {skill_list}")
                prompt_parts.append("")
            
            # Projects
            projects = user_resume.get('projects', [])
            if projects:
                prompt_parts.append("Projects:")
                for i, project in enumerate(projects, 1):
                    prompt_parts.append(f"{i}. {project.get('name', f'Project {i}')}")
                    if project.get('description'):
                        prompt_parts.append(f"   Description: {project['description']}")
                    if project.get('technologies'):
                        technologies = project['technologies']
                        if isinstance(technologies, list):
                            prompt_parts.append(f"   Technologies: {', '.join(technologies)}")
                        else:
                            prompt_parts.append(f"   Technologies: {technologies}")
                    if project.get('url'):
                        prompt_parts.append(f"   URL: {project['url']}")
                    prompt_parts.append("")
        
        # Add extra information
        if extra_info:
            prompt_parts.append("**ADDITIONAL INFORMATION:**")
            for key, value in extra_info.items():
                if value:
                    prompt_parts.append(f"- {key.replace('_', ' ').title()}: {value}")
            prompt_parts.append("")
        
        # Add ATS information
        if ats_score is not None:
            prompt_parts.append(f"**CURRENT ATS SCORE:** {ats_score}/100")
            prompt_parts.append("")
        
        if improvement_suggestions:
            prompt_parts.append("**ATS IMPROVEMENT SUGGESTIONS:**")
            for i, suggestion in enumerate(improvement_suggestions, 1):
                prompt_parts.append(f"{i}. {suggestion}")
            prompt_parts.append("")
            prompt_parts.append("Please incorporate these suggestions to improve ATS compatibility.")
            prompt_parts.append("")
        
        # Add template
        prompt_parts.extend([
            "**LATEX TEMPLATE TO USE:**",
            "```latex",
            resume_template.strip(),
            "```",
            "",
            "**OUTPUT REQUIREMENTS:**",
            "- Return ONLY the complete LaTeX code",
            "- Fill in all template sections with the user's data",
            "- Ensure proper LaTeX syntax and escaping",
            "- Maintain professional formatting",
            "- If ATS suggestions were provided, incorporate them into the content",
            "- Include all additional information in appropriate sections",
            "",
            "Generate the complete LaTeX resume code now:"
        ])
        
        return "\n".join(prompt_parts)
    
    def _extract_latex_code(self, llm_response: str) -> str:
        """
        Extract LaTeX code from LLM response.
        
        Args:
            llm_response: Raw response from LLM
            
        Returns:
            str: Extracted LaTeX code
        """
        # Remove common markdown code block markers
        latex_code = llm_response.strip()
        
        # Remove ```latex and ``` markers if present
        if latex_code.startswith("```latex"):
            latex_code = latex_code[8:]
        elif latex_code.startswith("```"):
            latex_code = latex_code[3:]
        
        if latex_code.endswith("```"):
            latex_code = latex_code[:-3]
        
        # Clean up any remaining markdown or formatting
        latex_code = latex_code.strip()
        
        # Ensure the LaTeX document starts with \documentclass if it's a complete document
        if not latex_code.startswith("\\documentclass") and not latex_code.startswith("\\begin{document}"):
            # If it doesn't start with document class, assume it's content only
            logger.info("LaTeX code appears to be content-only, not a complete document")
        
        return latex_code
    
    def get_available_providers(self) -> List[str]:
        """
        Get list of available LLM providers.
        
        Returns:
            List[str]: Available provider names
        """
        return self.llm_manager.get_available_providers()
    
    def is_available(self) -> bool:
        """
        Check if resume generation is available (i.e., if any LLM providers are available).
        
        Returns:
            bool: True if generation is available, False otherwise
        """
        return len(self.llm_manager.get_available_providers()) > 0
