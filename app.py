from flask import Flask, jsonify, request


#third party import
from tactic_client_lib.tactic_server_stub import TacticServerStub
from decouple import config


app = Flask(__name__)


#global
host = config('HOST')

# Helper functions
def connect_tactic(project, ticket):
    server = TacticServerStub(protocol='xmlrpc', setup=False)
    server.set_server(host)
    server.set_project(project)
    server.set_ticket(ticket)
    return server



#routes
@app.route('/')
def hello():
    return 'Hello World!'


@app.route('/login', methods=['GET','POST'])
def login():
    request_data = request.get_json(silent=True)
    project = request_data["project"]
    username = request_data["username"]
    password = request_data["password"]
    try:
        server = TacticServerStub(protocol='xmlrpc', setup=False)
        server.set_server(host)
        server.set_project(project)
        ticket = server.get_ticket(username, password)
        return jsonify(ticket)
    except:
        return jsonify({"error": "Invalid Username/Password"})
    # content = request.get_json(silent=True)
    # return jsonify(content)
    

@app.route('/tasks', methods=['GET','POST'])
def tasks():
    request_data = request.get_json(silent=True)
    server = connect_tactic(request_data["project"], request_data["ticket"])
    tasks = server.query("sthpw/task")
    return jsonify(tasks)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)

