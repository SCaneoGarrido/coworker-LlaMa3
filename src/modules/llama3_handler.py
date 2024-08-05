# ------------------------ IMPORTACION DE LIBRERIAS ------------------------ #
import subprocess
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# ------------------------ CLASE MANEJO DE LLAMA ------------------------ #
class Llama3Handler:
    # ------------------------ CONSTRUCTOR ------------------------ #
    def __init__(self) -> None:
        self.command = 'ollama run llama3'
        self.model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        self.index = faiss.IndexFlatL2(384) 

    # ------------------------ FUNCION VECTORIZACION DE TEXTO ------------------------ #
    def vectorize_text(self, text):
        return self.model.encode(text)  
   
    # ------------------------ AÑADIR EL TEXTO A UN INDICE ------------------------ #
    def add_text_to_index(self, text_id, text):
        vector = self.vectorize_text(text)
        self.index.add(np.array([vector]))
    
    # ------------------------ BUSCAR EN INDEX ------------------------ #
    def search_in_index(self, query):
        vector = self.vectorize_text(query)
        distances, indices = self.index.search(np.array([vector]), k=5)
        return indices
    
    # ------------------------ CHAT CON LLAMA 3 ------------------------ #
    def just_chat_with_llama(self, msg):
        prompt = f"""
            Porfavor responde al usuario el mensaje que ha enviado '{msg}'.
            Recuerda siempre consultar si necesita ayuda en alguna tareas
            (responde el idioma en el que este el mensaje)
        """
        try:
            result = subprocess.run(self.command, input=prompt, text=True, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
            output = result.stdout.strip()
            return output
        except subprocess.CalledProcessError as e:
            print(f"Error al ejecutar el comando: {e}")
            print(f"Salida de error: {e.stderr}")
            return ""
        
    # ------------------------ CHAT EN BASE A UN ARCHIVO ------------------------ #
    def chat_with_file(self, msg, docx_text):
        with open(docx_text, 'r', encoding='utf-8') as file:
            text_docx = file.read()
        
        # ------------------------ AGREGAR TEXTO AL INDICE FAISS ------------------------ #
        self.add_text_to_index("file_text", text_docx)

        # ------------------------ BUSCA INFO EN EL INDICE ------------------------ #
        indices = self.search_in_index(msg)

        # ------------------------ RECUPERAR EL TEXTO DE LOS INDICES ------------------------ #
        relevant_text = text_docx

        prompt = f"""
            Responde al mensaje del usuario '{msg}' basándote en la información contenida en el archivo proporcionado: '{text_docx}'
            (Responde en el idioma que llega el mensaje).
        """

        try:
            result = subprocess.run(self.command, input=prompt, text=True, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
            output = result.stdout.strip()
            return output
        except subprocess.CalledProcessError as e:
            print(f"Error al ejecutar el comando: {e}")
            print(f"Salida de error: {e.stderr}")
            return ""

