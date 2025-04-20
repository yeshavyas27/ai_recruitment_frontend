import streamlit as st
import requests
import json
from typing import Dict, List, Optional, Any
import pandas as pd

# API Base URL
API_BASE_URL = "https://ai-driven-recruitment.onrender.com"

# Page configuration
st.set_page_config(
    page_title="AI-Driven Recruitment Platform",
    page_icon="👔",
    layout="wide"
)

# Session state initialization
if "user_token" not in st.session_state:
    st.session_state.user_token = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "role" not in st.session_state:
    st.session_state.role = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "login"

if st.session_state.role == "candidate":
    if "profile_education_fields"  not in st.session_state:
        st.session_state.profile_education_fields = 1
    if "education_data" not in st.session_state:
        st.session_state.education_data = [{}]
    if "profile_experience_fields" not in st.session_state:
        st.session_state.profile_experience_fields = 1
    if "experience_data" not in st.session_state:
        st.session_state.experience_data = [{}]
    if "profile_projects_fields" not in st.session_state:   
        st.session_state.profile_projects_fields = 1
    if "projects_data" not in st.session_state:
        st.session_state.projects_data = [{}]
    if "s3_link" not in st.session_state:
        st.session_state.s3_link = None


# Helper functions
def api_request(endpoint: str, method: str = "GET", data: Optional[Dict] = None, 
                token: Optional[str] = None, params: Optional[Dict] = None, form_data: bool = False) -> Dict:
    """Make an API request to the backend"""
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            if form_data:
                headers["Content-Type"] = "application/x-www-form-urlencoded"
                response = requests.post(url, headers=headers, data=data)
            else:
                headers["Content-Type"] = "application/json"
                response = requests.post(url, headers=headers, json=data, params=params)
        elif method == "PUT":
            headers["Content-Type"] = "application/json"
            response = requests.put(url, headers=headers, json=data)
        
        return response
    except Exception as e:
        st.error(f"API request failed: {str(e)}")
        return {"error": str(e)}


def logout():
    """Log out the current user"""
    st.session_state.user_token = None
    st.session_state.user_id = None
    st.session_state.role = None
    st.session_state.current_page = "login"

def navigate_to(page: str):
    """Navigate to a specific page"""
    st.session_state.current_page = page

# Authentication pages
def login_page():
    """Login page for users"""
    st.title("AI-Driven Recruitment Platform")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.subheader("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login"):
            if not username or not password:
                st.error("Please fill in all fields")
            else:
                data = {
                    "username": username,
                    "password": password
                }
                
                response = api_request(f"/token", "POST", data, form_data=True)
                
                if response.status_code in (200, 201):
                    st.session_state.user_token = response.json()["access_token"]
                    
                    # Get user ID
                    user_info = api_request(f"/me", "GET", token=st.session_state.user_token)
                    if response.status_code in (200, 201):
                        user_details = user_info.json()
                        st.session_state.user_id = user_details["user_id"]
                        st.session_state.role = user_details["role"]
                        
                        if st.session_state.role == "candidate":
                            navigate_to("candidate_profile")
                        else:
                            navigate_to("recruiter_find_candidates")
                        st.rerun()
                    else:
                        st.error(f"Error: {response.json()["detail"]}")
                else:
                    # st.error(f"Error: {response.status_code} - {response.text["detail"]}")
                    st.error(f"Error: {response.json()["detail"]}")
    
    with tab2:
        st.subheader("Sign Up")
        name = st.text_input("Username", key="signup_username")
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password")
        role = st.selectbox("User Role", ["candidate", "recruiter"], key="signup_role")
        
        if st.button("Sign Up"):
            if not name or not email or not password:
                st.error("Please fill in all fields")
            else:
                data = {
                    "username": name,
                    "email": email,
                    "password": password,
                    "role": role
                }
                
                response = api_request(f"/signup", "POST", data)
                
                if response.status_code in (200, 201):
                    st.session_state.user_token = response.json()["access_token"]
                    st.success(f"Account created successfully!")
                    user_info = api_request(f"/me", "GET", token=st.session_state.user_token)
                    if response.status_code in (200, 201):
                        user_details = user_info.json()
                        st.session_state.user_id = user_details["user_id"]
                        st.session_state.role = user_details["role"]
                        
                        if st.session_state.role == "candidate":
                            navigate_to("candidate_profile")
                        else:
                            navigate_to("recruiter_dashboard")
                        st.rerun()
                    else:
                        st.error(f"Error: {response.json()["detail"]}")
                else:
                    st.error(f"Error: {response.json()["detail"]}")

# Navigation
def show_navigation():
    """Display navigation bar"""
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        st.write(f"Logged in as: {st.session_state.role.capitalize()}")
    
    if st.session_state.role == "candidate":
        with col2:
            if st.button("Dashboard", use_container_width=True):
                navigate_to("candidate_dashboard")
        with col3:
            if st.button("My Profile", use_container_width=True):
                navigate_to("candidate_profile")
    else:  # recruiter
        # with col2:
        #     if st.button("Dashboard", use_container_width=True):
        #         navigate_to("recruiter_dashboard")
        with col3:
            if st.button("Find Matches", use_container_width=True):
                navigate_to("recruiter_find_matches")
    
    with col4:
        if st.button("Logout", use_container_width=True):
            logout()
            st.rerun()
    
    st.divider()

# Candidate pages
def candidate_dashboard():
    """Dashboard for candidates"""
    show_navigation()
    st.title("Candidate Dashboard")
    # add a input box to enter the job link, and a button to find the match score
    job_link = st.text_input("Enter Job Link")
    match_criteria = st.selectbox("Select Match Criteria", ["Strict", "Moderate", "Flexible"])

    if match_criteria == "Strict":
        match_criteria_value = 3
    elif match_criteria == "Moderate":
        match_criteria_value = 2 
    elif match_criteria == "Flexible":  
        match_criteria_value = 1

    if st.button("Find Match Score"):
        if job_link:
            # Call the API to get the match score
            query_params = {
                "job_link": job_link,
                "match_criteria": match_criteria_value
            }
            response = api_request(f"/candidate/match_with_job", "GET",params=query_params, token=st.session_state.user_token)
            st.success(f"Your match score for this job is: {response.json()}")

@st.cache_resource
def get_candidate_profile():
    # send request to get profile for this user, and display it in the form
    response = api_request(f"/candidate/get_profile", method="GET", token=st.session_state.user_token)
    if response.status_code in  (200, 201):
        data = response.json()
        resume_data = data["parsed_resume"]
        st.session_state.s3_link = data["s3_link"] if data.get("s3_link") else None
        if resume_data.get("education"):
            st.session_state.education_data = resume_data.get("education")
            st.session_state.profile_education_fields = len(st.session_state.education_data)
        if resume_data.get("experience"):
            st.session_state.experience_data = resume_data.get("experience")
            st.session_state.profile_experience_fields = len(st.session_state.experience_data)
        if resume_data.get("accomplishments_and_projects"): 
            st.session_state.projects_data = resume_data.get("accomplishments_and_projects")
            st.session_state.profile_projects_fields = len(st.session_state.projects_data)
        return False, resume_data
    else:
        return True, {}
    
@st.cache_resource
def autofill_profile(uploaded_file):
    # Send the uploaded file to the API
            files = {"file": uploaded_file}
            response = requests.post(
                f"{API_BASE_URL}/candidate/parse_resume",
                headers={"Authorization": f"Bearer {st.session_state.user_token}"},
                files=files
            )
            if response.status_code in  (200, 201):
                st.success("Resume parsed successfully!")
                data = response.json()
                resume_data = data["parsed_resume"]
                st.session_state.s3_link = data["s3_link"]
                if resume_data.get("education"):
                    st.session_state.education_data = resume_data.get("education")
                    st.session_state.profile_education_fields = len(st.session_state.education_data)
                if resume_data.get("experience"):
                    st.session_state.experience_data = resume_data.get("experience")
                    st.session_state.profile_experience_fields = len(st.session_state.experience_data)
                if resume_data.get("accomplishments_and_projects"): 
                    st.session_state.projects_data = resume_data.get("accomplishments_and_projects")
                    st.session_state.profile_projects_fields = len(st.session_state.projects_data)
            else:
                st.error(f"Error: {response.json()["detail"]}")


def candidate_profile():
    """Profile page for candidates"""
    show_navigation()
    st.title("Candidate Profile")
    new_profile, resume_data = get_candidate_profile()
    

    # add link to view the resume file 
    st.write(f"[View Resume]({st.session_state.s3_link})")

    st.write("Autofill Profile with Resume")
    uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])


    if uploaded_file is not None:
        autofill_profile(uploaded_file)
    else:
        st.info("Please upload a resume to autofill your profile.")
    
    
    with st.expander("Basic Information", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name", value=resume_data.get("name", ""))
        with col2:
            linkedin = st.text_input("LinkedIn URL", value=resume_data.get("linkedin", ""))
            github = st.text_input("GitHub URL", value=resume_data.get("github", ""))
        
        total_exp = st.text_input("Total Years of Experience", value=resume_data.get("total_years_of_experience", ""))

    # Skills section
    with st.expander("Skills", expanded=True):
        st.subheader("Your Skills")
        
        skills = resume_data.get("skills", [])
        if skills:
            skills_text = ", ".join(skills)
        else:
            skills_text = ""
        
        new_skills = st.text_area(
            "Skills (comma separated)",
            value=skills_text,
            help="Enter skills separated by commas"
        )
        
        # Process skills from text area to list
        if new_skills:
            skills_list = [skill.strip() for skill in new_skills.split(",") if skill.strip()]
        else:
            skills_list = []

    # Education section
    with st.expander("Education", expanded=True):
        st.subheader("Education History")

        # Function to create education entry form
        for edu_idx in range(st.session_state.profile_education_fields):
            
            if edu_idx >= len(st.session_state.education_data):
                break
            edu = st.session_state.education_data[edu_idx]

            with st.container():
                st.markdown(f"**Education #{edu_idx + 1}**")
                col1, col2 = st.columns(2)
                with col1:
                    institution = st.text_input(f"Institution", value=edu.get("institution", ""), key=f"inst_{edu_idx}")
                    degree = st.text_input(f"Degree", value=edu.get("degree", ""), key=f"deg_{edu_idx}")
                with col2:
                    gpa = st.text_input(f"GPA", value=edu.get("GPA", ""), key=f"gpa_{edu_idx}")
                    graduation = st.text_input(f"Graduation Date", value=edu.get("graduation", ""), key=f"grad_{edu_idx}")
                
                coursework_text = ", ".join(edu.get("coursework", []))
                coursework = st.text_area(
                    f"Relevant Coursework", 
                    value=coursework_text, 
                    key=f"course_{edu_idx}",
                    help="Enter coursework separated by commas"
                )
                coursework_list = [course.strip() for course in coursework.split(",") if course.strip()]

                data = {
                    "institution": institution,
                    "degree": degree,
                    "GPA": gpa,
                    "graduation": graduation,
                    "coursework": coursework_list
                }
                st.session_state.education_data[edu_idx] = data

                if st.markdown("<br>", unsafe_allow_html=True): 
                    if st.button(f"Remove ❌", key=f"delete_edu_{edu_idx}"):
                        if st.session_state.profile_education_fields > 0:
                            st.session_state.education_data.pop(edu_idx)
                            st.session_state.profile_education_fields -= 1 
                    
                
                st.markdown("---")
                
        # Add new education button
        if st.button("Add Another Education"):
            st.session_state.profile_education_fields += 1
            st.session_state.education_data.append({})
            
    # Experience section
    with st.expander("Experience", expanded=True):
        st.subheader("Work Experience")

        for exp_idx in range(st.session_state.profile_experience_fields):
            if exp_idx >= len(st.session_state.experience_data):
                break
            exp = st.session_state.experience_data[exp_idx]

            with st.container():
                st.markdown(f"**Experience #{exp_idx + 1}**")
                col1, col2 = st.columns(2)
                with col1:
                    role = st.text_input(f"Role/Position", value=exp.get("role", ""), key=f"role_{exp_idx}")
                    organization = st.text_input(f"Organization", value=exp.get("organization", ""), key=f"org_{exp_idx}")
                with col2:
                    start_date = st.text_input(f"Start Date", value=exp.get("timeline", {}).get("start", ""), key=f"start_{exp_idx}")
                    end_date = st.text_input(f"End Date", value=exp.get("timeline", {}).get("end", ""), key=f"end_{exp_idx}")

                details_text = "\n".join(exp.get("details", []))
                details = st.text_area(
                    f"Details (one per line)", 
                    value=details_text, 
                    key=f"details_{exp_idx}",
                    help="Enter each bullet point on a new line"
                )
                details_list = [detail.strip() for detail in details.split("\n") if detail.strip()]

                skills_related_text = ", ".join(exp.get("skills_related", []))
                skills_related = st.text_input(
                    f"Skills Used", 
                    value=skills_related_text, 
                    key=f"skills_exp_{exp_idx}",
                    help="Enter skills separated by commas"
                )
                skills_related_list = [skill.strip() for skill in skills_related.split(",") if skill.strip()]

                data = {
                    "role": role,
                    "organization": organization,
                    "timeline": {"start": start_date, "end": end_date},
                    "details": details_list,
                    "skills_related": skills_related_list
                }
                st.session_state.experience_data[exp_idx] = data

                if st.markdown("<br>", unsafe_allow_html=True):
                    if st.button(f"Remove ❌", key=f"delete_exp_{exp_idx}"):
                        if st.session_state.profile_experience_fields > 0:
                            st.session_state.experience_data.pop(exp_idx)
                            st.session_state.profile_experience_fields -= 1

                st.markdown("---")

        if st.button("Add Another Experience"):
            st.session_state.profile_experience_fields += 1
            st.session_state.experience_data.append({})

    # Projects & Accomplishments section
    with st.expander("Projects & Accomplishments", expanded=True):
        st.subheader("Projects and Accomplishments")

        for proj_idx in range(st.session_state.profile_projects_fields):
            if proj_idx >= len(st.session_state.projects_data):
                break
            proj = st.session_state.projects_data[proj_idx]

            with st.container():
                st.markdown(f"**Project #{proj_idx + 1}**")
                name = st.text_input(f"Project Name", value=proj.get("name", ""), key=f"proj_{proj_idx}")

                skills_related_text = ", ".join(proj.get("skills_related", []))
                skills_related = st.text_input(
                    f"Skills Used", 
                    value=skills_related_text, 
                    key=f"skills_proj_{proj_idx}",
                    help="Enter skills separated by commas"
                )
                skills_related_list = [skill.strip() for skill in skills_related.split(",") if skill.strip()]

                details_text = "\n".join(proj.get("details", []))
                details = st.text_area(
                    f"Details (one per line)", 
                    value=details_text, 
                    key=f"proj_details_{proj_idx}",
                    help="Enter each bullet point on a new line"
                )
                details_list = [detail.strip() for detail in details.split("\n") if detail.strip()]

                data = {
                    "name": name,
                    "skills_related": skills_related_list,
                    "details": details_list
                }
                st.session_state.projects_data[proj_idx] = data

                if st.markdown("<br>", unsafe_allow_html=True):
                    if st.button(f"Remove ❌", key=f"delete_proj_{proj_idx}"):
                        if st.session_state.profile_projects_fields > 0:
                            st.session_state.projects_data.pop(proj_idx)
                            st.session_state.profile_projects_fields -= 1

                st.markdown("---")

        if st.button("Add Another Project"):
            st.session_state.profile_projects_fields += 1
            st.session_state.projects_data.append({})

        
    # Save profile
    if st.button("Save Profile"):
        # Prepare update data
        request_data = {
            "parsed_resume": {
            "name": name,
            "linkedin": linkedin,
            "github": github,
            "skills": skills_list,
            "education": st.session_state.education_data,
            "experience": st.session_state.experience_data,
            "accomplishments_and_projects": st.session_state.projects_data,
            "total_years_of_experience": total_exp,
            },
            "s3_link": st.session_state.s3_link,
        }
        
        if new_profile:
            # Send update request
            response = api_request(
                f"/candidate/save_profile",
                method="POST",
                data=request_data,
                token=st.session_state.user_token
            )
            
            if response.status_code in (200, 201):
                st.success("Profile saved successfully!")
            else:
                st.error(f"Error: {response.json()["detail"]}")
        else:
            # Send update request
            response = api_request(
                f"/candidate/update_profile",
                method="PUT",
                data=request_data,
                token=st.session_state.user_token
            )
            
            if response.status_code in (200, 201):
                st.success("Profile updated successfully!")
            else:
                st.error(f"Error: {response.json()["detail"]}")


def view_candidate_profile(resume_data):
    """View candidate profile"""
    st.subheader("Candidate Profile")
    
    # Display basic information
    st.write(f"**Name:** {resume_data.get('name', '')}")
    st.write(f"**LinkedIn:** {resume_data.get('linkedin', '')}")
    st.write(f"**GitHub:** {resume_data.get('github', '')}")
    
    # Display skills
    st.write("**Skills:**")
    skills = resume_data.get("skills", [])
    if skills:
        st.write(", ".join(skills))
    
    # Display education
    st.write("**Education:**")
    education = resume_data.get("education", [])
    for edu in education:
        st.write(f"- {edu.get('degree', '')} from {edu.get('institution', '')} (GPA: {edu.get('GPA', '')})")
    
    # Display experience
    st.write("**Experience:**")
    experience = resume_data.get("experience", [])
    for exp in experience:
        st.write(f"- {exp.get('role', '')} at {exp.get('organization', '')} ({exp.get('timeline', {}).get('start', '')} to {exp.get('timeline', {}).get('end', '')}): { ' '.join(exp.get('details', []))} ")
    
    # Display projects and accomplishments
    st.write("**Projects & Accomplishments:**")
    projects = resume_data.get("accomplishments_and_projects", [])
    for proj in projects:
        st.write(f"- {proj.get('name', '')}: {' '.join(proj.get('details', []))}")

def recruiter_find_matches():
    """Page for finding candidates based on job link and resumes"""
    show_navigation()
    st.title("Find Matches")
    
    # Add required field indicator at the top of the form
    st.markdown("<small style='color: red;'>* Required field</small>", unsafe_allow_html=True)

    # Input fields with required indicator
    job_link = st.text_input(
        "Enter Job Link *", 
        placeholder="https://www.example.com/job-posting",
        help="Required field - paste the URL of the job posting"
    )
    
    match_criteria = st.selectbox(
        "Select Match Criteria", 
        options=["Flexible", "Moderate", "Strict"],
        index=1,  # Default to Moderate
        help="Strict (3) requires exact matches, Moderate (2) is balanced, Flexible (1) allows more variation"
    )
    
    include_existing_resumes = st.checkbox("Include existing resumes stored in database", value=True)
    
    uploaded_files = st.file_uploader(
        "Upload new resumes for matching (PDF)", 
        type="pdf", 
        accept_multiple_files=True
    )
    
    if st.button("Find Matches", type="primary"):
        if not job_link:
            st.error("Please enter a job link to continue. This is a required field.")
            return
            
        # Map UI selection to API expected values
        match_criteria_map = {
            "Strict": 3,
            "Moderate": 2,
            "Flexible": 1
        }
        
        # Set up query parameters
        params = {
            "job_link": job_link,
            "match_criteria": match_criteria_map[match_criteria],
            "include_existing_resumes": include_existing_resumes
        }
        
        # Create multipart/form-data format exactly matching the curl example
        files = []
        
        if uploaded_files:
            for file in uploaded_files:
                # Add each file with the same field name 'resume_files'
                files.append(
                    ('resume_files', (file.name, file.getvalue(), 'application/pdf'))
                )
        
        try:
            with st.spinner("Finding matches..."):
                # Make the API request
                response = requests.post(
                    f"{API_BASE_URL}/recruiter/find_matches",
                    headers={"Authorization": f"Bearer {st.session_state.user_token}"},
                    params=params,
                    files=files if files else None,  # Only include files if there are any
                )
                
                if response.status_code == 200:
                    matches = response.json()
                    
                    # Display results
                    if len(matches) > 0:
                        st.success(f"Found {len(matches)} matches!")
                        
                        # Create a dataframe for better display
                        match_df = pd.DataFrame(matches)
                        match_df['match_score'] = match_df['match_score'].astype(int)
                        
                        # Store just the URLs in the dataframe - don't use markdown syntax here
                        match_df['resume_url'] = match_df['resume_link']
                        
                        match_df['profile'] = match_df['user_profile']
                        # Display the results table with proper link configuration
                        for _, row in match_df.iterrows():
                            with st.expander(f"Match Score: {row['match_score']}% "):
                                st.write("Check out their [resume](%s)" % row['resume_url'])
                                view_candidate_profile(row['profile'])
                    else:
                        st.info("No matches found for this job posting")
                else:
                    error_detail = "Unknown error occurred"
                    try:
                        error_response = response.json()
                        error_detail = error_response.get("detail", f"Error: Status code {response.status_code}")
                    except:
                        error_detail = f"Error: Status code {response.status_code}"
                    st.error(error_detail)
        except Exception as e:
            st.error(f"Connection error: {str(e)}")
            
# Main app logic
def main():
    """Main app logic based on current page"""
    if not st.session_state.user_token:
        login_page()
    else:
        # Route to the correct page based on session state
        if st.session_state.current_page == "candidate_dashboard":
            candidate_dashboard()
        elif st.session_state.current_page == "candidate_profile":
            candidate_profile()
        elif st.session_state.current_page == "recruiter_find_matches":
            recruiter_find_matches()
        else:
            # Default route based on user type
            if st.session_state.role == "candidate":
                candidate_dashboard()
            else:
                recruiter_find_matches()

if __name__ == "__main__":
    main()