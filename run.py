import os
from fixu import create_app

os.environ.setdefault("FIXU_BOOTSTRAP_DB", "1")
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
