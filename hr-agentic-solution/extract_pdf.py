import PyPDF2

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text

if __name__ == "__main__":
    pdf_path = "/usr/local/google/home/anujshaunj/hr-agentic-solution/hr-agentic-solution/handbook.pdf"
    text = extract_text_from_pdf(pdf_path)
    with open("/usr/local/google/home/anujshaunj/hr-agentic-solution/hr-agentic-solution/handbook.txt", "w") as f:
        f.write(text)
    print("Extracted text successfully")
