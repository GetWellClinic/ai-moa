from oscar_automation import OscarAutomation

def main():
    oscar = OscarAutomation()
    oscar.process_documents()
    oscar.process_pdfs()
    oscar.process_workflow()

if __name__ == "__main__":
    main()
