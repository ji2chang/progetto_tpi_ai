import mediapipe as mp
import numpy as np
import math

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

def vector_2d_angle(v1, v2):
    v1_x = v1[0]
    v1_y = v1[1]
    v2_x = v2[0]
    v2_y = v2[1]
    try:
        angle_= math.degrees(math.acos((v1_x*v2_x+v1_y*v2_y)/(((v1_x**2+v1_y**2)**0.5)*((v2_x**2+v2_y**2)**0.5))))
    except:
        angle_ = 180
    return angle_

def hand_angle(hand_):
    angle_list = []
    angle_ = vector_2d_angle(
        ((int(hand_[0][0])- int(hand_[2][0])),(int(hand_[0][1])-int(hand_[2][1]))),
        ((int(hand_[3][0])- int(hand_[4][0])),(int(hand_[3][1])- int(hand_[4][1])))
        )
    angle_list.append(angle_)
    angle_ = vector_2d_angle(
        ((int(hand_[0][0])-int(hand_[6][0])),(int(hand_[0][1])- int(hand_[6][1]))),
        ((int(hand_[7][0])- int(hand_[8][0])),(int(hand_[7][1])- int(hand_[8][1])))
        )
    angle_list.append(angle_)
    angle_ = vector_2d_angle(
        ((int(hand_[0][0])- int(hand_[10][0])),(int(hand_[0][1])- int(hand_[10][1]))),
        ((int(hand_[11][0])- int(hand_[12][0])),(int(hand_[11][1])- int(hand_[12][1])))
        )
    angle_list.append(angle_)
    angle_ = vector_2d_angle(
        ((int(hand_[0][0])- int(hand_[14][0])),(int(hand_[0][1])- int(hand_[14][1]))),
        ((int(hand_[15][0])- int(hand_[16][0])),(int(hand_[15][1])- int(hand_[16][1])))
        )
    angle_list.append(angle_)
    angle_ = vector_2d_angle(
        ((int(hand_[0][0])- int(hand_[18][0])),(int(hand_[0][1])- int(hand_[18][1]))),
        ((int(hand_[19][0])- int(hand_[20][0])),(int(hand_[19][1])- int(hand_[20][1])))
        )
    angle_list.append(angle_)
    return angle_list


def hand_pos(finger_angle):
    f1 = finger_angle[0]
    f2 = finger_angle[1]
    f3 = finger_angle[2]
    f4 = finger_angle[3]
    f5 = finger_angle[4]

    if f1 < 50 and f2 < 50 and f3 < 50 and f4 >= 50 and f5 >= 50:
        return 'def_hig' # ? Controllare se questo essere effettivamente def_hig
    elif f1 >= 50 and f2 < 50 and f3 < 50 and f4 < 50 and f5 < 50:
        return 'def'
    elif f1 >= 50 and f2 < 50 and f3 >= 50 and f4 >= 50 and f5 < 50:
        return 'atk'
    elif f1 >= 50 and f2 < 50 and f3 >= 50 and f4 >= 50 and f5 >= 50:
        return 'atk_hig'
    return ''

hands = mp_hands.Hands(model_complexity=0,min_detection_confidence=0.5,min_tracking_confidence=0.5)

def get_pos_img(img):
    results = hands.process(img)
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            finger_points = []
            for i in hand_landmarks.landmark:
                x = int(i.x * img.shape[1])
                y = int(i.y * img.shape[0])
                finger_points.append((x, y))
            if finger_points:
                finger_angle = hand_angle(finger_points)
                return hand_pos(finger_angle)
    return ''
