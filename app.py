from flask import Flask, request, Response, jsonify, session
from werkzeug.serving import run_simple
from uuid import uuid4

from app_symptom_checker.question_const import *
from deepcare.inference.inference import *
from deepcare.database.query_en import DC_Query_En

from deepcare.database.query import DC_Query
from deepcare.entity.user import User
from text_proccess.text_proccess import TextProcess
from redis_module.redis_server import RedisServer
from configs import api_setting
from configs import data_file
from configs import redis_settings

import setting
import json
import pickle


app = Flask(__name__)

app.secret_key = "deepcare"
app.config['SESSION_TYPE'] = 'filesystem'
app.config['JSON_AS_ASCII'] = False


query = {"vi" : DC_Query(data_file.APP_ONTOLOGY), 
         "en" : DC_Query_En(data_file.APP_ONTOLOGY)}
inference = {"vi" : DC_Inference(query["vi"], data_file.APP_ONTO2VEC),
             "en" : DC_Inference(query["en"], data_file.APP_ONTO2VEC, lang="en")}
text_process = {"vi" : TextProcess(),
                "en" : TextProcess(lang="en")}


redis_server = RedisServer(host=redis_settings.HOST, port=redis_settings.PORT, db=redis_settings.DB)


# user = User("tht", 22, "Nam")
# checker_test = DC_SymptomChecker(user, "<http://deepcare.io/dd0113c8_ae5a_4ca6_b645_27e1091afa1d>", inference["vi"], query["vi"])
# print("filting")
# checker_test.filt(query["vi"])
# redis_server.set_obj("ab665735-6617-4b49-96f7-c4c7b4357ade", checker_test)

def get_language(data):
    try:
        lang = data["language"]
    except Exception:
        lang = "vi"
    return lang

#API trich xuat trieu chung tu input nguoi dung
@app.route("/api/symptom_checker/extract_symptoms/vi", methods=["POST"])
def extract_symptoms_vi():
    data_input = json.loads(request.data.decode("utf-8"))
    user_input_string = data_input["user_input"]
    lang = get_language(data_input)
    symptom_list = text_process[lang].extract(user_input_string)
    data_return = {
        "symptoms": symptom_list,
        "confirm_question": QUESTION_GET_SYMPTOM[lang]["confirm_question"],
        "pick_question": QUESTION_GET_SYMPTOM[lang]["pick_question"]
    }
    
    if len(symptom_list) == 0:
        data_return["type"] = "none"
    elif len(symptom_list) == 1:
        data_return["type"] = "single"
    else:
        data_return["type"] = "multiple"
    return jsonify(data_return)

@app.route("/api/symptom_checker/extract_symptoms", methods=["POST"])
def extract_symptoms():
    data_input = json.loads(request.data.decode("utf-8"))
    user_input_string = data_input["user_input"]
    lang = get_language(data_input)
    symptom_list = text_process[lang].extract(user_input_string)
    data_return = {
        "symptoms": symptom_list,
        "confirm_question": QUESTION_GET_SYMPTOM[lang]["confirm_question"],
        "pick_question": QUESTION_GET_SYMPTOM[lang]["pick_question"]
    }
    
    if len(symptom_list) == 0:
        data_return["type"] = "none"
    elif len(symptom_list) == 1:
        data_return["type"] = "single"
    else:
        data_return["type"] = "multiple"
    return jsonify(data_return)

@app.route("/api/symptom_checker/start_session/vi", methods=["POST"])
def start_session_vi():
    data = json.loads(request.data.decode("utf-8"))
    lang = get_language(data)
    user = User(data["user"]["name"], int(data["user"]["age"]), data["user"]["gender"])
    symptom_init = data['symptom_init']
    symptoms = data['symptoms']
    symptom_pos = data['symptom_pos']
    symptom_neg = list(set(symptoms) - set(symptom_pos))

    symptom_pos_iri = [inference[lang].symptom_dict_iri[s.replace("_"," ")] for s in symptom_pos]
    symptom_neg_iri = [inference[lang].symptom_dict_iri[s.replace("_"," ")] for s in symptom_neg]
    symptom_init_iri = inference[lang].symptom_dict_iri[symptom_init.replace("_", " ")]
    for s in symptom_pos_iri:
        if inference[lang].symptoms[s].gender != None and inference[lang].symptoms[s].gender != user.gender:
            data_return = {
                    "token" : "error",
                    "status": "gender_error"
                    }
            return jsonify(data_return)
    checker = DC_SymptomChecker(user, symptom_init_iri, inference[lang], query[lang])
    checker.positive_user_symptoms.extend(symptom_pos_iri)
    checker.negative_user_symptoms.extend(symptom_neg_iri)
    token = str(uuid4())
    redis_server.set_obj(token, checker)
    data_return = {
        "token": token,
        "status": "success"
    }
    return jsonify(data_return)

@app.route("/api/symptom_checker/start_session", methods=["POST"])
def start_session():
    data = json.loads(request.data.decode("utf-8"))
    lang = get_language(data)
    user = User(data["user"]["name"], int(data["user"]["age"]), data["user"]["gender"])
    symptom_init = data['symptom_init']
    symptoms = data['symptoms']
    symptom_pos = data['symptom_pos']
    symptom_neg = list(set(symptoms) - set(symptom_pos))

    symptom_pos_iri = [inference[lang].symptom_dict_iri[s.replace("_"," ")] for s in symptom_pos]
    symptom_neg_iri = [inference[lang].symptom_dict_iri[s.replace("_"," ")] for s in symptom_neg]
    symptom_init_iri = inference[lang].symptom_dict_iri[symptom_init.replace("_", " ")]
    for s in symptom_pos_iri:
        if inference[lang].symptoms[s].gender != None and inference[lang].symptoms[s].gender != user.gender:
            data_return = {
                    "token" : "error",
                    "status": "gender_error"
                    }
            return jsonify(data_return)
    checker = DC_SymptomChecker(user, symptom_init_iri, inference[lang], query[lang])
    checker.positive_user_symptoms.extend(symptom_pos_iri)
    checker.negative_user_symptoms.extend(symptom_neg_iri)
    token = str(uuid4())
    redis_server.set_obj(token, checker)
    data_return = {
        "token": token,
        "status": "success"
    }
    return jsonify(data_return)


#API tra ve cac cau hoi ve cac dac diem, tinh chat cua trieu chung duoc nhap vao
@app.route("/api/symptom_checker/get_question_init/vi", methods=["POST"])
def get_question_init_vi():
    data = json.loads(request.data.decode("utf-8"))
    token = data["token"]
    lang = get_language(data)
    r_checker = redis_server.get_obj(token)
    checker = r_checker.load_to_symptom_checker(inference[lang], query[lang])
    questions = checker.get_init_questions()
    data_return = {
            "symptom_init": checker.symptom_init,
            "token": token,
            "questions": []
        }
    symptom_label = inference[lang].symptoms[checker.symptom_init].label
    if len(questions["where"]["iri"]) > 0:
        question = {
            "type": "symptom_where",
            "a_type": "multiple",
            "question": QUESTION_SYMPTOM_INIT_INFO[lang]["where"]["question"]%(symptom_label.lower().replace("_"," ")),
            "answer": [q.split(",")[0].replace("_"," ") for q in questions["where"]["label"]],
            "items": {
                "label": [q.split(",")[0].replace("_"," ") for q in questions["where"]["label"]],
                "iri": questions["where"]["iri"]
            }
        }
        data_return["questions"].append(question)
    if len(questions["when"]["iri"]) > 0:
        question = {
            "type": "symptom_when",
            "a_type": "multiple",
            "question": QUESTION_SYMPTOM_INIT_INFO[lang]["when"]["question"]%(symptom_label.lower().replace("_"," ")),
            "answer": [q.split(",")[0].replace("_"," ") for q in questions["when"]["label"]],
            "items":{
                "label": [q.split(",")[0].replace("_"," ") for q in questions["when"]["label"]],
                "iri": questions["when"]["iri"]
            }
        }
        data_return["questions"].append(question)
    if len(questions["how"]["iri"]) > 0:
        question = {
            "type": "symptom_how",
            "a_type": "multiple",
            "question": QUESTION_SYMPTOM_INIT_INFO[lang]["how"]["question"]%(symptom_label.lower().replace("_"," ")),
            "answer": [q.split(",")[0].replace("_"," ") for q in questions["how"]["label"]],
            "items":{
                "label": [q.split(",")[0].replace("_"," ") for q in questions["how"]["label"]],
                "iri": questions["how"]["iri"]
            }
        }
        data_return["questions"].append(question)
    return jsonify(data_return)

@app.route("/api/symptom_checker/get_question_init", methods=["POST"])
def get_question_init():
    data = json.loads(request.data.decode("utf-8"))
    token = data["token"]
    lang = get_language(data)
    r_checker = redis_server.get_obj(token)
    checker = r_checker.load_to_symptom_checker(inference[lang], query[lang])
    questions = checker.get_init_questions()
    data_return = {
            "symptom_init": checker.symptom_init,
            "token": token,
            "questions": []
        }
    symptom_label = inference[lang].symptoms[checker.symptom_init].label
    if len(questions["where"]["iri"]) > 0:
        question = {
            "type": "symptom_where",
            "a_type": "multiple",
            "question": QUESTION_SYMPTOM_INIT_INFO[lang]["where"]["question"]%(symptom_label.split(",")[0].lower().replace("_"," ")),
            "answer": [q.split(",")[0].replace("_"," ") for q in questions["where"]["label"]],
            "items": {
                "label": [q.split(",")[0].replace("_"," ") for q in questions["where"]["label"]],
                "iri": questions["where"]["iri"]
            }
        }
        data_return["questions"].append(question)
    if len(questions["when"]["iri"]) > 0:
        question = {
            "type": "symptom_when",
            "a_type": "multiple",
            "question": QUESTION_SYMPTOM_INIT_INFO[lang]["when"]["question"]%(symptom_label.split(",")[0].lower().replace("_"," ")),
            "answer": [q.split(",")[0].replace("_"," ") for q in questions["when"]["label"]],
            "items":{
                "label": [q.split(",")[0].replace("_"," ") for q in questions["when"]["label"]],
                "iri": questions["when"]["iri"]
            }
        }
        data_return["questions"].append(question)
    if len(questions["how"]["iri"]) > 0:
        question = {
            "type": "symptom_how",
            "a_type": "multiple",
            "question": QUESTION_SYMPTOM_INIT_INFO[lang]["how"]["question"]%(symptom_label.split(",")[0].lower().replace("_"," ")),
            "answer": [q.split(",")[0].replace("_"," ") for q in questions["how"]["label"]],
            "items":{
                "label": [q.split(",")[0].replace("_"," ") for q in questions["how"]["label"]],
                "iri": questions["how"]["iri"]
            }
        }
        data_return["questions"].append(question)
    return jsonify(data_return)

@app.route("/api/symptom_checker/get_question_init_where", methods=["POST"])
def get_question_init_where():
    data = json.loads(request.data.decode("utf-8"))
    token = data["token"]
    lang = get_language(data)
    r_checker = redis_server.get_obj(token)
    checker = r_checker.load_to_symptom_checker(inference[lang], query[lang])
    questions = checker.get_init_questions()
    data_return = {
            "symptom_init": checker.symptom_init,
            "token": token,
            "questions": []
        }
    symptom_label = inference[lang].symptoms[checker.symptom_init].label
    if len(questions["where"]["iri"]) > 0:
        question = {
            "type": "symptom_where",
            "a_type": "multiple",
            "question": QUESTION_SYMPTOM_INIT_INFO[lang]["where"]["question"]%(symptom_label.split(",")[0].lower().replace("_"," ")),
            "answer": [q.split(",")[0].replace("_"," ") for q in questions["where"]["label"]],
            "items": {
                "label": [q.split(",")[0].replace("_"," ") for q in questions["where"]["label"]],
                "iri": questions["where"]["iri"]
            }
        }
        data_return["questions"].append(question)
    return jsonify(data_return)

@app.route("/api/symptom_checker/get_question_init_when", methods=["POST"])
def get_question_init_when():
    data = json.loads(request.data.decode("utf-8"))
    token = data["token"]
    lang = get_language(data)
    r_checker = redis_server.get_obj(token)
    checker = r_checker.load_to_symptom_checker(inference[lang], query[lang])
    questions = checker.get_init_questions()
    data_return = {
            "symptom_init": checker.symptom_init,
            "token": token,
            "questions": []
        }
    symptom_label = inference[lang].symptoms[checker.symptom_init].label
    if len(questions["when"]["iri"]) > 0:
        question = {
            "type": "symptom_when",
            "a_type": "multiple",
            "question": QUESTION_SYMPTOM_INIT_INFO[lang]["when"]["question"]%(symptom_label.split(",")[0].lower().replace("_"," ")),
            "answer": [q.split(",")[0].replace("_"," ") for q in questions["when"]["label"]],
            "items":{
                "label": [q.split(",")[0].replace("_"," ") for q in questions["when"]["label"]],
                "iri": questions["when"]["iri"]
            }
        }
        data_return["questions"].append(question)
    return jsonify(data_return)

@app.route("/api/symptom_checker/get_question_init_how", methods=["POST"])
def get_question_init_how():
    data = json.loads(request.data.decode("utf-8"))
    token = data["token"]
    lang = get_language(data)
    r_checker = redis_server.get_obj(token)
    checker = r_checker.load_to_symptom_checker(inference[lang], query[lang])
    questions = checker.get_init_questions()
    data_return = {
            "symptom_init": checker.symptom_init,
            "token": token,
            "questions": []
        }
    symptom_label = inference[lang].symptoms[checker.symptom_init].label
    if len(questions["how"]["iri"]) > 0:
        question = {
            "type": "symptom_how",
            "a_type": "multiple",
            "question": QUESTION_SYMPTOM_INIT_INFO[lang]["how"]["question"]%(symptom_label.split(",")[0].lower().replace("_"," ")),
            "answer": [q.split(",")[0].replace("_"," ") for q in questions["how"]["label"]],
            "items":{
                "label": [q.split(",")[0].replace("_"," ") for q in questions["how"]["label"]],
                "iri": questions["how"]["iri"]
            }
        }
        data_return["questions"].append(question)
    return jsonify(data_return)


@app.route("/api/symptom_checker/handle_question_init", methods=["POST"])
def handle_question_init():
    data = json.loads(request.data.decode("utf-8"))
    token = data["token"]
    lang = get_language(data)
    r_checker = redis_server.get_obj(token)
    checker = r_checker.load_to_symptom_checker(inference[lang], query[lang])
    posivite_symptoms = data["user_symptoms"]["positive"]
    negative_symptoms = data["user_symptoms"]["negative"]

    checker.update_checker(posivite_symptoms, negative_symptoms, query[lang])
    redis_server.set_obj(token, checker)
    return jsonify({
        "token" : token,
        "status" : "success"
        })

@app.route("/api/symptom_checker/handle_question_init_z", methods=["POST"])
def handle_question_init_z():
    data = json.loads(request.data.decode("utf-8"))
    token = data["token"]
    lang = get_language(data)
    r_checker = redis_server.get_obj(token)
    checker = r_checker.load_to_symptom_checker(inference[lang], query[lang])
    posivite_symptoms = [s.lower() for s in data["user_symptoms"]["positive"]]
    negative_symptoms = [s.lower() for s in data["user_symptoms"]["negative"]]

    posivite_symptoms = [inference[lang].symptom_dict_iri[s] for s in posivite_symptoms]
    negative_symptoms = [inference[lang].symptom_dict_iri[s] for s in negative_symptoms]
    

    checker.update_checker(posivite_symptoms, negative_symptoms, query[lang])
    redis_server.set_obj(token, checker)
    return jsonify({
        "token" : token,
        "status" : "success"
        })


@app.route("/api/symptom_checker/get_question/vi", methods=["POST"])
def get_question_vi():
    data = json.loads(request.data.decode("utf-8"))
    token = data["token"]
    lang = get_language(data)
    r_checker = redis_server.get_obj(token)
    checker = r_checker.load_to_symptom_checker(inference[lang], query[lang])
    question = checker.get_multiple_choice_question()
    return jsonify(question)

@app.route("/api/symptom_checker/get_question", methods=["POST"])
def get_question():
    data = json.loads(request.data.decode("utf-8"))
    token = data["token"]
    lang = get_language(data)
    r_checker = redis_server.get_obj(token)
    checker = r_checker.load_to_symptom_checker(inference[lang], query[lang])
    question = checker.get_multiple_choice_question()
    return jsonify(question)

@app.route("/api/symptom_checker/handle_answer", methods=["POST"])
def handle_answer():
    data = json.loads(request.data.decode("utf-8"))
    token = data["token"]
    lang = get_language(data)
    r_checker = redis_server.get_obj(token)
    checker = r_checker.load_to_symptom_checker(inference[lang], query[lang])
    question_type = data["question"]["type"]
    if question_type == "stop":
        return 0

    elif question_type == "causes_list":
        causes = data["question"]["items"]["label"]
        user_answer = data["user_answer"]
        causes_yes = user_answer
        causes_no = list(set(causes) - set(user_answer))
        checker.positive_user_causes.extend(causes_yes)
        checker.negative_user_causes.extend(causes_no)

    elif question_type == "cause":
        cause = data["question"]["answer"]
        user_answer = data["user_answer"]
        if user_answer[0] == "yes":
            checker.positive_user_causes.extend(cause)
        elif user_answer[0] == "no":
            checker.negative_user_causes.extend(cause)

    elif question_type == "symptoms_list":
        symptoms = data["question"]["items"]["iri"]
        user_answer = data["user_answer"]
        symptoms_yes = user_answer
        symptoms_no = list(set(symptoms) - set(symptoms_yes))
        checker.positive_user_symptoms.extend(symptoms_yes)
        for s in symptoms_no:
            sub = query[lang].get_instance_subclass_by_iri(s)
            checker.negative_user_symptoms.append(s)
            checker.negative_user_symptoms.extend(sub)
            checker.symptoms_init = list(set(checker.symptoms_init) - set(sub))

    elif question_type == "symptom":
        symptom = data["question"]["answer"]
        user_answer = data["user_answer"]
        if user_answer[0] == "yes":
            checker.positive_user_symptoms.append(symptom)
        elif user_answer[0] == "no":
            sub = query[lang].get_instance_subclass_by_iri(symptom)
            checker.negative_user_symptoms.append(symptom)
            checker.negative_user_symptoms.extend(sub)
            checker.symptoms_init = list(set(checker.symptoms_init) - set(sub))

    checker.update_checker([],[], query[lang])
    redis_server.set_obj(token, checker)
    return jsonify({
        "token" : token,
        "status" : "success"
    })

@app.route("/api/symptom_checker/handle_answer_z", methods=["POST"])
def handle_answer_z():
    data = json.loads(request.data.decode("utf-8"))
    token = data["token"]
    lang = get_language(data)
    r_checker = redis_server.get_obj(token)
    checker = r_checker.load_to_symptom_checker(inference[lang], query[lang])
    question_type = data["question"]["type"]
    if question_type == "stop":
        return 0

    elif question_type == "causes_list":
        causes = data["question"]["items"]["label"]
        user_answer = data["user_answer"]
        causes_yes = user_answer
        causes_no = list(set(causes) - set(user_answer))
        checker.positive_user_causes.extend(causes_yes)
        checker.negative_user_causes.extend(causes_no)

    elif question_type == "cause":
        cause = data["question"]["answer"]
        user_answer = data["user_answer"]
        if user_answer[0] == "yes":
            checker.positive_user_causes.extend(cause)
        elif user_answer[0] == "no":
            checker.negative_user_causes.extend(cause)

    elif question_type == "symptoms_list":
        symptoms = data["question"]["items"]["iri"]
        user_answer = data["user_answer"]
        symptoms_yes = [s.lower() for s in user_answer]
        symptoms_no = [s.lower() for s in list(set(symptoms) - set(symptoms_yes))]

        symptoms_yes = [inference[lang].symptom_dict_iri[s] for s in symptoms_yes]
        symptoms_no = [inference[lang].symptom_dict_iri[s] for s in symptoms_no]

        checker.positive_user_symptoms.extend(symptoms_yes)
        for s in symptoms_no:
            sub = query[lang].get_instance_subclass_by_iri(s)
            checker.negative_user_symptoms.append(s)
            checker.negative_user_symptoms.extend(sub)
            checker.symptoms_init = list(set(checker.symptoms_init) - set(sub))

    elif question_type == "symptom":
        symptom = data["question"]["answer"]
        user_answer = data["user_answer"]
        if user_answer[0] == "yes":
            checker.positive_user_symptoms.append(symptom)
        elif user_answer[0] == "no":
            sub = query[lang].get_instance_subclass_by_iri(symptom)
            checker.negative_user_symptoms.append(symptom)
            checker.negative_user_symptoms.extend(sub)
            checker.symptoms_init = list(set(checker.symptoms_init) - set(sub))

    checker.update_checker([],[], query[lang])
    redis_server.set_obj(token, checker)
    return jsonify({
        "token" : token,
        "status" : "success"
    })


@app.route("/api/symptom_checker/get_question_severity/vi", methods=["POST"])
def get_question_severity_vi():
    data = json.loads(request.data.decode("utf-8"))
    token = data["token"]
    lang = get_language(data)
    r_checker = redis_server.get_obj(token)
    checker = r_checker.load_to_symptom_checker(inference[lang], query[lang])
    data_return = {
        "question_const": QUESTION_SEVERITY[lang] 
    }
    question_symptom = checker.get_symptom_to_ask_for_severity()
    data_return["question_symptom"] = question_symptom
    return jsonify(data_return)

@app.route("/api/symptom_checker/get_question_severity", methods=["POST"])
def get_question_severity():
    data = json.loads(request.data.decode("utf-8"))
    token = data["token"]
    lang = get_language(data)
    r_checker = redis_server.get_obj(token)
    checker = r_checker.load_to_symptom_checker(inference[lang], query[lang])
    data_return = {
        "question_const": QUESTION_SEVERITY[lang] 
    }
    question_symptom = checker.get_symptom_to_ask_for_severity()
    data_return["question_symptom"] = question_symptom
    return jsonify(data_return)

@app.route("/api/symptom_checker/handle_severity", methods=["POST"])
def handle_severity():
    data = json.loads(request.data.decode("utf-8"))
    token = data["token"]
    lang = get_language(data)
    r_checker = redis_server.get_obj(token)
    checker = r_checker.load_to_symptom_checker(inference[lang], query[lang])
    time = data["user_answer"]["time"]
    level = data["user_answer"]["level"][0]
    progress = data["user_answer"]["progress"]
    serious_symptom_D = data["user_answer"]["serious_symptoms"]["disease"]
    serious_symptom_S = data["user_answer"]["serious_symptoms"]["symptom"]
    
    final_result = checker.get_final_result(serious_symptom_D, serious_symptom_S, time, level, progress, query[lang])    
    data_return = {
        "token": token,
        "result": final_result
    }
    
    redis_server.clear_key(token)
    return jsonify(data_return)

@app.route("/api/symptom_checker/handle_severity_z", methods=["POST"])
def handle_severity_z():
    data = json.loads(request.data.decode("utf-8"))
    token = data["token"]
    lang = get_language(data)
    r_checker = redis_server.get_obj(token)
    checker = r_checker.load_to_symptom_checker(inference[lang], query[lang])
    time = data["user_answer"]["time"]
    level = data["user_answer"]["level"][0]
    progress = data["user_answer"]["progress"]
    serious_symptom_D = [s.lower for s in data["user_answer"]["serious_symptoms"]["disease"]]
    serious_symptom_S = [s.lower for s in data["user_answer"]["serious_symptoms"]["symptom"]]
    
    serious_symptom_D = [inference[lang].symptom_dict_iri[s] for s in serious_symptom_D]
    serious_symptom_D = [inference[lang].symptom_dict_iri[s] for s in serious_symptom_D]  

    final_result = checker.get_final_result(serious_symptom_D, serious_symptom_S, time, level, progress, query[lang])    
    data_return = {
        "token": token,
        "result": final_result
    }
    
    redis_server.clear_key(token)
    return jsonify(data_return)

@app.route("/api/symptom_checker/get_all_positions/vi", methods=["GET"])
def get_all_postitions():
    positions = query["vi"].get_all_position()
    data_return = {"positions" : positions}
    return jsonify(data_return)

@app.route("/api/symptom_checker/get_sub_postions_or_symptoms/vi", methods=["POST"])
def get_sub_positions_or_symptoms():
    data = json.loads(request.data.decode("utf-8"))
    position = data["postion"]
    result_list, result_type = inference["vi"].get_info_by_string(position, query)
    data = {
        "list" : result_list,
        "type" : result_type
    }
    return jsonify(data)

@app.route("/api/symptom_checker/get_info", methods=["GET"])
def get_info():
    data = {
        "service": "symptom_checker",
        "copyright": "deepcare",
        "year": "2020",
        "version": "v2.0.0"
    }
    return jsonify(data)

if __name__ == "__main__":
    app.run(host=api_setting.APP_BIND_ADDRESS, port=api_setting.APP_BIND_PORT, debug=True)

