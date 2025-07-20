from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Bot is alive!'

def run():
    # RenderはPORT環境変数でポートを指定してくる
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    run()
