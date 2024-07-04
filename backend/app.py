from flask import Flask, request, jsonify, render_template
import os
import fitz
from jinja2 import Environment, FileSystemLoader
import google.generativeai as genai
# import openai


app = Flask(__name__)

# Set up the environment for Jinja2
env = Environment(loader=FileSystemLoader('templats'))

genai.configure(api_key=os.environ["API_KEY"])

# openai.api_key = os.getenv('OPENAI_API_KEY')

model = genai.GenerativeModel('gemini-1.5-flash')

possible_sections = [
    'SUMMARY', 'ABOUT', 'ABOUT ME', 'EXPERIENCE', 'WORK EXPERIENCE',
    'PROFESSIONAL EXPERIENCE', 'PROJECT', 'PROJECTS', 'PROJECT EXPERIENCE', 'RELATED EXPERIENCE', 'LEADERSHIP', 'EDUCATION',
    'SKILLS', 'CERTIFICATIONS', 'AWARDS', 'ADDITIONAL', 'OTHER', 'INTERESTS', 'ADDITIONAL INTERESTS'
]
headers = ["About", "Education", "Experience", "Skills", "Projects", "Awards", "Other"]
def base(key):
    key = key.lower()
    if(key == 'summary' or key == 'about' or key == 'about me'):
        return 'About'
    elif(key == 'experience' or key == 'work experience' or key == 'professional experience' or key == 'related experience' or key == 'leadership'):
        return 'Experience'
    elif(key == 'project' or key == 'projects' or key == 'project experience'):
        return 'Projects'
    elif(key == 'education'):
        return 'Education'
    elif(key == 'awards'):
        return 'Awards'
    elif(key == 'skills' or key == 'certifications'):
        return 'Skills'
    else:
        return 'Other'

def capitalize_and_append(sections):
    capitalized_sections = []
    for section in sections:
        words = section.split()
        sec = ''
        for word in words:
            sec += word.capitalize() + " "
        capitalized_sections.append(sec.rstrip())
    sections.extend(capitalized_sections)
    return sections

capitalize_and_append(possible_sections)

# Function to extract text from a PDF file using PyMuPDF
def extract_text_from_pdf(file_path):
    text = ''
    with fitz.open(file_path) as doc:
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            text += page.get_text()
            text += '\n'  # Add a newline after each page
    # def remove_preceding_newlines(text):
    #     lines = text.split('\n')
    #     result = []
        
    #     for i in range(len(lines)):
    #         if (lines[i] and (lines[i][0].islower() or (lines[i][1] and lines[i][1].islower())) and result) :
    #             # Append the current line to the previous line
    #             result[-1] += " " + lines[i]
    #         else:
    #             # Add the current line as a new line in the result
    #             result.append(lines[i])
    #     return '\n'.join(result)
    
    return text

def classify_sections(text):
    # Initialize the sections dictionary
    sections = {section: '' for section in possible_sections}
    current_section = None
    contact = ''
    # Split the text into lines
    lines = text.split('\n')
    
    for line in lines:
        # print(line)
        # print(current_section)
        if line in possible_sections:
            current_section = line
        elif line and line.split()[0] in possible_sections:
            current_section = line.split()[0]
            # sections[current_section]+=line + " " # without first word
        elif len(line.split())>1 and ' '.join(line.split()[:2]) in possible_sections:
            current_section = ' '.join(line.split()[:2])
            # sections[current_section]+=line + " " # without first two words
        else:
            if current_section != None:
                sections[current_section]+=line + " "
            else:
                contact += line + " "
    
    # for key, value in sections.items():
    #     print(key + ":")
    #     print(value)
    #     print()
    # print("-------------------------------")    
    def reclassify(sections):
        divs = {header: '' for header in headers}
        for key, value in sections.items():
            if value:
                divs[base(key)] += value + " "
        return divs
    
    sections = reclassify(sections)    # organizes sections into divs of website
    # for key, value in sections.items():
    #     print(key + ":")
    #     print(value)
    #     print()
    # return
    def updateEducation(sections):
        prompt_input = sections['Education']

        prompt = f"Here is some text:\n\n{prompt_input}\n\nOrganize all of this text into 3 sections based on what category they fit in:\n\n1. University, degree, GPA\n2. Courses\n3. Activities, extracurriculars\n\nKeep in mind that input might not include all parts of every section, but every word in the input should fit into one of the 3 sections. Your output should just be 3 lines long, with each line corresponding to the words that fit into the sections in the same order they were presented to you initially. Don't include the section number in your output."
        
        response = model.generate_content(prompt)
        # replace this:
        # class Response:
        #     text = ''
        # response = Response()
        # response.text = "UNIVERSITY OF MICHIGAN – Ann Arbor, MI Expected May 2026 Bachelor of Science Engineering, Computer Science; Cumulative GPA: 4.0/4.0\nDiscrete Mathematics, Algorithms/Data Structures, Probability/Statistics, Foundations of CS\nSidney J. and Irene Shipman Scholarship/Society, Michigan Hackers, MRacing Autonomous\n"
        
        education_1 = response.text.split('\n')[0]
        education_2 = response.text.split('\n')[1]
        education_3 = response.text.split('\n')[2]

        # del sections['Education']
        sections['education_1'] = education_1
        sections['education_2'] = education_2
        sections['education_3'] = education_3
    
    def updateExperience(sections):
        # what if one experience has multiple positions?
        prompt_input = sections['Experience']
        # print(prompt_input)
        prompt = f"Here is some text:\n\n{prompt_input}\n\nOrganize all of this text into 2 sections, which 3 subsections each, based on what category they fit in:\n1. Experience 1 name\n2. Position/title of experience 1\n3. Start to end date of experience 1, formatted like start date - end date \n4. Experience 2 name\n5. Position/title of experience 2\n6. Start to end date of experience 2, formatted like start date - end date\nDon't include locations or places of employment in any of the sections.\nIf more than 2 experiences are in the input, ignore the additional experiences. If only one experience is in the input, put empty section (either 'empty experience', 'empty position', or 'empty date') in sections 4-6, respectively. Keep in mind that input might not include all parts of every section, and that not all words have to fit into a section. Your output should just be 6 lines long, with each line corresponding to the words that fit into the sections in the same order they were presented to you initially. Don't include the section number in your output."
        response = model.generate_content(prompt)
        # print(response.text)
        experience_1 = response.text.split('\n')[0]
        position_1 = response.text.split('\n')[1]
        date_1 = response.text.split('\n')[2]
        experience_2 = response.text.split('\n')[3]
        position_2 = response.text.split('\n')[4]
        date_2 = response.text.split('\n')[5]
        # del sections['Experience']
        sections['experience_1'] = experience_1
        sections['position_1'] = position_1
        sections['date_1'] = date_1
        sections['experience_2'] = experience_2
        sections['position_2'] = position_2
        sections['date_2'] = date_2
               
        
    def updateProjects(sections):
        prompt_input = sections['Projects']
        prompt = f"Here is some text:\n\n{prompt_input}\n\nOrganize all of this text into 4 sets of 2 sections each, based on what category they fit in, for a total of 8 sections:\n1. Project 1 name\n2. Project 1 description 1\n3. Project 2 name \n4. Project 2 description\n5. Project 3 name\n6. Project 3 description\n7. Project 4 name\n8. Project 4 description\nIf more than 4 projects are in the input, ignore the additional projects. If less than 4 projects are in the input, put empty section (either 'empty project name', or 'empty project description') in the corresponding empty sections. Keep in mind that input might not include all parts of every section, and that not all words have to fit into a section. Your output should be 8 lines long (even if less than 4 projects are in the input), with each line corresponding to the words that fit into the sections in the same order they were presented to you initially. Don't include the section number in your output. For the sections that ask for a project name, include only the name (not any links, locations, places of employment, or dates). Also for the project name, format it such that only the first letters of words are capitalized, rather than all caps. For the project description, summarize the description of the project (less than 100 characters of text) into a resume bullet point style, starting with an action verb. Don't include any bullet point characters or periods in project description, and keep project description within 100 characters of text, retaining only the most important information. All sections must have a maximum of 100 characters of text - this is a strict limit. In an effort to keep it concise and avoid repetition or redundancy, delete any tools, languages, or frameworks from the project description and replace them in parantheses at the end of the description. Don't use periods."
        response = model.generate_content(prompt)
        # print(response.text)
        p1 = response.text.split('\n')[0]
        p1_desc = response.text.split('\n')[1]
        p2 = response.text.split('\n')[2]
        p2_desc = response.text.split('\n')[3]
        p3 = response.text.split('\n')[4]
        p3_desc = response.text.split('\n')[5]
        p4 = response.text.split('\n')[6]
        p4_desc = response.text.split('\n')[7]
        # del sections['Projects']
        sections['p1'] = p1
        sections['p1_desc'] = p1_desc
        sections['p2'] = p2
        sections['p2_desc'] = p2_desc
        sections['p3'] = p3
        sections['p3_desc'] = p3_desc 
        sections['p4'] = p4
        sections['p4_desc'] = p4_desc 
        
    updateEducation(sections)
    updateExperience(sections)
    updateProjects(sections)
    prompt_input = contact
    prompt = f"Here is some text: \n{prompt_input}\nOrganize all of this text into 6 sections: 1. First name 2. Last name 3. Email address 4. Phone number 5. First company and link 6. Second company and link Organize this information into 6 sections, and then print the sections on 6 separate lines in plain text, in the order I presented them to you. Don't include the section number. For sections 5 to 6 that include links, write the company that the link refers to, followed by the link from the original text input. If the link doesn't start with https://, add https:// to the beginning of the link. University email addresses are not companies or links, so don't include them in sections 5-6. Section 3 should just be the email, no parentheses. For example, a Youtube link should output 'Youtube' followed by the link starting with https://. If you identify less than 2 links, write 'empty company' for the company and 'empty link' for the link. If you identify more than 2 links, ignore the links after the first two. Keep in mind that not every word in the input text must fit into any of the sections - in particular, any locations, addresses, or dates should be ignored. If first name, last name, email, or phone number are also not available in the input text, write 'empty' followed by the name of the section."
    response = model.generate_content(prompt)
    output = response.text
    descriptors = {
        'first_name' : output.split('\n')[0],
        'last_name' : output.split('\n')[1],
        'email' : output.split('\n')[2],
        'phone_number' : output.split('\n')[3],
        'company_1' : output.split('\n')[4],
        'link_1' : output.split('\n')[5],
        'company_2' : output.split('\n')[6],
        'link_2' : output.split('\n')[7],
        'About' : "I'm a rising sophomore at the University of Michigan expecting to graduate in May 2026. I'm interested in Artificial Intelligence &amp; Web Development, and I have been able to explore these fields through my coursework and projects."
    }
    sections.update(descriptors) # might need to reverse based on about section
    return sections

def generate_html(sections):
    template = env.get_template('template.html')
    html_content = template.render(
        first_name = sections['first_name'],
        last_name = sections['last_name'],
        about = sections['About'],
        email = sections['email'],
        phone_number = sections['phone_number'],
        education_1 = sections['education_1'],
        education_2 = sections['education_2'],
        education_3 = sections['education_3'],
        experience_1 = sections['experience_1'],
        position_1 = sections['position_1'],
        date_1 = sections['date_1'],
        experience_2 = sections['experience_2'],
        position_2 = sections['position_2'],
        date_2 = sections['date_2'],
        p1 = sections['p1'],
        p2 = sections['p2'],
        p3 = sections['p3'],    
        p4 = sections['p4'],  
        p1_desc = sections['p1_desc'],
        p2_desc = sections['p2_desc'],
        p3_desc = sections['p3_desc'],    
        p4_desc = sections['p4_desc'],
        company_1 = sections['company_1'],
        link_1 = sections['link_1'],
        company_2 = sections['company_2'],
        link_2 = sections['link_2']       
    )
    return html_content
    
file_path = "/Users/sriyanm/PortfolioGenerator/attempt_2/backend/uploads/resume.pdf"
text = extract_text_from_pdf(file_path)
with open('text.txt', 'w') as file: # debug extracted text
    file.write(text)

sections = classify_sections(text)
for key, value in sections.items():
    print(key + ":")
    print(value)
    print()
html_content = generate_html(sections)

with open('../frontend/index.html', 'w') as f:
    f.write(html_content)