import cv2
import mediapipe as mp
import random
import math
import time
import numpy

#MediaPipe初期化
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

#カメラ起動
cap = cv2.VideoCapture(0)

with mp_pose.Pose(
    min_detection_confidence=0.5, min_tracking_confidence=0.5
) as pose:
    while cap.isOpened():
        ret, frame = cap.read() #ret=return
        if not ret:
            break
        
        #MediaPipe処理
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        results = pose.process(rgb)
        rgb = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

        #ランドマーク描画
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                frame,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS
        )
        
        #画面表示
        cv2.imshow("Game", frame)

        #q end
        if cv2.waitKey(5) & 0xFF == ord('q'): #ord= str->int
            break

cap.release()
cv2.destroyAllWindows()