
import cv2
from app.camara.camara import iniciar_camara, obtener_frame
from app.detection.detector_rostro import procesar_frame
from app.database.database import inicializar_bd


def main():
    # Inicializar la base de datos
    inicializar_bd()

    # Iniciar la cámara
    cap = iniciar_camara()
    if cap is None:
        return

    while True:
        frame = obtener_frame(cap)
        if frame is None:
            break

        # Aquí se procesaría el frame con el detector de rostro
        frame_procesado, face_encoding, mensaje = procesar_frame(frame)

        print(mensaje)

        # Mostrar el frame procesado
        cv2.imshow('Cámara', frame_procesado)

        # Salir con la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Liberar la cámara y cerrar las ventanas
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()