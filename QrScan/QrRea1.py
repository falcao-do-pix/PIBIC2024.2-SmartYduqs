import cv2
import datetime
# initalize the cam
cap = cv2.VideoCapture("http://192.168.137.160:81/stream")
# initialize the cv2 QRCode detector
detector = cv2.QRCodeDetector()
while True:
    _, img = cap.read()
    # detect and decode
    data, bbox, _ = detector.detectAndDecode(img)
    # check if there is a QRCode in the image
    if data:
        a=data
        break
    # display the result
    cv2.imshow("QRCODEscanner", img)    

    if cv2.waitKey(1) == ord("q"):
        break
print(a)
now = datetime.datetime.now()
print(now.strftime("%Y-%m-%d %H:%M:%S"))
cap.release()
cv2.destroyAllWindows()