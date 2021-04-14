#flask imports
from flask import Flask, jsonify, request


#third party imports
from tactic_client_lib.tactic_server_stub import TacticServerStub
from decouple import config
from strgen import StringGenerator as SG

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
    try:
        request_data = request.get_json(silent=True)
        server = connect_tactic(request_data["project"], request_data["ticket"])
        filters = []
        filters.append(("assigned", request_data["username"]))
        filters.append(("project_code", request_data["project"]))
        tasks = server.query("sthpw/task", filters)
        return jsonify(tasks)
    except:
        return jsonify({"error": "An error occurred!"})


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
        path = server.get_path_from_snapshot(request_data["snapshotCode"], mode="web")
        path = host + path
        return jsonify(path)
    except:
        return jsonify({"error": "An error occured"})


@app.route('/checkin-file', methods=['POST'])
def checkin_file():
    request_data = json.loads(request.form.get("json_data"))
    server = connect_tactic(request_data["project"], request_data["ticket"])
    
    try:
        #update task status
        updated_data = server.update(search_key=request_data["key"], data={"status": request_data["status"]})

        #add note
        created_note = server.create_note(
                        search_key=request_data["SOKey"], 
                        note=request_data["message"], 
                        process=request_data["process"], 
                        user=request_data["username"])


        #save file before checkin
        file = request.files["file"]
        unique_filename = SG(r"[\w]{30}").render() + file.filename
        path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(path)

        search_key = server.build_search_key(request_data["SOType"], request_data["SOCode"])
        snapshot = server.simple_checkin(
                    search_key=search_key, 
                    context=request_data["process"], 
                    file_path=path, 
                    description=request_data["message"], 
                    mode="upload")
        if(snapshot):
            return jsonify({"success": "Checkin completed!"})
    except:
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
    try:
        request_data = request.get_json(silent=True)
        server = connect_tactic(request_data["project"], request_data["ticket"])
        notes = server.query("sthpw/note")
        return jsonify(notes)
    except:
        return jsonify({"error": "An error occured!"})


@app.route('/projects', methods=['POST'])
def projects():
    try:
        request_data = request.get_json(silent=True)
        server = connect_tactic(request_data["project"], request_data["ticket"])
        projects = server.query("sthpw/project")
        return jsonify(projects)
    except:
        return jsonify({"error": "An error occured!"})


@app.route('/process-state', methods=['POST'])
def process_state():
    try:
        request_data = request.get_json(silent=True)
        server = connect_tactic(request_data["project"], request_data["ticket"])
        projects = server.query("config/process_state")
        return jsonify(projects)
    except:
        return jsonify({"error": "An error occured!"})


@app.route('/users', methods=['POST'])
def users():
    try:
        request_data = request.get_json(silent=True)
        server = connect_tactic(request_data["project"], request_data["ticket"])
        users = server.query("sthpw/login")
        return jsonify(users)
    except:
        return jsonify({"error": "An error occured!"})



if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)

