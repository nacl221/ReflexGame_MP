import cv2
import mediapipe as mp
import random
import math
import time
import numpy

#MediaPipe初期化
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

def calc_arm_angle(shoulder,elbow,wrist):
    v1 =(shoulder.x - elbow.x, shoulder.y -elbow.y) #肘から肩のベクトル
    v2 =(wrist.x - elbow.x, wrist.y -elbow.y) #肘から手首のベクトル

    dot = v1[0]*v2[0] + v1[1]*v2[1]
    norm =  math.sqrt(v1[0]**2+v1[1]**2)* math.sqrt(v2[0]**2+v2[1]**2)

    cos_val =dot / norm
    cos_val =min(1,cos_val)
    cos_val =max(-1,cos_val)
    rad =math.acos(cos_val)
    angle =math.degrees(rad)
    return int(angle)

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
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)
        results = pose.process(rgb)
        rgb = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

        #ランドマーク描画
        if results.pose_landmarks:
            landmarks =results.pose_landmarks.landmark

            #右腕座標取得関係
            r_shoulder =landmarks[12]
            r_elbow =landmarks[14]
            r_wrist =landmarks[16]

            #各ランドマーク信頼度チェック
            if r_shoulder.visibility > 0.5 and \
                r_elbow.visibility > 0.5 and \
                r_wrist.visibility > 0.5:
                #角度計算
                r_angle =calc_arm_angle(r_shoulder,r_elbow,r_wrist)

                #発砲か待機かそれ以外か
                #READY
                if r_angle <= 150:
                    cv2.putText(frame, "READY",
                                (10,100),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1,(200,200,200),2) #gray
            
                #WAITING
                elif r_angle > 150 and r_wrist.y >r_shoulder.y:
                    cv2.putText(frame,"WAITING",
                                (10,100),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1,(255,0,0),2) #blue
            
            #FIRE
                elif r_angle >150 and abs(r_wrist.y - r_shoulder.y) < 0.1:
                    cv2.putText(frame,"FIRE!",
                                (10,100),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1,(0,0,255),2) #red

                #画面に角度表示
                cv2.putText(
                    frame, f"Angle:{r_angle}",
                    (10,50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,(0,255,0),2)
        
                mp_drawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS
                )

            #画面表示
            cv2.imshow("Game", frame)

            #q end
            if cv2.waitKey(5) & 0xFF == ord("q"): #ord= str->int
                break

cap.release()
cv2.destroyAllWindows()