import cv2
import mediapipe as mp
import random 
import math
import time
import numpy as np
import socket
import json

#定義
frame_count =0
game_state ="READY"
waiting_start =None
signal_time =None
reaction_time =None
wait_duration =0
UNITY_HOST = "127.0.0.1"
UNITY_PORT = 5006
udp_socket = None

#MediaPipe初期化
mp_pose =mp.solutions.pose
mp_drawing =mp.solutions.drawing_utils

#UDPsocket初期化
def init_udp_communication():
    global udp_socket
    try:
        udp_socket =socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print(f"UDP通信を初期化しました ({UNITY_HOST}:{UNITY_PORT})")
        return True
    except Exception as e:
        print(f"UDP初期化失敗: {e}")
        return False

#メッセージ送信関数
def send_to_unity_udp(message):
    global udp_socket
    if not udp_socket:
        return False
    
    try:
        json_message = json.dumps(message)
        udp_socket.sendto(json_message.encode('utf-8'), (UNITY_HOST, UNITY_PORT))
        return True
    except Exception as e:
        print(f"UDP送信エラー: {e}")
        return False
    
def calc_arm_angle(shoulder,elbow,wrist):
    v1 =(shoulder.x - elbow.x, shoulder.y -elbow.y) #肘から肩のベクトル
    v2 =(wrist.x - elbow.x, wrist.y -elbow.y) #肘から手首のベクトル

    dot =v1[0]*v2[0] + v1[1]*v2[1] #内積
    norm =math.sqrt(v1[0]**2+v1[1]**2)* math.sqrt(v2[0]**2+v2[1]**2)

    cos_val =dot / norm
    cos_val =min(1,cos_val) #上限を1に
    cos_val =max(-1,cos_val) #下限を-1に
    rad =math.acos(cos_val) #cosa->Arad
    angle =math.degrees(rad) #Arad->αdegrees
    return int(angle)

#カメラ起動
init_udp_communication()
cap =cv2.VideoCapture(0)

with mp_pose.Pose(
    min_detection_confidence=0.5, min_tracking_confidence=0.5, model_complexity=0
) as pose:
    while cap.isOpened():
        ret, frame = cap.read() #ret=return
        if not ret:
            break
        
        #MediaPipe処理
        rgb =cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results =pose.process(rgb)
        rgb =cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

        #ランドマーク描画
        if results.pose_landmarks:
            landmarks =results.pose_landmarks.landmark

            #右腕座標取得関係
            r_shoulder =landmarks[12]
            r_elbow =landmarks[14]
            r_wrist =landmarks[16]

            #各ランドマーク信頼度チェック
            if r_shoulder.visibility >0.5 and \
                r_elbow.visibility >0.5 and \
                r_wrist.visibility >0.5:
                #角度計算
                r_angle =calc_arm_angle(r_shoulder,r_elbow,r_wrist)

                arm_down=r_angle >150 and r_wrist.y >r_shoulder.y
                arm_fire=r_angle >150 and abs(r_wrist.y - r_shoulder.y) < 0.1
                
                #発砲か待機かそれ以外か
                #READY
                if game_state =="READY":
                    cv2.putText(frame, "READY",
                                (10,100),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1,(200,200,200),2)
                    if arm_down:
                        game_state ="WAITING"
                        wait_duration = random.uniform(3, 6)
                        waiting_start = time.time() #gray
            
                #WAITING
                elif game_state =="WAITING":
                    cv2.putText(frame,"WAITING",
                                (10,100),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1,(255,0,0),2) #blue
                    if not arm_down: #if arm up->return READY
                        game_state ="READY"
                    elapsed =time.time() -waiting_start
                    print(f"待機時間:{elapsed:.2f}")
                    if elapsed >=wait_duration:
                        game_state ="SIGNAL"
                        signal_time =time.time()

                #FIRE
                elif game_state =="SIGNAL":
                    cv2.putText(frame,"!",
                    (280, 240),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    5, (0, 0, 255), 5)
                    if arm_fire:
                        reaction_time =time.time() - signal_time
                        print(f"反応時間:{reaction_time:.2f}")
                        game_state ="RESULT"

                elif game_state =="RESULT":
                    cv2.putText(frame,f"Time:{reaction_time:.2f}",
                    (10, 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1, (255, 255, 0), 2)
            
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
                send_to_unity_udp({
                    "type": "game_state",
                    "state": game_state,
                    "reaction_time": reaction_time if reaction_time else 0,
                    "timestamp": time.time()
                })

                #デバッグ用座標表示
                #frame_count +=1
                #if frame_count % 30 ==0:
                #    print(f"W_y:{r_wrist.y:.2f} S_y:{r_shoulder.y:.2f} Diff:{abs(r_wrist.y - r_shoulder.y):.2f}")
            
            else: #mediapipeが動作していないときREADY
                cv2.putText(frame,"READY",
                (10, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                1, (200, 200, 200), 2)
                
            #画面表示
        cv2.imshow("Game", frame)

        #q end
        if cv2.waitKey(5) & 0xFF ==ord("q"): #ord= str->int
            break

# リソースの解放
if udp_socket:
    udp_socket.close()
cap.release()
cv2.destroyAllWindows()