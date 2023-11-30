import os
import spacy
import pdfplumber
import re
import multiprocessing as mp
import pprint
from linkedin_scraper import Person

class CustomResumeParser(object):
    def __init__(self, resume):
        self.__details = {
            'name': None,
            'email': None,
            'mobile_number': None,
            'skills': None,
            'education': None,
            'experience': None,
            'competencies': None,
            'measurable_results': None,
            'linkedin': None
        }
        self.__resume = resume
        self.__text_raw = self.__load_resume_text()
        self.__nlp = spacy.load("en_core_web_sm")
        self.__noun_chunks = list(self.__nlp(self.__text_raw).noun_chunks)
        self.__get_basic_details()

    def __load_resume_text(self):
        with pdfplumber.open(self.__resume) as pdf:
            text = ''
            for page in pdf.pages:
                text += page.extract_text()
            return text

    def get_extracted_data(self):
        return self.__details

    def __get_basic_details(self):
        self.__extract_name()
        self.__extract_email()
        self.__extract_mobile_number()
        self.__extract_skills()
        self.__extract_education()
        self.__extract_experience()
        self.__extract_competencies()
        self.__extract_measurable_results()
        self.__extract_linkedin()

    def __extract_name(self):
        # Implement logic to extract name using NLP techniques
        # For example: Find entities tagged as PERSON in NER
        for ent in self.__nlp(self.__text_raw).ents:
            if ent.label_ == 'PERSON':
                self.__details['name'] = ent.text
                break

    def __extract_email(self):
        # Implement logic to extract email using regex
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
        matches = re.findall(email_pattern, self.__text_raw)
        if matches:
            self.__details['email'] = matches[0]

    def __extract_mobile_number(self):
        # Implement logic to extract mobile number using regex
        mobile_pattern = r"\b\d{10}\b"
        matches = re.findall(mobile_pattern, self.__text_raw)
        if matches:
            self.__details['mobile_number'] = matches[0]

    def __extract_skills(self):
     skills_section = re.search(r"SKILLS\n([\s\S]*?)(?=\n[A-Z ]+:|$)", self.__text_raw)
     if skills_section:
         skills_text = skills_section.group(1)
         keywords = ["Programming Languages", "Libraries"]
         extracted_skills = []
 
         for keyword in keywords:
             keyword_pattern = rf"{keyword}:\s*([\s\S]*?)(?=\n[A-Z ]+:|$)"
             keyword_matches = re.findall(keyword_pattern, skills_text, re.I)
             
             if keyword_matches:
                 extracted_skills.extend([skill.strip() for skill in keyword_matches[0].split(',')])
 
         self.__details['skills'] = extracted_skills



    def __extract_education(self):
        # Implement logic to extract education details using regex or NLP
        # For example: Look for keywords like 'education' and extract relevant sentences
        education_pattern = r"\b(education|qualification|degree)\b.*?((?<=\s)[A-Z][a-z]+(?=\s[A-Z]))"
        matches = re.findall(education_pattern, self.__text_raw, re.I)
        if matches:
            self.__details['education'] = [match[1] for match in matches]

    def __extract_experience(self):
        # Implement logic to extract experience details using regex or NLP
        # For example: Look for keywords like 'experience' and extract relevant sentences
        experience_pattern = r"\b(experience)\b.*?((?<=\s)[A-Z][a-z]+(?=\s[A-Z]))"
        matches = re.findall(experience_pattern, self.__text_raw, re.I)
        if matches:
            self.__details['experience'] = [match[1] for match in matches]

    def __extract_competencies(self):
        # Implement logic to extract competencies using NLP techniques
        # For example: Find verbs in the text
        self.__details['competencies'] = [token.text for token in self.__nlp(self.__text_raw) if token.pos_ == 'VERB']

    def __extract_measurable_results(self):
        # Implement logic to extract measurable results using NLP techniques
        # For example: Find sentences with numbers
        measurable_results_pattern = r"\b\d+\b.*?((?<=\d)\s+\w+)"
        matches = re.findall(measurable_results_pattern, self.__text_raw)
        if matches:
            self.__details['measurable_results'] = [match[0] for match in matches]

    def __extract_linkedin(self):
        # Extract LinkedIn profile URL using regex
        linkedin_url_pattern = r"(https?://[^\s]+linkedin\.com[^\s]+)"
        matches = re.findall(linkedin_url_pattern, self.__text_raw, re.I)
        if matches:
            self.__details['linkedin'] = matches[0]

def resume_result_wrapper(resume):
    parser = CustomResumeParser(resume)
    return parser.get_extracted_data()

if __name__ == '__main__':
    pool = mp.Pool(mp.cpu_count())

    resumes = []
    data = []
    for root, directories, filenames in os.walk('resumes'):
        for filename in filenames:
            file = os.path.join(root, filename)
            resumes.append(file)

    results = [pool.apply_async(resume_result_wrapper, args=(x,)) for x in resumes]

    results = [p.get() for p in results]

    pprint.pprint(results)
