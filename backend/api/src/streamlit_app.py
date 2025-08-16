"""Streamlit web interface for Darzi Resume Parser with Enhanced LLM and ATS Analysis."""

import streamlit as st
import requests
import tempfile
import os
import json
from typing import Optional, Dict, Any

st.set_page_config(
    page_title="Darzi Resume Parser & ATS Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:7860")

def main():
    st.title("📄 Darzi Resume Parser & ATS Analyzer")
    st.markdown("AI-powered resume parsing, text extraction, and ATS optimization")

    # Sidebar
    st.sidebar.title("🛠️ Tools")
    tool = st.sidebar.selectbox(
        "Choose a tool:",
        ["Resume Parser", "ATS Analyzer", "Text Extractor"]
    )

    if tool == "Resume Parser":
        resume_parser_interface()
    elif tool == "ATS Analyzer":
        ats_analyzer_interface()
    elif tool == "Text Extractor":
        text_extractor_interface()

def check_api_status():
    """Check API health and services status"""
    try:
        health_response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            return health_data
        return None
    except:
        return None

def resume_parser_interface():
    st.header("🔍 Enhanced Resume Parser")
    st.markdown("Extract structured data from resumes using AI-powered parsing")
    
    # Check API status
    health_data = check_api_status()
    if not health_data:
        st.error("❌ Cannot connect to API service. Please ensure the server is running.")
        return
    
    # Parser configuration sidebar
    st.sidebar.subheader("⚙️ Parser Settings")
    
    # Check parser status
    try:
        status_response = requests.get(f"{API_BASE_URL}/parser-status")
        if status_response.status_code == 200:
            status_data = status_response.json()
            llm_available = status_data.get('llm_available', False)
            available_providers = status_data.get('available_llm_providers', [])
            
            if llm_available:
                st.sidebar.success(f"🤖 LLM Available: {', '.join(available_providers)}")
            else:
                st.sidebar.warning("⚠️ LLM Not Available - Using Local Parser Only")
        else:
            llm_available = False
            available_providers = []
            st.sidebar.error("❌ Cannot check parser status")
    except:
        llm_available = False
        available_providers = []
        st.sidebar.error("❌ Cannot connect to parser service")
    
    # Parser method selection
    parser_method = st.sidebar.selectbox(
        "Parsing Method:",
        ["Enhanced (LLM + Fallback)", "LLM Only", "Local Only"] if llm_available else ["Local Only"]
    )
    
    # Provider selection if LLM is available
    preferred_provider = None
    if llm_available and available_providers and parser_method in ["Enhanced (LLM + Fallback)", "LLM Only"]:
        preferred_provider = st.sidebar.selectbox(
            "Preferred LLM Provider:",
            ["Auto"] + available_providers
        )
        if preferred_provider == "Auto":
            preferred_provider = None
    
    # Output format selection
    return_raw = st.sidebar.checkbox(
        "Return Raw Data",
        value=False,
        help="Return raw parsed data instead of normalized structure"
    )

    # Input method selection
    input_method = st.radio(
        "Input method:",
        ["Upload File", "Paste Text"]
    )

    if input_method == "Upload File":
        uploaded_file = st.file_uploader(
            "Choose a resume file",
            type=["pdf", "txt", "docx"],
            help="Upload a resume in PDF, TXT, or DOCX format"
        )

        if uploaded_file is not None and st.button("Parse Resume", type="primary"):
            with st.spinner("Parsing resume with AI..."):
                try:
                    # Determine endpoint based on parser method
                    if parser_method == "Enhanced (LLM + Fallback)":
                        endpoint = "/parse-enhanced"
                        data = {
                            "use_llm": True,
                            "return_raw": return_raw
                        }
                        if preferred_provider:
                            data["preferred_provider"] = preferred_provider
                    elif parser_method == "LLM Only":
                        endpoint = "/parse-llm-only"
                        data = {"return_raw": return_raw}
                        if preferred_provider:
                            data["preferred_provider"] = preferred_provider
                    else:  # Local Only
                        endpoint = "/parse-local-only"
                        data = {"return_raw": return_raw}
                    
                    response = requests.post(
                        f"{API_BASE_URL}{endpoint}",
                        files={"file": uploaded_file},
                        data=data
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        display_enhanced_resume_results(result, return_raw)
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    else:  # Paste Text
        resume_text = st.text_area(
            "Paste resume text:",
            height=200,
            help="Copy and paste the resume text here"
        )

        if resume_text and st.button("Parse Resume Text", type="primary"):
            with st.spinner("Parsing resume text..."):
                try:
                    # Create a temporary text file for the enhanced parser
                    response = requests.post(
                        f"{API_BASE_URL}/parse-enhanced",
                        files={"file": ("resume.txt", resume_text.encode(), "text/plain")},
                        data={
                            "use_llm": True if llm_available else False,
                            "return_raw": return_raw,
                            "preferred_provider": preferred_provider
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        display_enhanced_resume_results(result, return_raw)
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

def ats_analyzer_interface():
    st.header("📊 AI-Powered ATS Analyzer")
    st.markdown("Analyze your resume's compatibility with Applicant Tracking Systems using advanced AI")
    
    # Check API status
    health_data = check_api_status()
    if not health_data:
        st.error("❌ Cannot connect to API service. Please ensure the server is running.")
        return
    
    # ATS configuration sidebar
    st.sidebar.subheader("⚙️ ATS Settings")
    
    # Check ATS analyzer status
    try:
        ats_status_response = requests.get(f"{API_BASE_URL}/ats-status")
        if ats_status_response.status_code == 200:
            ats_status_data = ats_status_response.json()
            ats_llm_available = ats_status_data.get('llm_available', False)
            ats_providers = ats_status_data.get('available_providers', [])
            
            if ats_llm_available:
                st.sidebar.success(f"🤖 ATS AI Available: {', '.join(ats_providers)}")
            else:
                st.sidebar.warning("⚠️ ATS AI Not Available - Using Rule-Based Analysis")
        else:
            ats_llm_available = False
            ats_providers = []
            st.sidebar.error("❌ Cannot check ATS analyzer status")
    except:
        ats_llm_available = False
        ats_providers = []
        st.sidebar.error("❌ Cannot connect to ATS analyzer service")
    
    # Provider selection for ATS
    ats_preferred_provider = None
    if ats_llm_available and ats_providers:
        ats_preferred_provider = st.sidebar.selectbox(
            "Preferred AI Provider for ATS:",
            ["Auto"] + ats_providers
        )
        if ats_preferred_provider == "Auto":
            ats_preferred_provider = None

    # Input sections
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 Resume Text")
        resume_text = st.text_area(
            "Paste your resume text here:",
            height=300,
            help="Copy and paste your complete resume text"
        )
    
    with col2:
        st.subheader("💼 Job Description")
        job_description = st.text_area(
            "Paste the job description here:",
            height=300,
            help="Copy and paste the job posting you're targeting"
        )

    if resume_text and job_description and st.button("🚀 Analyze ATS Compatibility", type="primary"):
        with st.spinner("Analyzing ATS compatibility with AI..."):
            try:
                payload = {
                    "resume_text": resume_text,
                    "job_description": job_description
                }
                if ats_preferred_provider:
                    payload["preferred_provider"] = ats_preferred_provider
                
                response = requests.post(f"{API_BASE_URL}/analyze-ats", json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    display_ats_analysis_results(result)
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    elif st.button("🚀 Analyze ATS Compatibility", type="primary"):
        if not resume_text:
            st.warning("⚠️ Please paste your resume text")
        if not job_description:
            st.warning("⚠️ Please paste the job description")

def text_extractor_interface():
    st.header("📝 Text Extractor")
    st.markdown("Extract text from PDFs, images, and documents using Google Vision API")

    input_method = st.radio(
        "Input method:",
        ["Upload File", "Google Drive URL"]
    )

    if input_method == "Upload File":
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["pdf", "png", "jpg", "jpeg", "gif", "txt", "md", "csv"],
            help="Upload PDF, image, or text file"
        )

        if uploaded_file is not None and st.button("Extract Text", type="primary"):
            with st.spinner("Extracting text..."):
                try:
                    response = requests.post(f"{API_BASE_URL}/api/extract", files={"file": uploaded_file})
                    
                    if response.status_code == 200:
                        result = response.json()
                        display_text_results(result)
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    else:  # Google Drive URL
        drive_url = st.text_input(
            "Google Drive URL:",
            help="Paste a Google Drive share link"
        )

        if drive_url and st.button("Extract Text from URL", type="primary"):
            with st.spinner("Extracting text from URL..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/api/extract-url",
                        json={"url": drive_url}
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        display_text_results(result)
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

def display_enhanced_resume_results(result: Dict[str, Any], return_raw: bool):
    """Display enhanced resume parsing results."""
    if result.get("status") == "success":
        # Metadata section
        st.success(f"✅ Resume parsed successfully!")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("File Size", result.get("file_size", "Unknown"))
        with col2:
            st.metric("Text Length", f"{result.get('text_length', 0):,} chars")
        with col3:
            st.metric("Parsing Method", result.get("parsing_method", "Unknown"))
        with col4:
            if "confidence_score" in result:
                st.metric("Confidence", f"{result['confidence_score']:.0%}")
        
        # Parser info
        if result.get("parsed_by"):
            st.info(f"🤖 Parsed by: {result['parsed_by']}")
        
        # Main results tabs
        if return_raw:
            tab1, tab2 = st.tabs(["📊 Raw Data", "📋 JSON Export"])
            
            with tab1:
                st.subheader("Raw Parsed Data")
                raw_data = result.get("raw_data", {})
                display_structured_data(raw_data)
            
            with tab2:
                st.subheader("Export Raw JSON")
                st.json(result.get("raw_data", {}))
                
        else:
            tab1, tab2, tab3 = st.tabs(["📊 Structured Data", "🔍 Raw Data", "📋 JSON Export"])
            
            with tab1:
                st.subheader("Structured Resume Data")
                normalized_data = result.get("normalized_data", {})
                display_structured_data(normalized_data)
            
            with tab2:
                st.subheader("Raw Parsed Data")
                raw_data = result.get("raw_data", {})
                display_structured_data(raw_data)
            
            with tab3:
                st.subheader("Export Complete JSON")
                st.json(result)
    else:
        st.error(f"❌ Parsing failed: {result.get('error', 'Unknown error')}")

def display_structured_data(data: Dict[str, Any]):
    """Display structured data in an organized format."""
    if not data:
        st.warning("No data available")
        return
    
    # Contact Information
    if "contact_information" in data:
        st.subheader("👤 Contact Information")
        contact = data["contact_information"]
        if isinstance(contact, dict):
            col1, col2 = st.columns(2)
            with col1:
                if contact.get("full_name"):
                    st.text(f"Name: {contact['full_name']}")
                if contact.get("email"):
                    st.text(f"Email: {contact['email']}")
            with col2:
                if contact.get("phone"):
                    st.text(f"Phone: {contact['phone']}")
                if contact.get("title"):
                    st.text(f"Title: {contact['title']}")
    
    # Professional Summary
    if "professional_summary" in data and data["professional_summary"]:
        st.subheader("📝 Professional Summary")
        st.write(data["professional_summary"])
    
    # Skills
    if "skills" in data or "technical_skills" in data:
        st.subheader("🛠️ Skills")
        skills_data = data.get("skills") or data.get("technical_skills")
        
        if isinstance(skills_data, dict):
            for category, skills_list in skills_data.items():
                if skills_list:
                    st.write(f"**{category.replace('_', ' ').title()}:** {', '.join(skills_list)}")
        elif isinstance(skills_data, list):
            st.write(", ".join(skills_data))
        else:
            st.write(str(skills_data))
    
    # Work Experience
    if "work_experience" in data and data["work_experience"]:
        st.subheader("💼 Work Experience")
        experience = data["work_experience"]
        
        if isinstance(experience, list):
            for job in experience:
                if isinstance(job, dict):
                    st.write(f"**{job.get('title', 'Position')}** at **{job.get('company', 'Company')}**")
                    if job.get("duration"):
                        st.write(f"*{job['duration']}*")
                    if job.get("responsibilities"):
                        for resp in job["responsibilities"]:
                            st.write(f"• {resp}")
                    st.write("---")
    
    # Education
    if "education" in data and data["education"]:
        st.subheader("🎓 Education")
        education = data["education"]
        
        if isinstance(education, list):
            for edu in education:
                if isinstance(edu, dict):
                    st.write(f"**{edu.get('degree', 'Degree')}** in **{edu.get('field', 'Field')}**")
                    if edu.get("institution"):
                        st.write(f"*{edu['institution']}*")
                    if edu.get("year"):
                        st.write(f"Year: {edu['year']}")
                    st.write("---")
        else:
            st.write(str(education))
    
    # Projects
    if "projects" in data and data["projects"]:
        st.subheader("🚀 Projects")
        projects = data["projects"]
        
        if isinstance(projects, list):
            for project in projects:
                if isinstance(project, dict):
                    st.write(f"**{project.get('name', 'Project')}**")
                    if project.get("description"):
                        st.write(project["description"])
                    if project.get("technologies"):
                        st.write(f"Technologies: {', '.join(project['technologies'])}")
                    st.write("---")

def display_ats_analysis_results(result: Dict[str, Any]):
    """Display comprehensive ATS analysis results."""
    if not result.get("success"):
        st.error(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")
        return
    
    analysis = result.get("analysis", {})
    overall_score = analysis.get("overall_score", 0)
    
    # Header with overall score
    st.success(f"✅ ATS Analysis Complete!")
    
    # Score visualization
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Overall ATS Score", f"{overall_score}/100", 
                 help="Overall compatibility with ATS systems")
    with col2:
        st.metric("Predicted Pass Rate", f"{analysis.get('predicted_ats_pass_rate', 0)}%",
                 help="Likelihood of passing through ATS filters")
    with col3:
        confidence = analysis.get('confidence_score', 0)
        st.metric("Analysis Confidence", f"{confidence:.0%}",
                 help="Confidence level of the analysis")
    
    # Analysis method info
    method = analysis.get('analysis_method', 'unknown')
    provider = analysis.get('provider_used', 'unknown')
    if method == 'llm':
        st.info(f"🤖 Analyzed using AI: {provider}")
    else:
        st.info(f"📊 Analyzed using: {method}")
    
    # Score interpretation
    if overall_score >= 90:
        st.success("🎉 Excellent! Your resume is highly optimized for ATS systems.")
    elif overall_score >= 80:
        st.success("👍 Good! Your resume should perform well with most ATS systems.")
    elif overall_score >= 70:
        st.warning("⚠️ Fair. Your resume needs some improvements for better ATS compatibility.")
    elif overall_score >= 60:
        st.warning("⚠️ Poor. Significant improvements needed for ATS compatibility.")
    else:
        st.error("❌ Critical. Major overhaul required for ATS compatibility.")
    
    # Summary
    if analysis.get("summary"):
        st.subheader("📋 Executive Summary")
        st.write(analysis["summary"])
    
    # Detailed analysis tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔑 Keywords", "📄 Content", "🎨 Formatting", "🛠️ Skills", "💼 Experience"
    ])
    
    with tab1:
        display_keyword_analysis(analysis.get("keyword_analysis", {}))
    
    with tab2:
        display_content_analysis(analysis.get("content_analysis", {}))
    
    with tab3:
        display_formatting_analysis(analysis.get("formatting_analysis", {}))
    
    with tab4:
        display_skills_analysis(analysis.get("skills_analysis", {}))
    
    with tab5:
        display_experience_analysis(analysis.get("experience_analysis", {}))
    
    # Improvement priorities
    st.subheader("🎯 Improvement Priorities")
    priorities = analysis.get("improvement_priority", {})
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**🔴 High Priority**")
        for item in priorities.get("high_priority", []):
            st.write(f"• {item}")
    
    with col2:
        st.write("**🟡 Medium Priority**")
        for item in priorities.get("medium_priority", []):
            st.write(f"• {item}")
    
    with col3:
        st.write("**🟢 Low Priority**")
        for item in priorities.get("low_priority", []):
            st.write(f"• {item}")
    
    # ATS optimization tips
    if analysis.get("ats_optimization_tips"):
        st.subheader("💡 ATS Optimization Tips")
        for tip in analysis["ats_optimization_tips"]:
            st.write(f"• {tip}")

def display_keyword_analysis(keyword_data: Dict[str, Any]):
    """Display keyword analysis details."""
    if not keyword_data:
        st.warning("No keyword analysis available")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        score = keyword_data.get("keyword_match_score", 0)
        st.metric("Keyword Match Score", f"{score}/100")
        
        matched = keyword_data.get("matched_keywords", [])
        if matched:
            st.write("**✅ Matched Keywords:**")
            for keyword in matched[:10]:  # Show first 10
                st.write(f"• {keyword}")
    
    with col2:
        density = keyword_data.get("keyword_density", 0)
        st.metric("Keyword Density", f"{density}/100")
        
        missing = keyword_data.get("missing_critical_keywords", [])
        if missing:
            st.write("**❌ Missing Critical Keywords:**")
            for keyword in missing[:10]:  # Show first 10
                st.write(f"• {keyword}")
    
    # Recommendations
    recommendations = keyword_data.get("recommendations", [])
    if recommendations:
        st.write("**💡 Keyword Recommendations:**")
        for rec in recommendations:
            st.write(f"• {rec}")

def display_content_analysis(content_data: Dict[str, Any]):
    """Display content analysis details."""
    if not content_data:
        st.warning("No content analysis available")
        return
    
    score = content_data.get("content_score", 0)
    st.metric("Content Quality Score", f"{score}/100")
    
    col1, col2 = st.columns(2)
    
    with col1:
        strengths = content_data.get("strengths", [])
        if strengths:
            st.write("**✅ Strengths:**")
            for strength in strengths:
                st.write(f"• {strength}")
    
    with col2:
        weaknesses = content_data.get("weaknesses", [])
        if weaknesses:
            st.write("**⚠️ Areas for Improvement:**")
            for weakness in weaknesses:
                st.write(f"• {weakness}")
    
    # Missing sections
    missing = content_data.get("missing_sections", [])
    if missing:
        st.write("**📝 Missing Sections:**")
        for section in missing:
            st.write(f"• {section}")
    
    # Recommendations
    recommendations = content_data.get("recommendations", [])
    if recommendations:
        st.write("**💡 Content Recommendations:**")
        for rec in recommendations:
            st.write(f"• {rec}")

def display_formatting_analysis(formatting_data: Dict[str, Any]):
    """Display formatting analysis details."""
    if not formatting_data:
        st.warning("No formatting analysis available")
        return
    
    score = formatting_data.get("formatting_score", 0)
    st.metric("Formatting Score", f"{score}/100")
    
    issues = formatting_data.get("formatting_issues", [])
    if issues:
        st.write("**⚠️ Formatting Issues:**")
        for issue in issues:
            st.write(f"• {issue}")
    
    recommendations = formatting_data.get("recommendations", [])
    if recommendations:
        st.write("**💡 Formatting Recommendations:**")
        for rec in recommendations:
            st.write(f"• {rec}")

def display_skills_analysis(skills_data: Dict[str, Any]):
    """Display skills analysis details."""
    if not skills_data:
        st.warning("No skills analysis available")
        return
    
    score = skills_data.get("skills_match_score", 0)
    st.metric("Skills Match Score", f"{score}/100")
    
    col1, col2 = st.columns(2)
    
    with col1:
        matched = skills_data.get("matched_skills", [])
        if matched:
            st.write("**✅ Matched Skills:**")
            for skill in matched:
                st.write(f"• {skill}")
    
    with col2:
        missing = skills_data.get("missing_skills", [])
        if missing:
            st.write("**❌ Missing Skills:**")
            for skill in missing:
                st.write(f"• {skill}")
    
    # Skill gaps
    gaps = skills_data.get("skill_gaps", [])
    if gaps:
        st.write("**🔍 Skill Gaps:**")
        for gap in gaps:
            st.write(f"• {gap}")
    
    # Recommendations
    recommendations = skills_data.get("recommendations", [])
    if recommendations:
        st.write("**💡 Skills Recommendations:**")
        for rec in recommendations:
            st.write(f"• {rec}")

def display_experience_analysis(experience_data: Dict[str, Any]):
    """Display experience analysis details."""
    if not experience_data:
        st.warning("No experience analysis available")
        return
    
    score = experience_data.get("experience_score", 0)
    st.metric("Experience Relevance Score", f"{score}/100")
    
    col1, col2 = st.columns(2)
    
    with col1:
        relevant = experience_data.get("relevant_experience", [])
        if relevant:
            st.write("**✅ Relevant Experience:**")
            for exp in relevant:
                st.write(f"• {exp}")
    
    with col2:
        gaps = experience_data.get("experience_gaps", [])
        if gaps:
            st.write("**❌ Experience Gaps:**")
            for gap in gaps:
                st.write(f"• {gap}")
    
    # Recommendations
    recommendations = experience_data.get("recommendations", [])
    if recommendations:
        st.write("**💡 Experience Recommendations:**")
        for rec in recommendations:
            st.write(f"• {rec}")

def display_text_results(result: Dict[str, Any]):
    """Display text extraction results."""
    if result.get("success"):
        st.success("✅ Text extracted successfully!")
        
        file_info = result.get("file_info", {})
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File Name", file_info.get("name", "Unknown"))
        with col2:
            st.metric("File Size", file_info.get("size", "Unknown"))
        with col3:
            st.metric("File Type", file_info.get("type", "Unknown"))
        
        extracted_text = result.get("text", "")
        if extracted_text:
            st.subheader("📄 Extracted Text")
            st.text_area("Text content:", value=extracted_text, height=400)
            
            # Download button
            st.download_button(
                label="📥 Download as TXT",
                data=extracted_text,
                file_name=f"{file_info.get('name', 'extracted')}.txt",
                mime="text/plain"
            )
        else:
            st.warning("No text was extracted from the file.")
    else:
        st.error(f"❌ Text extraction failed: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()
