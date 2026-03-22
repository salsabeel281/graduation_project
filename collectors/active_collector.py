import pygetwindow as gw

def collect_active_application():
    try:
        win = gw.getActiveWindow()
        if win:
            return {
                "active_application": win.title.split(" - ")[-1],
                "window_title": win.title
            }
    except:
        pass
    return {"active_application": "Unknown", "window_title": "Unknown"}