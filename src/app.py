# ------------------------------- IMPORTACIONES DE LIBRERIAS -------------------------- #
import os
import requests
from flask import Flask, render_template, jsonify, request
from werkzeug.utils import secure_filename
from modules.llama3_handler import Llama3Handler
from modules.file_handler import FileHandler
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS  # Importar la clase DDGS

# ------------------------------- CONFIGURACION DE DIRECTORIOS Y VARIABLES -------------- #
app = Flask(__name__, template_folder="templates", static_folder="static")
UPLOADS_FOLDER = 'UPLOADS_FOLDER'  # Variable de APP para crear la carpeta de uploads
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}  # Tipos de archivo permitidos
app.config['UPLOADS_FOLDER'] = UPLOADS_FOLDER

# ------------------------------- VARIABLES ------------------------------- #
chat_history = []

# -------------------------------- INICIALIZACION DE CLASES ------------------------------ #
FileManager_instace = FileHandler()
Llama3Controller_instance = Llama3Handler()

# ------------------------------- FUNCION AUXILIAR  ------------------------------- #
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_prompt_from_history(history):
    prompt = "Conversation history:\n"
    for entry in history:
        prompt += f"{entry['role']}: {entry['content']}\n"
    prompt += "Assistant, based on this history, please respond to the new user message."
    return prompt

def scrape_website(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Verifica que la solicitud fue exitosa
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Aquí puedes ajustar qué información quieres extraer. Este ejemplo obtiene todo el texto de las etiquetas <p>
        paragraphs = soup.find_all('p')
        content = '\n'.join([p.get_text() for p in paragraphs])
        
        return content
    except requests.RequestException as e:
        print(f"Ocurrió un error durante el scraping: {e}")
        return ""

def search_duckduckgo(query):
    """Realiza una búsqueda en DuckDuckGo y devuelve los resultados."""
    ddgs = DDGS()
    results = ddgs.text(query, max_results=3)  # Limitar a 3 resultados
    return results

# ----------------------------------- RENDERIZADOR DE HOME -------------------------------------------------------- #
@app.route("/")
def home():
    return render_template("index.html")

# ---------------------------------- RUTA PARA REALIZAR UN CHAT CON LLAMA3 ---------------------------------- #
@app.route('/chat', methods=['POST'])
def chatLlaMa3():
    if request.method == 'POST':
        file = request.files.get('file')
        message = request.form.get('message')
        url = request.form.get('url')  # Parámetro opcional para URL

        if not message:
            return jsonify({'error': 'El mensaje no puede estar vacío.'}), 400

        # Verificar y leer el archivo si existe
        if file:
            filename = secure_filename(file.filename)
            if allowed_file(filename):
                file_content = file.read()
                file.seek(0)  # Reiniciar el puntero del archivo para otras operaciones
                print(f"Nombre del archivo: {filename}")
                print(f"Tamaño del archivo: {len(file_content)} bytes")

                upload_folder = app.config['UPLOADS_FOLDER']
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                
                ruta_archivoDocx = os.path.join(upload_folder, filename)
                print(f"Ruta para guardar el archivo: {ruta_archivoDocx}")

                try:
                    file.save(ruta_archivoDocx)
                    print("Archivo guardado correctamente.")
                    
                    # Realizamos la consulta en base al archivo
                    txt_docx = FileManager_instace.extraer_texto_docx(ruta_archivoDocx)
                    if txt_docx is not None:
                        result_docx = Llama3Controller_instance.chat_with_file(message, txt_docx)
                        if result_docx != "":
                            return jsonify({'resp': result_docx})
                    else:
                        print("No se extrajo texto del archivo DOCX.")
                        
                except Exception as e:
                    print(f"Error al guardar o procesar el archivo: {e}")
                    return jsonify({'err': 'No se ha logrado realizar la petición'}), 500
            else:
                print(f"Archivo no permitido: {filename}")
                return jsonify({'error': 'Tipo de archivo no permitido.'}), 400
        else:
            print("No se recibió archivo.")

        print(f"Mensaje: {message}")

        # Realizar búsqueda si se proporciona un mensaje
        additional_context = ""
        if message:
            additional_context = search_duckduckgo(message)  # Realiza búsqueda en DuckDuckGo
            print(f"Resultados de DuckDuckGo: {additional_context}")

        # Agregar el mensaje del usuario al historial
        chat_history.append({'role': 'user', 'content': message})

        try:
            prompt = create_prompt_from_history(chat_history)
            prompt += f"\nInformación adicional: {additional_context}"
            result = Llama3Controller_instance.just_chat_with_llama(prompt)
            
            if result:
                # Agregar la respuesta del modelo al historial
                chat_history.append({'role': 'assistant', 'content': result})
                print(result)
                return jsonify({'resp': result})
        except Exception as e:
            print(f"Ocurrió un error durante la respuesta del modelo\n Error: {e}")
            return jsonify({'error': 'Ocurrió un error durante la solicitud'}), 500

        return jsonify({'msg': 'Data recibida'}), 200
    else:
        return jsonify({'error': 'Método No Permitido'}), 405

# ------------------------ EJECUCION DE APP -------------------------------------------- #
if __name__ == "__main__":
    app.run(debug=True)