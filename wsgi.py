from app import app
import os
application = app

if __name__ == '__main__':
    app.run(host="virtual-docent.herokuapp.com", port=int(os.environ['PORT']))

