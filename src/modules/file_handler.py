# ------------------------ IMPORTACION DE LIBRERIAS ------------------------ #
import os
from docx import Document
from PyPDF2 import PdfReader

# ------------------------ FILEHANDLER ------------------------ #
class FileHandler:
    # ------------------------ CONSTRUCTOR ------------------------ #
    def __init__(self) -> None:
        self.files_folder = 'FILES_FOLDER'
        if not os.path.exists(self.files_folder):
            os.makedirs(self.files_folder)
    
    # ------------------------ EXTRAE EL TEXTO DEL PDF ------------------------ #
    def extract_text_from_pdf(self, pdf_path):
        text = ""
        output_file_path = os.path.join(self.files_folder, 'output.txt')
        
        try:
            with open(pdf_path, 'rb') as file:
                reader = PdfReader(file)
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    text += page.extract_text() if page.extract_text() else ""
        except Exception as e:
            print(f"Error en la función 'extract_text_from_pdf()' \nClase: 'FileHandler'\n Error->{e}")

        try:
            with open(output_file_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write(text)
        except Exception as e:
            print(f"Error al guardar el archivo {output_file_path}: {e}")

        return output_file_path

    def extraer_texto_docx(self, ruta_docx):
        # Cargar el archivo DOCX
        doc = Document(ruta_docx)
        
        # Extraer texto del archivo DOCX
        texto = ""
        for parrafo in doc.paragraphs:
            texto += parrafo.text + "\n"
        
        # Definir la ruta del archivo TXT en la misma carpeta
        nombre_archivo = os.path.basename(ruta_docx)
        nombre_archivo_sin_ext = os.path.splitext(nombre_archivo)[0]
        ruta_txt = os.path.join(self.files_folder, nombre_archivo_sin_ext + '.txt')
        
        # Escribir el texto extraído en el archivo TXT
        try:
            with open(ruta_txt, 'w', encoding='utf-8') as archivo_txt:
                archivo_txt.write(texto)
        except Exception as e:
            print(f"Error al guardar el archivo {ruta_txt}: {e}")

        # Retornar la ruta del archivo TXT
        return ruta_txt