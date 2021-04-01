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


@app.route('/login', methods=['POST'])
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
    

@app.route('/tasks', methods=['POST'])
def tasks():
    try:
        request_data = request.get_json(silent=True)
        server = connect_tactic(request_data["project"], request_data["ticket"])
        filters = []
        filters.append("assigned", request_data["username"])
        filters.append("project_code", request_data["project"])
        tasks = server.query("sthpw/task", filters)
        return jsonify(tasks)
    except:
        return jsonify({"error": "Invalid Username/Password"})


@app.route('/objects', methods=['POST'])
def shots():
    try:
        request_data = request.get_json(silent=True)
        server = connect_tactic(request_data["project"], request_data["ticket"])
        objects = server.query(request_data["searchType"])
        return jsonify(objects)
    except:
        return jsonify({"error": "An error occured"})

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)

