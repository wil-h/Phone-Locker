from flask import Flask, request, render_template, send_file, g, jsonify
from waitress import serve

app = Flask(__name__)

@app.route('/api/startstatus', methods=['POST'])
def start():
    with open('database.txt', 'w') as file:
        file.write('go')
        file.close()
    return 'done'

@app.route('/api/getstatus', methods=['GET'])
def get():
    with open('database.txt', 'r') as file:
        read=file.read()
        if read!="working":
            return read
    return 'waiting'

@app.route('/api/startprocess', methods=['GET'])
def ready():
    ready=False
    with open('database.txt', 'r') as file:
        if file.read()=='go':
            ready=True
    if ready:
        with open('database.txt', 'w') as file:
            file.write("working")
            file.close()
        return 'go'
    else:
        return 'no'

@app.route('/api/writedb', methods=['POST'])
def write():
    data = request.form
    status=data.get("status")
    with open('database.txt', 'w') as file:
        file.write(status)
        file.close()
    return 'done'

if __name__ == '__main__':
    serve(app,host = '0.0.0.0',port = 5000)
    #app.run(debug=True,host='0.0.0.0')
