#flask imports
from flask import Flask, jsonify, request


#third party imports
from tactic_client_lib.tactic_server_stub import TacticServerStub
from decouple import config

#python imports
import json
import os


UPLOAD_FOLDER = './media'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


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
    # try:
    request_data = request.get_json(silent=True)
    server = connect_tactic(request_data["project"], request_data["ticket"])
    filters = []
    filters.append(("assigned", request_data["username"]))
    filters.append(("project_code", request_data["project"]))
    tasks = server.query("sthpw/task", filters)
    return jsonify(tasks)
    # except:
        retur/n jsonify({"error": "An error occurred!"})


@app.route('/objects', methods=['POST'])
def objects():
    try:
        request_data = request.get_json(silent=True)
        server = connect_tactic(request_data["project"], request_data["ticket"])
        objects = server.query(request_data["searchType"])
        return jsonify(objects)
    except:
        return jsonify({"error": "An error occured"})


@app.route('/snapshot', methods=['POST'])
def snapshot():
    try:
        request_data = request.get_json(silent=True)
        server = connect_tactic(request_data["project"], request_data["ticket"])
        snapshots = server.query("sthpw/snapshot")
        return jsonify(snapshots)
    except:
        return jsonify({"error": "An error occured"})


@app.route('/get-path', methods=['POST'])
def get_path():
    try:
        request_data = request.get_json(silent=True)
        server = connect_tactic(request_data["project"], request_data["ticket"])
        path = server.get_path_from_snapshot(request_data["code"], mode="web")
        return jsonify(path)
    except:
        return jsonify({"error": "An error occured"})


@app.route('/checkin-file', methods=['POST'])
def checkin_file():
    request_data = json.loads(request.form.get("json_data"))
    server = connect_tactic(request_data["project"], request_data["ticket"])

    #update task status
    updated_data = server.update(search_key=request_data["key"], data={"status": request_data["status"]})
    if(not updated_data):
        return jsonify({"error": "An error occurred"})

    #save file before checkin
    file = request.files["file"]
    path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(path)

    snapshot = server.simple_checkin(
                search_key=request_data["key"], 
                context=request_data["process"], 
                file_path=path, 
                description=request_data["message"], 
                mode="upload")
    if(snapshot):
        return jsonify({"success": "Checkin completed!"})
    else:
        return jsonify({"error": "An error occurred!"})


@app.route('/checkin-note', methods=['POST'])
def checkin_note():
    request_data = request.get_json(silent=True)
    server = connect_tactic(request_data["project"], request_data["ticket"])

    #update task status
    updated_data = server.update(search_key=request_data["key"], data={"status": request_data["status"]})
    if(not updated_data):
        return jsonify({"error": "An error occurred"})

    #add note
    created_note = server.create_note(
                    search_key=request_data["SOKey"], 
                    note=request_data["message"], 
                    process=request_data["process"], 
                    user=request_data["username"])
    if(created_note):
        return jsonify({"success": "Checkin completed!"})
    else:
        return jsonify({"error": "An error occurred!"})


@app.route('/notes', methods=['POST'])
def notes():
    request_data = request.get_json(silent=True)
    server = connect_tactic(request_data["project"], request_data["ticket"])

    notes = server.query("sthpw/note")
    return jsonify(notes)



if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)

