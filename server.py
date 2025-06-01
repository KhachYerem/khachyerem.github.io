from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import os
import json
import uuid

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "http://localhost:5001"]}})


REQUESTS_FILE = 'requests.json'
MESSAGES_FILE = 'messages.json'


if not os.path.exists(REQUESTS_FILE):
    with open(REQUESTS_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)

if not os.path.exists(MESSAGES_FILE):
    with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)

def read_requests():
    with open(REQUESTS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_requests(requests):
    with open(REQUESTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(requests, f)

def read_messages():
    with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_messages(messages):
    with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
        json.dump(messages, f)

@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    data_string = (
        f"ФИО: {data.get('fullName', '')}\n"
        f"Email: {data.get('email', '')}\n"
        f"Гражданство: {data.get('citizenship', '')}\n"
        f"Тип документа: {data.get('documentType', '')}\n"
        f"Номер документа: {data.get('documentNumber', '')}\n"
        f"Дата действительности документа: {data.get('validityDate', '')}\n"
        f"Пол: {data.get('gender', '')}\n"
        f"Дата рождения: {data.get('dob', '')}\n"
        f"Время отправки: {data.get('timestamp', '')}\n"
        f"Страна: {data.get('country', 'Не указана')}\n"
        f"------------------------\n"
    )

    with open('user_data.txt', 'a', encoding='utf-8') as f:
        f.write(data_string)

    request_id = str(uuid.uuid4())
    request_data = {
        'id': request_id,
        'fullName': data.get('fullName', ''),
        'email': data.get('email', ''),
        'citizenship': data.get('citizenship', ''),
        'documentType': data.get('documentType', ''),
        'documentNumber': data.get('documentNumber', ''),
        'validityDate': data.get('validityDate', ''),
        'gender': data.get('gender', ''),
        'dob': data.get('dob', ''),
        'timestamp': data.get('timestamp', ''),
        'status': 'pending',
        'country': data.get('country', 'Не указана')
    }
    requests = read_requests()
    requests.append(request_data)
    write_requests(requests)

    try:
        result = subprocess.run(
            ['python', 'send_email.py', 'emptymailfortest@gmail.com', data_string],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return jsonify({'message': 'Данные сохранены и отправлены на email'}), 200
        else:
            return jsonify({'error': 'Ошибка при отправке email: ' + result.stderr}), 500
    except Exception as e:
        return jsonify({'error': 'Ошибка: ' + str(e)}), 500

@app.route('/requests', methods=['GET'])
def get_requests():
    return jsonify(read_requests())

@app.route('/action/<request_id>/<action>', methods=['POST'])
def handle_action(request_id, action):
    if action not in ['accept', 'reject']:
        return jsonify({'error': 'Недопустимое действие'}), 400

    requests = read_requests()
    for req in requests:
        if req['id'] == request_id:
            req['status'] = action
            email = req['email']
            gender = req.get('gender', '').lower()
            status_text = "принята" if action == 'accept' else "нет"
            if gender == 'male' and action == 'accept':
                status_text = "принят"
            message = f"Ваш запрос: {status_text}.\nПодробности: {req['fullName']}, {req['timestamp']}"
            try:
                result = subprocess.run(
                    ['python', 'send_email.py', email, message],
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    return jsonify({'error': 'Ошибка при отправке email: ' + result.stderr}), 500
            except Exception as e:
                return jsonify({'error': 'Ошибка при отправке email: ' + str(e)}), 500
            break

    write_requests(requests)
    return jsonify({'message': f'Запрос {request_id} {action}ed', 'status': action})

@app.route('/messages', methods=['GET'])
def get_messages():
    return jsonify(read_messages())

@app.route('/send_message', methods=['POST'])
def send_message():
    message = request.get_json()
    messages = read_messages()
    messages.append(message)
    write_messages(messages)
    return jsonify({'message': 'Сообщение отправлено'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)