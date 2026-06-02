import time
import numpy as np
from pynput import keyboard, mouse

key_times = []
mouse_speeds = []
mouse_moves = 0
last_pos = None

def on_press(key):
    key_times.append(time.time())
    if len(key_times) > 1000:
        key_times.pop(0)

kb_listener = keyboard.Listener(on_press=on_press)
kb_listener.start()

def on_move(x, y):
    global last_pos, mouse_moves
    if last_pos:
        dx = x - last_pos[0]
        dy = y - last_pos[1]
        speed = (dx**2 + dy**2)**0.5
        mouse_speeds.append(speed)
        if len(mouse_speeds) > 1000:
            mouse_speeds.pop(0)
        mouse_moves += 1
    last_pos = (x, y)

ms_listener = mouse.Listener(on_move=on_move)
ms_listener.start()

def collect_input_event():
    now = time.time()
    intervals = [j - i for i, j in zip(key_times[:-1], key_times[1:])] if len(key_times)>1 else [0.1]
    
    typing_variance = float(np.var(intervals)) if len(intervals) > 1 else 0.0
    
    mouse_accels = [mouse_speeds[i] - mouse_speeds[i-1] for i in range(1, len(mouse_speeds))] if len(mouse_speeds) > 1 else [0.0]
    mouse_acceleration = float(sum(mouse_accels)/len(mouse_accels)) if mouse_accels else 0.0
    
    return {
        "avg_key_interval": sum(intervals)/len(intervals),
        "typing_variance": typing_variance,
        "min_key_interval": min(intervals),
        "max_key_interval": max(intervals),
        "key_presses_count": len(key_times),
        "avg_mouse_speed": sum(mouse_speeds)/len(mouse_speeds) if mouse_speeds else 0,
        "mouse_acceleration": mouse_acceleration,
        "min_mouse_speed": min(mouse_speeds) if mouse_speeds else 0,
        "max_mouse_speed": max(mouse_speeds) if mouse_speeds else 0,
        "mouse_moves_count": mouse_moves,
        "system_time": time.strftime("%H:%M:%S", time.localtime())
    }