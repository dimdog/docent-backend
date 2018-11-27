from app import app
import os
application = app

if __name__ == '__main__':
    app.run(port=int(os.environ['PORT']))

