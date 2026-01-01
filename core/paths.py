from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # project root
APP_DIR = BASE_DIR / "app"
TEMPLATES_DIR = APP_DIR / "templates"
STATIC_DIR = APP_DIR / "static"
