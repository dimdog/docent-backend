from app import app
import os
application = app

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ['PORT']))

