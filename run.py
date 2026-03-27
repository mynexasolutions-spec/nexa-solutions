from app import create_app
import sys
import io

# Force UTF-8 for the terminal logs
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

app = create_app()

if __name__ == "__main__":
    # Setting debug=True allows you to see errors and auto-reloads when you save
    app.run(debug=True)