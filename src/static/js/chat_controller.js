document.addEventListener('DOMContentLoaded', () => {
    const sendMessageBtn = document.getElementById('sendMessageBtn');
    const userInput = document.getElementById('userInput');
    const fileInput = document.getElementById('InputFile'); // Asegúrate de que el ID coincida
    const fileNameSpan = document.getElementById('fileName'); // Span para mostrar el nombre del archivo
    const chatBox = document.getElementById('chatBox');
    const loadingIndicator = document.getElementById('loadingIndicator'); // Agrega un indicador de carga

    fileInput.addEventListener('change', () => {
        const file = fileInput.files[0];
        if (file) {
            fileNameSpan.textContent = file.name; // Mostrar el nombre del archivo cargado
            fileInput.style.backgroundColor = '#08c23c'; // Cambiar color de fondo
        } else {
            fileNameSpan.textContent = 'Ningún archivo seleccionado'; // Mensaje predeterminado
            fileInput.style.backgroundColor = ''; // Restaurar color de fondo
        }
    });

    sendMessageBtn.addEventListener('click', () => {
        const message = userInput.value.trim();
        const file = fileInput.files[0];

        if (!message) {
            alert('El mensaje no puede estar vacío.');
            return;
        }

        // Mostrar indicador de carga
        loadingIndicator.style.display = 'block';

        const formData = new FormData();
        formData.append('message', message);

        if (file) {
            formData.append('file', file);
        }

        chatBox.innerHTML = '';
        fetch('/chat', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Ocultar indicador de carga
            loadingIndicator.style.display = 'none';
            
            const newMessage = document.createElement('div');
            newMessage.textContent = data.resp || data.error;
            chatBox.appendChild(newMessage);
            userInput.value = ''; // Limpiar el campo de entrada después del envío

            
        })
        .catch(error => {
            // Ocultar indicador de carga
            loadingIndicator.style.display = 'none';

            console.error('Error:', error);
            const errorMessage = document.createElement('div');
            errorMessage.textContent = 'Ocurrió un error al enviar el mensaje.';
            chatBox.appendChild(errorMessage);
        });
    });
});
