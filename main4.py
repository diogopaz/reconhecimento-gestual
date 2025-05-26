import cv2
import mediapipe as mp

# Inicializa o MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Inicializa a webcam
cap = cv2.VideoCapture(0)

def count_fingers(hand_landmarks, handedness_str):
    """Conta os dedos levantados com lógica ajustada e considerando a lateralidade."""
    finger_tips_ids = [4, 8, 12, 16, 20]  # Pontas dos dedos (polegar, indicador, médio, anelar, mínimo)
    finger_pip_ids = [2, 6, 10, 14, 18]   # Juntas Proximais Interfalangeanas (PIP) - segunda junta a partir da ponta
    thumb_mcp_id = 2 # Junta Metacarpofalangeana (MCP) do polegar

    fingers = []

    # Lógica para o Polegar
    thumb_tip = hand_landmarks.landmark[finger_tips_ids[0]]
    thumb_pip = hand_landmarks.landmark[finger_tips_ids[0] - 1] # Junta PIP do polegar
    thumb_mcp = hand_landmarks.landmark[thumb_mcp_id]

    # Verifica se o polegar está estendido (ponta mais "para fora" que a junta PIP)
    # E se a ponta está acima da junta MCP (para cima)
    if handedness_str == 'Right': # Mão Direita (imagem espelhada)
        # Polegar para a "esquerda" da sua junta PIP e ponta acima da junta MCP
        if thumb_tip.x < thumb_pip.x and thumb_tip.y < thumb_mcp.y :
            fingers.append(1)
        else:
            fingers.append(0)
    elif handedness_str == 'Left': # Mão Esquerda
        # Polegar para a "direita" da sua junta PIP e ponta acima da junta MCP
        if thumb_tip.x > thumb_pip.x and thumb_tip.y < thumb_mcp.y:
            fingers.append(1)
        else:
            fingers.append(0)
    else: # Caso a lateralidade não seja detectada de forma confiável
        # Lógica mais genérica (pode ser menos precisa para o polegar)
        # Polegar para cima (ponta acima da junta PIP e da junta MCP)
        if thumb_tip.y < thumb_pip.y and thumb_tip.y < hand_landmarks.landmark[finger_tips_ids[0]-2].y : # landmark[2] é a base do polegar
            fingers.append(1)
        else:
            fingers.append(0)

    # Lógica para os outros quatro dedos
    for id in range(1, 5): # Dedos: Indicador, Médio, Anelar, Mínimo
        tip_y = hand_landmarks.landmark[finger_tips_ids[id]].y
        pip_y = hand_landmarks.landmark[finger_pip_ids[id]].y
        mcp_y = hand_landmarks.landmark[finger_pip_ids[id]-1].y # Junta MCP do dedo correspondente

        # Para ser considerado levantado, a ponta deve estar significativamente acima da junta PIP,
        # e a junta PIP deve estar acima da junta MCP.
        if tip_y < pip_y and pip_y < mcp_y:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers.count(1)

def is_thumbs_up(hand_landmarks, handedness_str):
    """Verifica se o gesto de "joia" (polegar para cima) está sendo feito."""
    finger_tips_ids = [4, 8, 12, 16, 20]
    finger_pip_ids = [2, 6, 10, 14, 18]
    thumb_mcp_id = 2

    # Lógica do Polegar para "Joia"
    thumb_tip = hand_landmarks.landmark[finger_tips_ids[0]]
    thumb_pip = hand_landmarks.landmark[finger_tips_ids[0] - 1]
    thumb_mcp = hand_landmarks.landmark[thumb_mcp_id]
    thumb_up = False

    if handedness_str == 'Right':
        if thumb_tip.x < thumb_pip.x and thumb_tip.y < thumb_mcp.y:
            thumb_up = True
    elif handedness_str == 'Left':
        if thumb_tip.x > thumb_pip.x and thumb_tip.y < thumb_mcp.y:
            thumb_up = True
    else: # Genérico
         if thumb_tip.y < thumb_pip.y and thumb_tip.y < hand_landmarks.landmark[finger_tips_ids[0]-2].y:
            thumb_up = True

    # Outros dedos para baixo ou curvados (ponta abaixo ou no mesmo nível da junta PIP)
    other_fingers_down = True
    for id in range(1, 5):
        tip_y = hand_landmarks.landmark[finger_tips_ids[id]].y
        pip_y = hand_landmarks.landmark[finger_pip_ids[id]].y
        # Se a ponta de qualquer outro dedo estiver acima da sua junta PIP, não é "joia"
        if tip_y < pip_y:
            other_fingers_down = False
            break
    return thumb_up and other_fingers_down

while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("Não foi possível capturar a imagem da webcam.")
        continue

    # Inverte a imagem horizontalmente para visualização tipo espelho
    image = cv2.flip(image, 1)
    # Converte a imagem de BGR para RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Processa a imagem para detectar mãos
    results = hands.process(image_rgb)

    finger_count = 0
    gesture = ""
    handedness_text = "N/A" # Para exibir qual mão foi detectada

    # Desenha as anotações da mão na imagem
    if results.multi_hand_landmarks:
        # Itera sobre cada mão detectada (configurado para max_num_hands=1, então deve ser apenas uma)
        for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            mp_drawing.draw_landmarks(
                image, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=4), # Estilo dos landmarks
                mp_drawing.DrawingSpec(color=(250, 44, 250), thickness=2, circle_radius=2)  # Estilo das conexões
            )

            # Obter a lateralidade da mão (Esquerda ou Direita)
            handedness_str = ""
            if results.multi_handedness:
                try:
                    # Acessa o handedness correspondente à mão detectada
                    handedness = results.multi_handedness[hand_idx]
                    handedness_str = handedness.classification[0].label # 'Left' ou 'Right'
                    handedness_text = handedness_str
                except IndexError:
                    handedness_text = "N/A" # Caso não consiga determinar

            # Conta os dedos
            finger_count = count_fingers(hand_landmarks, handedness_str)

            # Verifica o gesto de "joia"
            if is_thumbs_up(hand_landmarks, handedness_str):
                gesture = "Joia!"
            else:
                gesture = "" # Limpa o gesto se não for "joia"

    # Exibe a contagem de dedos, o gesto e a lateralidade da mão
    cv2.putText(image, f'Dedos: {finger_count}', (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3, cv2.LINE_AA)
    if gesture:
        cv2.putText(image, gesture, (30, 110), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3, cv2.LINE_AA)
    cv2.putText(image, f'Mao: {handedness_text}', (30, 170), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

    # Mostra a imagem
    cv2.imshow('Reconhecimento de Gestos - IA', image)

    # Pressione 'q' para sair
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

# Libera os recursos
cap.release()
cv2.destroyAllWindows()
hands.close()