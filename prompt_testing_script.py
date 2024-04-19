import requests
import os
from doctr.io import DocumentFile
from doctr.models import ocr_predictor

def getTypePrompt():
    promopt = """For the following question, respond in one word, only one word if confidence level is more than 85%, else reply ‘Others’. From the list, choose one that suits the type of the EMR document. Here are your options, respond with only one of terms and no other words: Lab, Consult, Insurance, Legal, Old Chart, Radiology, Photo, Consent, Pathology, Diagnostics, Pharmacy, Requisition, HCC Referrals. See descriptions of these terms below; these descriptions should be only used to help you to identify the correct term, and not to be used to display in the output.


Lab: This refers to documents related to laboratory tests and results related to blood.
Consult: This refers to documents related to professional medical advice or consultations; this would include any response to a referral, to another doctor, and ED Consultations. Consult also includes pathology done by a dermatologist who has seen the patient. ED Consultations and ED Reports are also considered as a consult.
Insurance: This refers to documents related to patient insurance information, including request for medical records such as specifically clinical notes, consultation reports, and test results, for the purpose of assessing a disability claim, policy details, coverage, claims, and billing.
Legal: This refers to documents that requests to transfer copy/original of patients medical records to specific healthcare providers.
Old Chart: This refers to documents that includes patients previous medical reports or records, patients previous consulation records, patients previous lab reports.
Radiology: This refers to documents solely regarding radiology reports from a radiologist.
Photo: This refers to photographs related to the patient’s condition.
Consent: This refers to documents that request permission to view/access patients medical records from specific healthcare providers; this does not include the requests to transfer copy/original of the patients medical records to specific healthcare providers.
Pathology: This refers to documents related to detail findings from tissue or fluid sample analyses and examination of cells obtained from body fluids, aspirates, or tissue scrapings to diagnose diseases, particularly cancerous and precancerous conditions, also laboratory tests conducted on various specimens to identify microorganisms and determine appropriate treatment strategies for infectious diseases and mircobiology reports. This only applies if the document is from a medical laboratory or a pathologist.
Diagnostics: This refers to documents related to diagnostic reports or results including  laboratory test commonly used to assess heart rhythm and electrical activity in patients.
Pharmacy: This refers to documents sent from a pharmacist solely regarding medication renewals, as well as questions from a pharmacist at a pharmacy to a doctor. This does not include consultations from other physicians that also discuss medications as part of a consultation by a physician; these are consultations.
Requisition: This refers to documents that mentions challenges like misplaced medical records, missing test results, unavailability of supplies or equipment, communication breakdowns, insurance authorization issues, and technical difficulties with electronic health record; this also includes requests to resend any of the EMR records may arise due to issues such as misplaced medical records, missing test results, and communication breakdowns related to patients.
HCC Referrals: This refers to documents for incoming referrals to family physicians at that clinic from health care connect.
Please choose the most appropriate type for your document."""
    return promopt

def getDoctorNamePrompt():
    #promopt = """Answer only to the following question in one word.What is the lastname of the Doctor? Give the response in a json format, if there are more than one doctor mentioned, list all the first names as a json array."""
    promopt = """ instructions: Your task is to identify the lastname of the patients physician to whom this report is addressed; this is the family physician of the patient. Return these names in a JSON array. The rules are as follows:,
  rules: 1.Patient first names or patient last names are never part of the output.,2.If the lastname of the patient's family physician to whom this document is addressed is available and the confidence level is more than 85%, return a JSON array with one element - the lastname of the patient's family physician. The response will always be a single JSON array without any additional text or explanation.,3.If the confidence level is less than 85% return an empty JSON array., 4.Do not include any other information or assumptions from the document in the response., 5.The response should not contain any sentences or explanations, only a JSON array., 6.Any hypothetical scenarios or conditional statements should not be included in the response.""" 
    return promopt

def getPrompt():
    promopt = """Act as if you are a medical office assistant who follows direction precisly and consistantly when identifying a document. Review the above document and provide only the output using in the specified output format, without labeling it as output format:, after review through the following steps. 1. Select one category from  CATEGORY LIST provided below. If the provided category list does not provide a strong match display the word 'Other'. Output format template: 'category (Name of the pharmacy)'. Ensure this output format template is followed precisly including brackets (), and the output must end without a period. For reference this is an example using this output template 'Rx Refill (Shoppers), Rx Clarification (New Canyon Pharmacy), Rx Summary (MedsCheck)'. CATEGORY LIST: Rx Refill, Rx Clarification, Rx Summary, Lab Test Results, Imaging Results, Consultation Notes, Allergy List, Immunization Records, Family History, Patient Demographics"""
    return promopt


def get_pdf_files(folder_path):
    pdf_files = []
    for file in os.listdir(folder_path):
        if file.endswith(".pdf"):
            pdf_files.append(file)
    return pdf_files
    #return ["Sample-C6-003.pdf"]

def getText(pdf_file):
    model = ocr_predictor(det_arch='db_resnet50', pretrained=True)
    # PDF
    doc = DocumentFile.from_pdf(pdf_file)
    # Analyze
    result = model(doc)
    text = ''
    # Iterate through pages
    for page in result.pages:
        #print(f"Page {page.page_idx}:")
        
        # Iterate through blocks
        for block in page.blocks:
            #print("Block:")
            
            # Iterate through lines
            for line in block.lines:
                text += '\n'
                
                # Print words in the line
                for word in line.words:
                    text += word.value + ' '

    return text
                

def getDescription(text):
    url = "http://127.0.0.1:5000/v1/chat/completions"
    headers = {
        "Authorization": "Bearer qwerty",
        "Content-Type": "application/json"
    }
    data = {
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant designed to output JSON."
            },
            {
                "role": "user",
                "content": text
            }
        ],
            "mode": "instruct",
            "temperature": 0.3,
            "character": "Assistant",
            "top_p":.5
            #"frequency_penalty":-2,
            #"Presence_penalty":-2,
            #"repatition_penalty":1,
            #"max_tokens":21
    }

    response = requests.post(url, headers=headers, json=data)
    content_value = response.json()['choices'][0]['message']['content']
    print(content_value)
    append_to_file(file_path, content_value)

def append_to_file(file_path, content):
    with open(file_path, "a") as file:
        file.write(content + "\n")


folder_path = "/home/justinjoseph/Documents/AI-MOA/C5 - Pharmacy/"
print(folder_path)
pdf_files = get_pdf_files(folder_path)

print("PDF files in", folder_path, "are:")
response = "yes"
file_path = "C5 - Pharmacy.txt"
#append_to_file(file_path, getPrompt())

for pdf_file in pdf_files:
    if response in ('yes', 'y'):
        print(pdf_file)
        append_to_file(file_path, pdf_file)
        path = folder_path + pdf_file
        text = getText(path)
        fileType = text + getTypePrompt()
        getDescription(fileType)
        doctorName = text + getDoctorNamePrompt()
        #getDescription(doctorName)
        description = text + getPrompt()
        getDescription(description)
        #response = input("Do you want to continue execution? (yes/no): ").strip().lower()
