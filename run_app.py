import os
import sys
import streamlit.web.cli as stcli

def resolve_path(path):
    """Resuelve la ruta absoluta al archivo, ya sea en desarrollo o dentro del .exe extraído"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, path)
    return os.path.abspath(path)

if __name__ == "__main__":
    script_path = resolve_path("landing.py")
    sys.argv = ["streamlit", "run", script_path, "--server.port=8501", "--global.developmentMode=false"]
    sys.exit(stcli.main())