# 假设菜品数据已经整理好
menu_data = [
    {"name": "虾", "fat": 0.014, "carbs": 0, "protein": 0.191},
    {"name": "黑鱼片", "fat": 0.045, "carbs": 0.051, "protein": 0.106},
    {"name": "五色糙米", "fat": 0.031, "carbs": 0.75, "protein": 0.088, "fixed": True},
    {"name": "番茄", "fat": 0.002, "carbs": 0.033, "protein": 0.009},
]

# 设定营养目标
daily_nutrition_goals = {
    # "calories": (1600, 1700),
    "fat": (50, 60),
    "carbs": (200, 250),
    "protein": (90, 100),
}


import time
import numpy as np
from numpy.linalg import solve

i = 0
while True:
    pl = np.array([[0.014, 0.045, 0.031], [0, 0.051, 0.75], [0.191, 0.106, 0.088]])
    y = np.array([i, 200, 90])
    print(i, solve(pl, y))
    time.sleep(0.5)
    if i > 1000:
        break
    i += 1
