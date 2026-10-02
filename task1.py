import cv2
cap = cv2.VideoCapture('demo.avi')
if not cap.isOpened():
    print("无法打开视频，请检查文件路径和名称")
    exit()
while True:
    ret, frame = cap.read()
    if not ret:
        print("视频播放完毕")
        break
    cv2.imshow('Task 1 - Video Playback',frame)
    if cv2.waitKey(60) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()