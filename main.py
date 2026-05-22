import cv2

cap = cv2.VideoCapture(0)

window_name = 'Wifi-With-Camera'
cv2.namedWindow(window_name)

fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    mirrored_frame = cv2.flip(frame, 1)
    out.write(mirrored_frame)
    cv2.imshow(window_name, mirrored_frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
        
    if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
        break

cap.release()
out.release()
cv2.destroyAllWindows()

