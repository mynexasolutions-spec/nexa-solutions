from app import create_app

app = create_app()

if __name__ == "__main__":
    # Setting debug=True allows you to see errors and auto-reloads when you save
    app.run(debug=True)