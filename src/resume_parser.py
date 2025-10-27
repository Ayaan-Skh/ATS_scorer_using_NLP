from PyPDF2 import PdfReader

class PdfParser():
    def __init__(self):
        pass
    
    def Resume_parse(self,file_path:str)->str:
        reader=PdfReader(file_path)
        text=[]
        for i in range(len(reader.pages)):
            page=reader.pages[i]
            text.append(page.extract_text())
        return " ".join(text)
    