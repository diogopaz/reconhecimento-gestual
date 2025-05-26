## Reconhecimento de Gestos com MediaPipe

Este projeto utiliza Python, OpenCV e MediaPipe para reconhecer números de 1 a 5 com a mão voltada para a câmera e detectar o gesto de "joia". Além disso, identifica se a mão é esquerda ou direita.

### Funcionalidades

    Contagem de Dedos: Reconhece o número de dedos levantados (1 a 5).
    Gesto de Joia: Detecta quando o polegar está levantado e os outros dedos estão abaixados.
    Identificação da Mão: Reconhece se a mão é esquerda ou direita.

### Requisitos

    Python 3.x
    OpenCV
    MediaPipe

### Instalação

Certifique-se de ter o Python e pip instalados em seu sistema.

    Clone ou baixe este repositório.
    Instale as dependências usando o pip:
    ```bash
    pip install opencv-python mediapipe
    ```
Uso

Execute o script gesture_recognition.py para iniciar o reconhecimento de gestos:
```bash
python gesture_recognition.py
```
    Mantenha a mão aberta e voltada para a câmera para que os dedos sejam reconhecidos.
    Experimente fazer o gesto de "joia" para testar a detecção.
    Pressione 'q' para encerrar o programa.
