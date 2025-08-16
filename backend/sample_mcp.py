import os
import dotenv
import smtplib
import requests
from mcp.server.fastmcp import FastMCP
from bs4 import BeautifulSoup
from serpapi import GoogleSearch
from urllib.request import urlopen
from pathlib import Path
from pypdf import PdfReader
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText

dotenv.load_dotenv()
server = FastMCP(name="Automate personal Mail for reaching prof")
"""
1) We would first create the tool to scrapp the the google scholar profile , linkdin and the paper title 
2) In data folder mine resume and cv would be there 
3) Would create the tool to ectract my personal information such as linkdin , kaggle and github 
"""

session = smtplib.SMTP("smtp.gmail.com", 587)
session.starttls()
message = MIMEMultipart()
sender_password = str(os.getenv("PASSWORD"))

def kaggle_scrapper(user_url: str):
    pass


def fetch_github_projects_with_readmes(username):
    """
    Returns a dictionary with repo names as keys and README contents as values.
    If README not found, sets value as None.
    """
    projects = {}
    api_url = f"https://api.github.com/users/{username}/repos"
    headers = {"Accept": "application/vnd.github.v3+json"}

    response = requests.get(api_url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch repositories: {response.status_code}")

    repos = response.json()

    for repo in repos:
    
        # projects[repo_name] = readme_content
    # return projects


def read_datafolder(folder_location: str):
    p = Path(os.path.join(folder_location))
    pdf_in_folder = list(p.glob("/*.pdf"))
    content = dict()
    for pdf in pdf_in_folder:
        content[pdf.name] = []
        reader = PdfReader(pdf)
        for i in range(len(reader.pages)):
            text = reader.pages[i].extract_text()
            content[pdf.name].append(text)

    return content


def read_the_paper_website_url(paper_url: str):
    page = urlopen(paper_url)
    html_bytes = page.read()
    html = html_bytes.decode("utf-8")

    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style"]):
        tag.decompose()

    body = soup.body.get_text(separator="\n")

    lines = [line.strip() for line in body.splitlines() if line.strip()]
    visible_text = "\n".join(lines)

    return visible_text


@server.tool()
def get_my_personal_info():
    """
    This tools would help LLM to get the context of mine and help to write persnalized mail according to professor and given context by me
    """
    content = {
        # "github": fetch_github_projects_with_readmes(username="Aryan-coder-student"),
        "resume_content": read_datafolder(
            folder_location=""
        ),
    }

    return content


@server.tool()
def get_prof_author_id(scholar_id: str):
    """
    Extract the Professor detail
    Return:
        Mail id , list of research title and body , and personal website
    """
    

    # return result


@server.tool()
def get_personal_website(personal_website_url: str):
    """
    This tool would extract the website get the latest , project and on going research
    Args:
        personal_website_url:webite of the prof is available in university or personal website.
    Return:
        Linkdin , mail_id and latest , project and on going research
    """
    extracted_text = read_the_paper_website_url(personal_website_url)

    return extracted_text


@server.tool()
def get_the_research_paper_content(list_of_paper_url: list):
    """
    Get the content of the pepaer of ieee , springer or any other orgainization
    """
    extracted_text_list = []
    for urls in list_of_paper:
        extracted_text_list.append(read_the_paper_website_url(personal_website_url))
    return extracted_text_list


@server.tool()
def send_mail(recipient_mail: str, subject: str, sender_message: str):
    """
    This function sends an email with the generated report by the tool generate_report().
    Args:
        sender_mail (str): The email address of the sender .
        recipient_mail (str): The email address of the recipient.
        subject (str): The subject of the email .
        sender_message (str): The body of the email.
    """
   


@server.prompt()
def generate_research_email(professor_info: str, student_info: str, research_area: str):
    """
    Generate a personalized research internship email to a professor

    Args:
        professor_info: Information about the professor including research interests, recent papers
        student_info: Information about the student including background, projects, skills
        research_area: Specific research area or topic of interest

    Returns:
        A personalized email draft for research internship opportunity
    """
    return f"""
    You are an expert email writer specializing in academic correspondence. 
    
    Write a professional, personalized email to a professor requesting a research internship opportunity.
    
    Professor Information:
    {professor_info}
    
    Student Information:
    {student_info}
    
    Research Area of Interest:
    {research_area}
    
    Guidelines:
    1. Keep the email concise (200-300 words)
    2. Show genuine interest in the professor's specific research
    3. Highlight relevant student background and projects
    4. Be respectful and professional
    5. Include a clear ask for research internship opportunity
    6. Mention resume attachment
    7. Use proper academic email format
    
    Generate both a compelling subject line and email body.
    """


@server.prompt()
def analyze_professor_research():
    """
    Analyze professor's research profile and suggest alignment opportunities

    This prompt helps identify key research areas, recent publications, and potential
    collaboration opportunities based on the professor's academic profile.
    """
    return """
    You are a research analyst specializing in academic profiles.
    
    Analyze the provided professor information and:
    1. Identify their main research areas and interests
    2. Highlight their most recent and impactful publications
    3. Suggest potential collaboration opportunities
    4. Identify keywords and topics that should be mentioned in outreach
    5. Assess their openness to working with students based on their profile
    
    Provide a structured analysis that can be used to craft targeted outreach emails.
    """


@server.prompt()
def optimize_student_profile():
    """
    Optimize student profile presentation for academic outreach

    This prompt helps present the student's background, projects, and skills
    in the most compelling way for academic research opportunities.
    """
    return """
    You are a career counselor specializing in academic opportunities.
    
    Based on the student's background information (GitHub projects, resume, skills):
    1. Identify the most relevant projects and experiences for research
    2. Highlight technical skills that align with academic research
    3. Suggest how to present achievements in an academic context
    4. Recommend specific talking points for different research areas                                                       
    5. Identify any gaps that should be addressed or strengths to emphasize
    
    Provide recommendations for presenting the student profile effectively to professors.
    """


@server.prompt()
def create_followup_strategy():
    """
    Create a follow-up strategy for academic outreach

    This prompt helps design appropriate follow-up communications and timing
    for research internship requests.
    """
    return """
    You are an academic networking expert.
    
    Create a strategic follow-up plan for research internship outreach:
    1. Appropriate timing for follow-up emails
    2. Content variations for different follow-up attempts
    3. Alternative approaches if initial outreach fails
    4. Ways to add value in follow-up communications
    5. When to stop following up professionally
    
    Include template variations for different scenarios (no response, positive interest, need more info, etc.).
    """


if _name_ == "_main_":
    server.run()