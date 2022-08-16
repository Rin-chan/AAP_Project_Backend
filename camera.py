import cv2
import time


camera = cv2.VideoCapture(0)

def gen_frames():  
    global camera
    camera = cv2.VideoCapture(0)

    while True:
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

def capturePhoto():
    success, frame = camera.read()
    if success:
        filename = "frame"+time.strftime("%Y%m%d-%H%M%S")+'.jpg'
        filepath = 'static/img/'+filename
        cv2.imwrite(filepath, img=frame)
        camera.release()

        return filename
    else: 
        camera.release()
        print('not successful')

def closeCamera():
    if cv2.VideoCapture(0).isOpened():
        camera.release()
    
