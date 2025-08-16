"""Streamlit web interface for Darzi Resume Parser and Text Extractor."""

import streamlit as st
import requests
import tempfile
import os
from typing import Optional

st.set_page_config(
    page_title="Darzi Resume Parser & Text Extractor",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:7860")  # Set API base URL via environment variable

def main():
    st.title("📄 Darzi Resume Parser & Text Extractor")
    st.markdown("AI-powered resume parsing and document text extraction")

    # Sidebar
    st.sidebar.title("🛠️ Tools")
    tool = st.sidebar.selectbox(
        "Choose a tool:",
        ["Resume Parser", "Text Extractor", "ATS Optimizer"]
    )

    if tool == "Resume Parser":
        resume_parser_interface()
    elif tool == "Text Extractor":
        text_extractor_interface()
    elif tool == "ATS Optimizer":
        ats_optimizer_interface()

def resume_parser_interface():
    st.header("🔍 Resume Parser")
    st.markdown("Extract structured data from resumes (PDF or text)")
    
    # Parser configuration
    st.sidebar.subheader("⚙️ Parser Settings")
    
    # Check parser status first
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

    input_method = st.radio(
        "Input method:",
        ["Upload PDF", "Paste Text"]
    )

    if input_method == "Upload PDF":
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=["pdf"],
            help="Upload a resume in PDF format"
        )

        if uploaded_file is not None and st.button("Parse Resume"):
            with st.spinner("Parsing resume..."):
                try:
                    # Determine endpoint based on parser method
                    if parser_method == "Enhanced (LLM + Fallback)":
                        endpoint = "/parse-enhanced"
                        params = {
                            "use_llm": True,
                            "return_raw": return_raw
                        }
                        if preferred_provider:
                            params["preferred_provider"] = preferred_provider
                    elif parser_method == "LLM Only":
                        endpoint = "/parse-llm-only"
                        params = {"return_raw": return_raw}
                        if preferred_provider:
                            params["preferred_provider"] = preferred_provider
                    else:  # Local Only
                        endpoint = "/parse-local-only"
                        params = {"return_raw": return_raw}
                    
                    response = requests.post(
                        f"{API_BASE_URL}{endpoint}",
                        files={"file": uploaded_file},
                        params=params
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

        if resume_text and st.button("Parse Resume"):
            st.info("📝 Text parsing endpoint will be implemented for enhanced parsing. For now, using legacy endpoint.")
            with st.spinner("Parsing resume..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/parse",
                        data=resume_text,
                        headers={"Content-Type": "text/plain"}
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        display_resume_results(result)
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

def text_extractor_interface():
    st.header("📝 Text Extractor")
    st.markdown("Extract text from PDFs, images, and documents")

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

        if uploaded_file is not None and st.button("Extract Text"):
            with st.spinner("Extracting text..."):
                try:
                    files = {"file": uploaded_file.getvalue()}
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

        if drive_url and st.button("Extract Text from URL"):
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

def ats_optimizer_interface():
    st.header("📊 ATS Optimizer")
    st.markdown("Optimize your resume for Applicant Tracking Systems")

    resume_text = st.text_area(
        "Resume text:",
        height=200,
        help="Paste your resume text here"
    )

    job_description = st.text_area(
        "Job description (optional):",
        height=150,
        help="Paste the job description for keyword matching"
    )

    if resume_text and st.button("Analyze ATS Compatibility"):
        with st.spinner("Analyzing ATS compatibility..."):
            try:
                payload = {
                    "resume_text": resume_text,
                    "job_description": job_description if job_description else ""
                }
                response = requests.post(f"{API_BASE_URL}/optimize-ats", json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    display_ats_results(result)
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Error: {str(e)}")

def display_resume_results(result):
    """Display resume parsing results."""
    if result.get("success"):
        data = result.get("data", {})
        metadata = result.get("metadata", {})
        
        st.success("✅ Resume parsed successfully!")
        
        # Display confidence score
        confidence = data.get("confidence_score", 0)
        st.metric("Confidence Score", f"{confidence:.2f}")
        
        # Create tabs for different sections
        tabs = st.tabs(["Personal Info", "Skills", "Experience", "Education", "Raw Data"])
        
        with tabs[0]:  # Personal Info
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📋 Personal Information")
                st.write(f"**Name:** {data.get('name', 'Not found')}")
                st.write(f"**Summary:** {data.get('summary', 'Not available')}")
            
            with col2:
                st.subheader("📞 Contact")
                emails = data.get('email', [])
                phones = data.get('mobile_number', [])
                st.write(f"**Email:** {', '.join(emails) if emails else 'Not found'}")
                st.write(f"**Phone:** {', '.join(phones) if phones else 'Not found'}")
        
        with tabs[1]:  # Skills
            st.subheader("🛠️ Skills")
            skills = data.get('skills', [])
            if skills:
                # Display skills as tags
                skills_html = " ".join([f"<span style='background-color: #e1f5fe; padding: 4px 8px; margin: 2px; border-radius: 4px; display: inline-block;'>{skill}</span>" for skill in skills])
                st.markdown(skills_html, unsafe_allow_html=True)
            else:
                st.write("No skills found")
        
        with tabs[2]:  # Experience
            st.subheader("💼 Experience")
            experience = data.get('experience', [])
            if experience:
                for i, exp in enumerate(experience):
                    st.write(f"**{i+1}.** {exp}")
            else:
                st.write("No experience found")
        
        with tabs[3]:  # Education
            st.subheader("🎓 Education")
            education = data.get('education', [])
            if education:
                for i, edu in enumerate(education):
                    st.write(f"**{i+1}.** {edu}")
            else:
                st.write("No education found")
        
        with tabs[4]:  # Raw Data
            st.subheader("📄 Raw Data")
            st.json(data)

def display_enhanced_resume_results(result, return_raw=False):
    """Display enhanced resume parsing results with flexible structure."""
    if result.get("status") == "success":
        st.success("✅ Resume parsed successfully!")
        
        # Display metadata
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Parsing Method", result.get("parsing_method", "Unknown").title())
        with col2:
            st.metric("Parsed By", result.get("parsed_by", "Unknown"))
        with col3:
            st.metric("Confidence", f"{result.get('confidence_score', 0)*100:.1f}%")
        with col4:
            st.metric("File Size", result.get("file_size", "Unknown"))
        
        # Show parsing info
        if result.get('llm_available'):
            st.info(f"🤖 LLM Available: {', '.join(result.get('available_providers', []))}")
        else:
            st.warning("⚠️ LLM not available - used local parser")
        
        if result.get('error'):
            st.warning(f"⚠️ Note: {result['error']}")
        
        # Choose which data to display
        if return_raw or 'normalized_data' not in result:
            data_to_display = result.get('raw_data', {})
            st.subheader("📄 Raw Parsed Data")
        else:
            data_to_display = result.get('normalized_data', {})
            st.subheader("📋 Structured Resume Data")
        
        if not data_to_display:
            st.error("No data found in the response")
            return
        
        if return_raw:
            # For raw data, create dynamic tabs based on sections found
            sections = list(data_to_display.keys())
            if '_metadata' in sections:
                sections.remove('_metadata')
            
            if sections:
                tabs = st.tabs([section.replace('_', ' ').title() for section in sections])
                
                for i, section in enumerate(sections):
                    with tabs[i]:
                        st.subheader(f"📁 {section.replace('_', ' ').title()}")
                        section_data = data_to_display[section]
                        
                        if isinstance(section_data, dict):
                            for key, value in section_data.items():
                                if isinstance(value, list):
                                    st.write(f"**{key.replace('_', ' ').title()}:** {', '.join(map(str, value)) if value else 'Not specified'}")
                                else:
                                    st.write(f"**{key.replace('_', ' ').title()}:** {value if value else 'Not specified'}")
                        elif isinstance(section_data, list):
                            for j, item in enumerate(section_data):
                                st.write(f"**{j+1}.** {item}")
                        else:
                            st.write(section_data)
            
            # Show metadata if available
            if '_metadata' in data_to_display:
                st.subheader("🔍 Parsing Metadata")
                st.json(data_to_display['_metadata'])
            
            # Raw JSON view
            with st.expander("🗂️ View Complete Raw JSON"):
                st.json(data_to_display)
        
        else:
            # For normalized data, use structured display
            display_normalized_resume_data(data_to_display)
    
    else:
        st.error("❌ Failed to parse resume")
        if result.get('error'):
            st.error(f"Error: {result['error']}")

def display_normalized_resume_data(data):
    """Display normalized resume data in a structured format."""
    # Extract main sections
    contact_info = data.get('contact_information', {})
    summary = data.get('professional_summary', '')
    experience = data.get('work_experience', [])
    education = data.get('education', [])
    skills = data.get('skills', {})
    projects = data.get('projects', [])
    additional = data.get('additional_sections', {})
    
    # Create tabs for different sections
    tab_names = ["👤 Contact", "📝 Summary", "💼 Experience", "🎓 Education", "🛠️ Skills"]
    if projects:
        tab_names.append("🚀 Projects")
    if additional:
        tab_names.append("📂 Additional")
    tab_names.append("🗂️ Raw Data")
    
    tabs = st.tabs(tab_names)
    tab_index = 0
    
    # Contact Information
    with tabs[tab_index]:
        st.subheader("👤 Contact Information")
        if contact_info:
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Name:** {contact_info.get('full_name', 'Not found')}")
                st.write(f"**Email:** {contact_info.get('email', 'Not found')}")
                st.write(f"**Phone:** {contact_info.get('phone', 'Not found')}")
            with col2:
                st.write(f"**Location:** {contact_info.get('location', 'Not found')}")
                if contact_info.get('linkedin'):
                    st.write(f"**LinkedIn:** {contact_info['linkedin']}")
                if contact_info.get('github'):
                    st.write(f"**GitHub:** {contact_info['github']}")
        else:
            st.write("No contact information found")
    
    tab_index += 1
    
    # Professional Summary
    with tabs[tab_index]:
        st.subheader("📝 Professional Summary")
        if summary:
            st.write(summary)
        else:
            st.write("No professional summary found")
    
    tab_index += 1
    
    # Work Experience
    with tabs[tab_index]:
        st.subheader("💼 Work Experience")
        if experience:
            for i, exp in enumerate(experience):
                with st.expander(f"{exp.get('position', 'Position')} at {exp.get('company', 'Company')}", expanded=i == 0):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Company:** {exp.get('company', 'Not specified')}")
                        st.write(f"**Position:** {exp.get('position', 'Not specified')}")
                    with col2:
                        st.write(f"**Duration:** {exp.get('duration', exp.get('start_date', 'Not specified'))}")
                        st.write(f"**Location:** {exp.get('location', 'Not specified')}")
                    
                    if exp.get('description'):
                        st.write(f"**Description:** {exp['description']}")
                    if exp.get('responsibilities'):
                        st.write("**Responsibilities:**")
                        if isinstance(exp['responsibilities'], list):
                            for resp in exp['responsibilities']:
                                st.write(f"• {resp}")
                        else:
                            st.write(exp['responsibilities'])
                    if exp.get('achievements'):
                        st.write("**Achievements:**")
                        if isinstance(exp['achievements'], list):
                            for achievement in exp['achievements']:
                                st.write(f"• {achievement}")
                        else:
                            st.write(exp['achievements'])
        else:
            st.write("No work experience found")
    
    tab_index += 1
    
    # Education
    with tabs[tab_index]:
        st.subheader("🎓 Education")
        if education:
            for i, edu in enumerate(education):
                with st.expander(f"{edu.get('degree', 'Degree')} from {edu.get('institution', 'Institution')}", expanded=i == 0):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Institution:** {edu.get('institution', 'Not specified')}")
                        st.write(f"**Degree:** {edu.get('degree', 'Not specified')}")
                    with col2:
                        st.write(f"**Field:** {edu.get('field_of_study', 'Not specified')}")
                        st.write(f"**Year:** {edu.get('graduation_year', edu.get('graduation_date', 'Not specified'))}")
                    
                    if edu.get('gpa'):
                        st.write(f"**GPA:** {edu['gpa']}")
                    if edu.get('honors'):
                        st.write(f"**Honors:** {edu['honors']}")
        else:
            st.write("No education found")
    
    tab_index += 1
    
    # Skills
    with tabs[tab_index]:
        st.subheader("🛠️ Skills")
        if skills:
            for skill_category, skill_list in skills.items():
                if skill_list and skill_category != 'general_skills':
                    st.write(f"**{skill_category.replace('_', ' ').title()}:**")
                    if isinstance(skill_list, list):
                        # Display as tags
                        skills_html = " ".join([
                            f"<span style='background-color: #e1f5fe; padding: 4px 8px; margin: 2px; border-radius: 4px; display: inline-block;'>{skill}</span>" 
                            for skill in skill_list
                        ])
                        st.markdown(skills_html, unsafe_allow_html=True)
                    else:
                        st.write(skill_list)
                    st.write("")  # Add spacing
        else:
            st.write("No skills found")
    
    tab_index += 1
    
    # Projects (if available)
    if projects:
        with tabs[tab_index]:
            st.subheader("🚀 Projects")
            for i, project in enumerate(projects):
                with st.expander(f"{project.get('name', f'Project {i+1}')}", expanded=i == 0):
                    st.write(f"**Name:** {project.get('name', 'Not specified')}")
                    if project.get('description'):
                        st.write(f"**Description:** {project['description']}")
                    if project.get('technologies'):
                        st.write("**Technologies:**")
                        if isinstance(project['technologies'], list):
                            tech_html = " ".join([
                                f"<span style='background-color: #f3e5f5; padding: 4px 8px; margin: 2px; border-radius: 4px; display: inline-block;'>{tech}</span>" 
                                for tech in project['technologies']
                            ])
                            st.markdown(tech_html, unsafe_allow_html=True)
                        else:
                            st.write(project['technologies'])
                    if project.get('url'):
                        st.write(f"**URL:** {project['url']}")
        tab_index += 1
    
    # Additional sections (if available)
    if additional:
        with tabs[tab_index]:
            st.subheader("📂 Additional Sections")
            for section_name, section_data in additional.items():
                st.write(f"**{section_name.replace('_', ' ').title()}:**")
                if isinstance(section_data, dict):
                    for key, value in section_data.items():
                        st.write(f"• **{key.replace('_', ' ').title()}:** {value}")
                elif isinstance(section_data, list):
                    for item in section_data:
                        st.write(f"• {item}")
                else:
                    st.write(section_data)
                st.write("")  # Add spacing
        tab_index += 1
    
    # Raw Data
    with tabs[tab_index]:
        st.subheader("🗂️ Complete Data")
        st.json(data)

def display_text_results(result):
    """Display text extraction results."""
    if result.get("success"):
        text = result.get("text", "")
        file_info = result.get("file_info", {})
        
        st.success("✅ Text extracted successfully!")
        
        # Display file info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File Name", file_info.get("name", "Unknown"))
        with col2:
            st.metric("File Size", file_info.get("size", "Unknown"))
        with col3:
            st.metric("File Type", file_info.get("type", "Unknown"))
        
        # Display extracted text
        st.subheader("📄 Extracted Text")
        st.text_area("", value=text, height=400, disabled=True)
        
        # Download button
        st.download_button(
            label="📥 Download Text",
            data=text,
            file_name="extracted_text.txt",
            mime="text/plain"
        )

def display_ats_results(result):
    """Display ATS optimization results."""
    if result.get("success"):
        data = result.get("data", {})
        ats_score = data.get("ats_score", 0)
        suggestions = data.get("suggestions", [])
        
        st.success("✅ ATS analysis completed!")
        
        # Display ATS score with color coding
        score_color = "green" if ats_score >= 70 else "orange" if ats_score >= 50 else "red"
        st.markdown(f"### ATS Score: <span style='color: {score_color}; font-size: 2em;'>{ats_score}/100</span>", unsafe_allow_html=True)
        
        # Display suggestions
        st.subheader("💡 Improvement Suggestions")
        for i, suggestion in enumerate(suggestions, 1):
            st.write(f"{i}. {suggestion}")
        
        # Display optimized sections if available
        optimized_sections = data.get("optimized_sections", {})
        if optimized_sections:
            st.subheader("🔧 Detailed Analysis")
            
            # Keywords analysis
            if "keywords" in optimized_sections:
                keywords_data = optimized_sections["keywords"]
                st.write("**Keyword Matching:**")
                st.write(f"- Match Percentage: {keywords_data.get('match_percentage', 0)}%")
                
                missing_keywords = keywords_data.get('missing_keywords', [])
                if missing_keywords:
                    st.write("**Missing Keywords:**")
                    keywords_html = " ".join([f"<span style='background-color: #ffebee; padding: 4px 8px; margin: 2px; border-radius: 4px; display: inline-block;'>{keyword}</span>" for keyword in missing_keywords[:10]])
                    st.markdown(keywords_html, unsafe_allow_html=True)
            
            # Formatting suggestions
            if "formatting" in optimized_sections:
                formatting_suggestions = optimized_sections["formatting"]
                st.write("**Formatting Recommendations:**")
                for suggestion in formatting_suggestions:
                    st.write(f"- {suggestion}")

if __name__ == "__main__":
    main()
