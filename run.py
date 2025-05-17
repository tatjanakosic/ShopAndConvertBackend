from app import create_app, db
from app import models  # Ensure models are imported before create_all()
from apscheduler.schedulers.background import BackgroundScheduler
from app.routes import process_pending_purchases

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        scheduler = BackgroundScheduler()
        # Користимо lambda да проследимо app аргумент
        scheduler.add_job(func=lambda: process_pending_purchases(app), trigger="interval", seconds=60)
        scheduler.start()

    app.run(debug=True)
    #app.run(host='0.0.0.0', port=5000)
