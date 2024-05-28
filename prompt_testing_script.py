import requests
import os
import torch
import time
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

def getPrompt(text):
    promopt = [""] * 16
    promopt[0] = "These rules always apply; patient first names or patient last names are never part of output; output ends without period '.'; Act as if you are a medical office assistant who follows direction precisely and consistantly when identifying a document. Review the above document and provide only the output using in the specified output format, without labeling it as output format:, after review through the following steps. 1. Select one category from the list (Bloodwork, Immunology, Endocrinology) that suits the above document. 2. Identify the lab OR hospital name that performed the tests in the lab report; use the english name if there is both english and french; if uncertain look for a laboratry name. 3. Select one sub-type only from this list; you will use this choice for the sub-type in the output format template: TSH, h. pylori, LMC, hepatitis, other. Output format template: 'Consultation type (lab OR hospital name) sub-type'. Ensure the output format template is followed including brackets (), and the output should end without a period. For reference this is an example using this output template 'Bloodwork (Public Health) hepatitis'."
    promopt[1] = """These rules always apply; patient first names or patient last names are never part of output; output ends without period ‘.’; Act as if you are a medical office assistant who follows direction precisely and consistently when identifying a document. Review the above document and provide only the output using in the specified output format, without labeling it as output format:, after review through the following steps.

If this document has a strong match in category as a Geriatric Nurse Report, HealthLinks Coordinated Care Plan, or ‘Discharge summary’, select from that list for the category. ‘ED summary’ should be used for all discharge summaries from an emergency department. If no strong match for the category, select one category as the consultation type from the SPECIALITY LIST FOR REFERENCE provided at the end of these instructions if there is a strong match based on the document content or select the category other.
Identify the name of the consultant or attending physician who wrote this document. Always include the prefix ‘Dr.’ before the physician’s name; Always use the format: Dr. Firstname Lastname.
Identify the hospital/lab that this consultation report is sent from if any; never directly reference the patient by any type of name.
Without using the first name or last name of the patients, identify the sub-type or general nature of this specialty report and prepare a description in less than 5 words for the above document. Never directly reference the patient by any type of name. If document category is ‘ED summary’ this sub-type nature of the specialty report should be described as injury or illness in 5 words or less; Never directly reference the patient by any type of name in this description.
Output format template: ‘Consultation type (consultant physician OR lab OR hospital name) sub-type or general nature’. If the report is from a hospital or lab or of the category ‘Discharge summary’, provide the hospital or lab name and do not include the physician’s name. Do not mention the words ‘Consultation type’ or ‘report’ or ‘note’ or ‘sub-type’ in the response! Only choose ‘Geriatrics’ if the consultation indicates this is from a Geriatrics specialist; this does not include ED Consultations; Do not use ‘Geriatrics’ as a specialty just because the patient is old or the issues are age related it must be only used if the physician sending the report is a  Geriatrician. Ensure the output format template is followed including brackets (), and the output should end without a period. For reference this is an example using this output template ‘Immunology (Dr. Smith) Allergy Test’.

SPECIALITY LIST FOR REFERENCE: Cardiology, Gastroenterology, Respirology, Dermatology, Orthopedics, Neurology, Hematology, Endocrinology, Rheumatology, Nephrology, Pulmonology, Ophthalmology, Psychiatry, Gynecology, Urology, Oncology, Infectious Diseases, Allergy and Immunology, Geriatrics, Gastrointestinal Surgery, Plastic Surgery, Vascular Surgery, Obstetrics, Pediatrics, Physical Medicine and Rehabilitation, Hepatology, Hematopathology, Nuclear Medicine, Radiology, Pain Management, Genetics, Hepatobiliary Surgery, Colorectal Surgery, Thoracic Surgery, Otolaryngology (ENT), Hematologic Oncology, Geriatric Psychiatry, Gynecologic Oncology, Neonatology, Interventional Cardiology, Clinical Genetics, Pediatric Cardiology, Pediatric Endocrinology, Pediatric Gastroenterology, Pediatric Hematology-Oncology, Pediatric Nephrology, Pediatric Neurology, Pediatric Pulmonology, Pediatric Rheumatology, Pediatric Surgery, Pediatric Urology, General Surgery, Pediatric Respirology, Anesthesiology, Surgical Outpatient, Pain management."""
    promopt[2] = "Act as if you are a medical office assistant who follows direction precisly and consistantly when identifying a document. Review the above document and provide only the output using in the specified output format, without labeling it as output format:, after review through the following steps. 1. Identify the organization who wrote this document. 2. Select one category from  CATEGORY LIST provided below. If the provided category list does not provide a strong match display the word 'Other'. Output format template: 'category (Insurance company name)'. Ensure this output format template is followed precisly including brackets (), and the output must end without a period. For reference this is an example using this output template 'Request - medical records (Lifeworks)'. CATEGORY LIST: Prior Authorization, Request - medical records, Other"
    promopt[3] = "Act as if you are a medical office assistant who follows direction precisly and consistantly when identifying a document. Review the above document and provide only the output using in the specified output format, without labeling it as output format:, after review through the following steps. 1. Identify the organization who wrote this document. 2. Select one category from  CATEGORY LIST provided below. If the provided category list does not provide a strong match display the word 'Other'. Output format template: 'category (Name of the firm/company/ the person who requested the document/the date of request if its requestd by a patient)'. Ensure this output format template is followed precisly including brackets (), and the output must end without a period. For reference this is an example using this output template 'Request Records (Sharma Law Firm),Attending physician’s statement (Spector Lit Law Firm), Request Record by patient (04 April 2021) '. CATEGORY LIST: Prior Authorization, Attending physician’s statement, Request Records, Request Record by patient"
    promopt[4] = "Act as if you are a medical office assistant who follows direction precisly and consistantly when identifying a document. Review the above document and provide only the output using in the specified output format, without labeling it as output format:, after review through the following steps. 1. Select one category from  CATEGORY LIST provided below. If the provided category list does not provide a strong match display the word 'Other'. Output format template: 'category (Name of the Doctor/Hospital/Clinic)'. Ensure this output format template is followed precisly including brackets (), and the output must end without a period. For reference this is an example using this output template 'Immunization record (Get well clinic), Old Medical Records (NYGH), Medical Records (Dr. Smith – Magenta Health), Rx history'. CATEGORY LIST: Immunization Record, Old Medical Records, Medical Records, Rx History, Surgical History, Family Medical History"
    promopt[5] = "Act as if you are a medical office assistant who follows direction precisly and consistently when identifying a document. Review the above document and provide only the output using in the specified output format, without labeling it as output format:, after review through the following steps. 1. Select one category from  CATEGORY LIST provided below. If the provided category list does not provide a strong match display the word 'Other'. 2. Compose a miximum three word summary of the type of content of the findings.  Output format template: 'category (Name of the facility) summary'. Ensure this output format template is followed precisely including brackets (), and the output must end without a period. For reference this is an example using this output template 'MRI Head (NYGH) Trauma, CT Chest (UHN) nodule, CXR (PDS), BMD (PDS), U/S abdo pelvis (PDS), Angiography (NYGH)'. CATEGORY LIST: MRI Head (NYGH) Trauma, CT Chest Nodule, CXR, BMD, U/S Abdo Pelvis, Angiography, Mammography, PET Scan, CT Angiogram, MRI Spine"
    promopt[6] = "Act as if you are a medical office assistant who follows direction precisly and consistantly when identifying a document. Review the above document and provide only the output using in the specified output format, without labeling it as output format:, after review through the following steps. 1. Select one category from  CATEGORY LIST provided below. If the provided category list does not provide a strong match display the word 'Other'. Output format template: 'category (Name of the hospital)'. Ensure this output format template is followed precisly including brackets (), and the output must end without a period. For reference this is an example using this output template 'Biopsy colon (HRH), Bone Marrow (Markham Stouffville), Gyn Cytopathology (NYGH). CATEGORY LIST: Biopsy Colon, Bone Marrow, Gyn Cytopathology, Blood Culture, Urinalysis, Complete Blood Count, Liver Function Test, Thyroid Function Test, Coagulation Profile, Tissue Culture"
    promopt[7] = "Act as if you are a medical office assistant who follows direction precisly and consistantly when identifying a document. Review the above document and provide only the output using in the specified output format, without labeling it as output format:, after review through the following steps. 1. Select one category from  CATEGORY LIST provided below. If the provided category list does not provide a strong match display the word 'Other'. Output format template: 'category (Name of Doctor/Hospital)'. Ensure this output format template is followed precisly including brackets (), and the output must end without a period. For reference this is an example using this output template 'Notification – Admission (TSH), Appt notification– OB (Dr.Cheng), Declined Appt – OB (Dr. Cha), Declined Appt from GWC – Psychotherapy (Dr. Copeland), Cancelled – Appt - OB (Dr. Cheng), Appt clarification - Physiatry (Dr. Unarket), Appt notification from GWC – WMP, ER visit (HRH), Unable to reach pt – Psychiatry (Dr. Chen)'. CATEGORY LIST: Notification – Admission, Appt Notification– OB, Declined Appt – OB, Declined Appt from GWC – Psychotherapy, Cancelled – Appt - OB, Appt Clarification - Physiatry, Appt Notification from GWC – WMP, ER Visit, Unable to Reach Pt – Psychiatry, PHQ-9, GAD-7, Patient Feedback, Patient Education Materials"
    promopt[8] = "Give a short description in less than 6 words for the above document which should include the type of the document, type of specimen and name of the hospital. It should be less than 6 words!"
    promopt[9] = "Act as if you are a medical office assistant who follows direction precisly and consistantly when identifying a document. Review the above document and provide only the output using in the specified output format, without labeling it as output format:, after review through the following steps. 1. Select one category from  CATEGORY LIST provided below. If the provided category list does not provide a strong match display the word 'Other'. Output format template: 'category'. Ensure this output format template is followed precisly including brackets (), and the output must end without a period. For reference this is an example using this output template 'Patient Registration and Consent, Consent to release records, Authorization for release to third party, Non-Resident governing law consent form, Medical record transfer Consent, Patient Enrolment Form'. CATEGORY LIST: Patient Registration and Consent, Consent to Release Records, Authorization for Release to Third Party, Non-Resident Governing Law Consent Form, Medical Record Transfer Consent, Patient Enrolment Form, Informed Consent for Treatment, Consent for Telemedicine Services, Consent for Minor's Treatment, Consent for Surgical Procedure"
    promopt[10] = "Act as if you are a medical office assistant who follows direction precisly and consistantly when identifying a document. Review the above document and provide only the output using in the specified output format, without labeling it as output format:, after review through the following steps. 1. Select one category from  CATEGORY LIST provided below. If the provided category list does not provide a strong match display the word 'Other'. Output format template: 'category (Name of the facility)'. Ensure this output format template is followed precisly including brackets (), and the output must end without a period. For reference this is an example using this output template 'ECG (Lifelabs), Stress Test (the Heart Clinic ), PFT (Polyclinic), Holter Monitor (KHM)'. CATEGORY LIST: ECG, Stress Test, PFT, Holter Monitor, EEG, Sleep Study, Audiogram, Vision Test, Spirometry, Treadmill Test,ECG, EKG,Echocardiogram,Stress Test,Holter Monitor,Cardiac CatheterizationCardiac MRI, CT Angiography"
    promopt[11] = "Act as if you are a medical office assistant who follows direction precisly and consistantly when identifying a document. Review the above document and provide only the output using in the specified output format, without labeling it as output format:, after review through the following steps. 1. Select one category from  CATEGORY LIST provided below. If the provided category list does not provide a strong match display the word 'Other'. Output format template: 'category (Name of the pharmacy)'. Ensure this output format template is followed precisly including brackets (), and the output must end without a period. For reference this is an example using this output template 'Rx Refill (Shoppers), Rx Clarification (New Canyon Pharmacy), Rx Summary (MedsCheck)'. CATEGORY LIST: Rx Refill, Rx Clarification, Rx Summary, Lab Test Results, Imaging Results, Consultation Notes, Allergy List, Immunization Records, Family History, Patient Demographics"
    promopt[12] = "Act as if you are a medical office assistant who follows direction precisly and consistantly when identifying a document. Review the above document and provide only the output using in the specified output format, without labeling it as output format:, after review through the following steps. 1. Select one category from  CATEGORY LIST provided below. If the provided category list does not provide a strong match display the word 'Other'. Output format template: 'category (Name of the doctor/specialist/practitioner/location/)'. Ensure this output format template is followed precisly including brackets (), and the output must end without a period. For reference this is an example using this output template 'Req Neurologist (Dr. Prigozhikh), Req Cardiology (BP Monitor; Downsview Clinic), Req Colonscopy York Diagnostic Centre, Referral (ENT) Polyclinic – hearing loss, Referral to GWC (Dr. Copeland)- psychotherapy, Referral to GWC (Weight Management Program)'. CATEGORY LIST: Req Neurologist, Req Cardiology, Req Colonscopy, Referral (ENT), Referral to GWC, Req Dermatology, Req Endocrinology, Req Pulmonology, Referral (Ophthalmology), Referral to Physiotherapy"
    promopt[13] = "Act as if you are a medical office assistant who follows direction precisly and consistantly when identifying a document. Review the above document and provide only the output using in the specified output format, without labeling it as output format:. Output format template: 'HCC referral to Dr.(Name of Doctor/physician) - name of patient'. Ensure this output format template is followed precisly including brackets () and -, and the output must end without a period. For reference this is an example using this output template 'HCC referral to Dr. (John, Smith) – DOE, Cullian Murphy"
    promopt[14] = "Act as if you are a medical office assistant who follows direction precisly and consistantly when identifying a document. Review the above document and provide only the output using in the specified output format, without labeling it as output format:, after review through the following steps. 1. Select one category from  CATEGORY LIST provided below. If the provided category list does not provide a strong match display the word 'Other'. Output format template: 'category (Name of the physician who requested the document/the clinic that requested the document/ the clinic to which the patient is being transfered to)'. Ensure this output format template is followed precisly including brackets (), and the output must end without a period. For reference this is an example using this output template 'Request for Medical(Get well clinic),Request for Medical(Dr. Smith)'. CATEGORY LIST: Request for Medical Records"
    promopt[15] = "Give a short description in less than 6 words for the above document which should include the details health care referal, referal doctors name . It should be less than 6 words!"
    categories = [
                    "Lab",
                    "Consult",
                    "Insurance",
                    "Legal",
                    "Old Chart",
                    "Radiology",
                    "Pathology",
                    "Others",
                    "Photo",
                    "Consent",
                    "Diagnostics",
                    "Pharmacy",
                    "Requisition",
                    "Referral",
                    "Request"
                ]
    if '.' in text:
        text = text.replace('.', '')
    for index, category in enumerate(categories):
        for word in text.split():
            if word.lower() == category.lower():
                #print(index)
                return promopt[index]
                


def get_pdf_files(folder_path):
    pdf_files = []
    files_to_remove = {

    }
    for file in os.listdir(folder_path):
        if file.endswith(".pdf") and file not in files_to_remove:
            pdf_files.append(file)
    return pdf_files
    # return ["Sample-C1-012.pdf"]

def getText(pdf_file):
    start_time = time.time()
    try:
        device = torch.device("cuda:0")
        model = ocr_predictor(pretrained=True).to(device)
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
        # print(text)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print("OCR Time taken for one file:", elapsed_time, "seconds")
        # print("ocr completed")
        return text
    except Exception as e:
        print("An error occurred:", e)

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
    return content_value

def append_to_file(file_path, content):
    with open(file_path, "a") as file:
        file.write(content + "\n")


folder_path = "/home/justinjoseph/Documents/AI-MOA/all_files/"
#print(folder_path)
pdf_files = get_pdf_files(folder_path)

#print("PDF files in", folder_path, "are:")
response = "yes"
file_path = "all_files_ocr_gpu.txt"
#append_to_file(file_path, getPrompt())

for pdf_file in pdf_files:
    start_time = time.time()
    if response in ('yes', 'y'):
        print(pdf_file)
        append_to_file(file_path, pdf_file)
        path = folder_path + pdf_file
        text = getText(path)
        #print(path)
        fileType = text + getTypePrompt()
        start_time_type = time.time()
        append_to_file(file_path, "File Type:")
        typeOfDOcument = getDescription(fileType)
        end_time_type = time.time()
        elapsed_time_type = end_time_type - start_time_type
        append_to_file(file_path, "Time taken for file type identification:")
        append_to_file(file_path,str(elapsed_time_type))
        print("Time taken for file type identification:", elapsed_time_type, "seconds")
        #doctorName = text + getDoctorNamePrompt()
        #getDescription(doctorName)
        if typeOfDOcument is None or text is None:
            print(typeOfDOcument)
            print(":::")
            print(text)
            print(":::")
            print(getPrompt(typeOfDOcument))
        description = text + getPrompt(typeOfDOcument)
        start_time_desc = time.time()
        append_to_file(file_path, "Description:")
        documentDescription = getDescription(description)
        end_time_desc = time.time()
        elapsed_time_desc = end_time_desc - start_time_desc
        print("Time taken for file description:", elapsed_time_desc, "seconds")
        append_to_file(file_path, "Time taken for file description:")
        append_to_file(file_path,str(elapsed_time_desc))
        #response = input("Do you want to continue execution? (yes/no): ").strip().lower()
    end_time = time.time()
    elapsed_time = end_time - start_time
    print("Time taken for the file:", elapsed_time, "seconds")
    append_to_file(file_path, "Time taken for the file:")
    append_to_file(file_path,str(elapsed_time))
