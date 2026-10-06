import cv2
import numpy as np

def nothing(x):
    pass
cv2.namedWindow('Trackbars')
cv2.createTrackbar('H_min', 'Trackbars', 0, 255, nothing)
cv2.createTrackbar('H_max', 'Trackbars', 255, 255, nothing)
cv2.createTrackbar('S_min', 'Trackbars', 0, 255, nothing)
cv2.createTrackbar('S_max', 'Trackbars', 255, 255, nothing)
cv2.createTrackbar('V_min', 'Trackbars', 0, 255, nothing)
cv2.createTrackbar('V_max', 'Trackbars', 255, 255, nothing)

def find_armor(frame):
    """
    输入：原始图像
    输出：画好框的图像，以及检测到的装甲板列表
    """

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    h_min = cv2.getTrackbarPos('H_min', 'Trackbars')
    h_max = cv2.getTrackbarPos('H_max', 'Trackbars')
    s_min = cv2.getTrackbarPos('S_min', 'Trackbars')
    s_max = cv2.getTrackbarPos('S_max', 'Trackbars')
    v_min = cv2.getTrackbarPos('V_min', 'Trackbars')
    v_max = cv2.getTrackbarPos('V_max', 'Trackbars')

    lower = np.array([h_min, s_min, v_min])
    upper = np.array([h_max, s_max, v_max])

    mask = cv2.inRange(hsv, lower, upper)

    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=1)
    mask = cv2.erode(mask, kernel, iterations=1)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #找灯条
    light_bars = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 50: 
            continue
            
        rect = cv2.minAreaRect(cnt)
        (x, y), (w, h), angle = rect
        
        if w > h:
            w, h = h, w
            angle += 90
            

        aspect_ratio = h / w
        if aspect_ratio < 2.5 or aspect_ratio > 10:
            continue
        if abs(angle) > 45:
            continue
            
        light_bars.append({'rect': rect, 'center': (int(x), int(y)), 'size': (w, h), 'angle': angle})
    #将前面找到的灯条挑出来，计算灯条的大小然后框出框来
    armors = []
    if len(light_bars) >= 2:
        light_bars.sort(key=lambda b: b['center'][0])
        
        used = [False] * len(light_bars)
        for i in range(len(light_bars) - 1):
            if used[i]: continue
            for j in range(i + 1, len(light_bars)):
                if used[j]: continue
                
                bar1 = light_bars[i]
                bar2 = light_bars[j]
                
                if abs(bar1['center'][1] - bar2['center'][1]) < 30: 
                    if abs(bar1['angle'] - bar2['angle']) < 15:
                        x1 = min(bar1['center'][0], bar2['center'][0])
                        x2 = max(bar1['center'][0], bar2['center'][0])
                        y1 = min(bar1['center'][1], bar2['center'][1])
                        y2 = max(bar1['center'][1], bar2['center'][1])
                        
                        pad = 15
                        armors.append((x1 - pad, y1 - pad, x2 + pad, y2 + pad))
                        used[i] = True
                        used[j] = True
                        break

    for (x1, y1, x2, y2) in armors:
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        cv2.putText(frame, "blue1", (x1, y1 - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        #把框标出来是blue

    return frame, mask

def main():
    cap = cv2.VideoCapture('/home/chenlin/自瞄任务素材包/demo.avi') 
    
    if not cap.isOpened():
        print("无法打开摄像头")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        result_frame, mask = find_armor(frame)

        cv2.imshow("imshow", result_frame)
        #将框好的框显示出来
        
        cv2.imshow("Mask (Debug)", mask) 
       

        key = cv2.waitKey(100)
        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()