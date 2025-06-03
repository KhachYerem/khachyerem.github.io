from flask import Flask, request, render_template_string, redirect, url_for, session, jsonify
from flask_cors import CORS
import os
import json
import uuid
from datetime import datetime
import subprocess

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["https://khachyerem.github.io", "http://localhost:3000"]}})
app.secret_key = os.urandom(24)

REQUESTS_FILE = 'requests.json'
MESSAGES_FILE = 'messages.json'

if not os.path.exists(REQUESTS_FILE):
    with open(REQUESTS_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)

if not os.path.exists(MESSAGES_FILE):
    with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)

def read_requests():
    try:
        with open(REQUESTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def write_requests(requests):
    try:
        with open(REQUESTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(requests, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def read_messages():
    try:
        with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def write_messages(messages):
    try:
        with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

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
        'country': data.get('country', 'Не указана'),
        'userId': data.get('userId', str(uuid.uuid4()))
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

@app.route('/api/requests', methods=['GET'])
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
            status_text = "принята" if action == 'accept' else "отклонена"
            if gender == 'male' and action == 'accept':
                status_text = "принят"
            message = f"Ваш запрос {status_text}.\nПодробности: {req['fullName']}, {req['timestamp']}"
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
    user_id = request.args.get('userId')
    messages = read_messages()
    if user_id:
        return jsonify([msg for msg in messages if msg.get('userId') == user_id])
    return jsonify(messages)

@app.route('/send_message', methods=['POST'])
def send_message():
    message = request.get_json()
    if not message or 'text' not in message or 'userId' not in message:
        return jsonify({'error': 'Некорректное сообщение'}), 400
    messages = read_messages()
    messages.append({
        'id': message.get('id', str(uuid.uuid4())),
        'sender': message.get('sender', 'unknown'),
        'text': message['text'],
        'timestamp': message.get('timestamp', datetime.now().isoformat()),
        'userId': message['userId']
    })
    write_messages(messages)
    return jsonify({'message': 'Сообщение отправлено', 'id': message['id']}), 200

@app.route('/delete_messages', methods=['POST'])
def delete_messages():
    user_id = request.json.get('userId')
    if not user_id:
        return jsonify({'error': 'No userId provided'}), 400
    messages = read_messages()
    messages[:] = [msg for msg in messages if msg.get('userId') != user_id]
    write_messages(messages)
    return jsonify({'message': 'Сообщения удалены'}), 200

VALID_USERNAME = 'manager'
VALID_PASSWORD = 'password123'

LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Вход для менеджеров</title>
    <style>
        body { font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-box { border: 1px solid #ccc; padding: 20px; border-radius: 5px; }
        .form-group { margin-bottom: 15px; }
        input { padding: 12px 16px; border: 1px solid #ccd1d5; border-radius: 4px; font-size: 16px; color: #364b66; background-color: white; transition: border-color 0.3s ease; margin-bottom: 15px; width: 265px; }
        button { padding: 5px 10px; cursor: pointer; font-size: 18px; font-weight: bold; border: 1px solid #2862AC; color: #2862AC; border-radius: 4px; height: 48px; width: 100%; transition: background-color 0.3s ease; background-color: #ffffff; }
        label { color: #7c7c7d; font-size: 14px; }
        button:hover { background-color: #2862AC; color: #ffffff; }
        h2 { margin-left: 14px; }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>Вход для менеджеров</h2>
        {% if error %}
            <p style="color: red;">{{ error }}</p>
        {% endif %}
        <form method="POST" action="/login">
            <div class="form-group">
                <label>Логин:</label><br>
                <input type="text" name="username" required>
            </div>
            <div class="form-group">
                <label>Пароль:</label><br>
                <input type="password" name="password" required>
            </div>
            <button type="submit">Войти</button>
        </form>
    </div>
</body>
</html>
'''

REQUESTS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Менеджер запросов</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { display: flex; justify-content: space-between; }
        .requests-section { width: 45%; }
        .chat-section { width: 45%; }
        .request { border: 1px solid #ccc; padding: 10px; margin: 10px 0; border-radius: 5px; }
        .chat-message { border: 1px solid #ddd; padding: 10px; margin: 10px 0; border-radius: 5px; }
        .buttons { margin-top: 10px; }
        button { padding: 5px 10px; margin-right: 10px; cursor: pointer; font-size: 18px; font-weight: bold; border: 1px solid #2862AC; color: #2862AC; border-radius: 4px; height: 43px; width: 100%; transition: background-color 0.3s ease; background-color: #ffffff; }
        button:hover { background-color: #2862AC; color: #ffffff; }
        .accepted { background-color: #d4edda; }
        .rejected { background-color: #f8d7da; }
        .logout { margin-top: 20px; }
        .chat-input { display: flex; gap: 10px; margin-top: 10px; }
        input { padding: 12px 16px; border: 1px solid #ccd1d5; border-radius: 4px; font-size: 16px; color: #364b66; background-color: white; transition: border-color 0.3s ease; margin-bottom: 15px; width: 265px; }
        .chat-input button { padding: 5px 10px; width: auto; }
        .chat-section { display: block; }
        .chat-item { cursor: pointer; padding: 5px; border-bottom: 1px solid #ddd; }
        .chat-item:hover { background-color: #f0f0f0; }
        .notification { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .success { background-color: #d4edda; color: #155724; }
        .error { background-color: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <div class="container">
        <div class="requests-section">
            <h1>Список запросов</h1>
            <div id="requests"></div>
        </div>
        <div class="chat-section">
            <h1>Чат с пользователями</h1>
            <div id="chat-list"></div>
            <div id="chat-content" style="margin-top: 20px;"></div>
        </div>
    </div>
    <div class="logout">
        <button onclick="window.location.href='/logout'">Выйти</button>
    </div>

    <script>
        let currentUserId = null;
        let isTyping = false;
        let currentMessageDraft = '';
        let lastMessages = [];

        const BASE_URL = 'https://khachyerem-github-io-4.onrender.com';

        function showNotification(message, type) {
            const notification = document.createElement('div');
            notification.className = `notification ${type}`;
            notification.innerText = message;
            document.body.insertBefore(notification, document.body.firstChild);
            setTimeout(() => notification.remove(), 3000);
        }

        async function loadRequests() {
            try {
                const response = await fetch(`${BASE_URL}/api/requests`);
                if (!response.ok) throw new Error('Ошибка загрузки запросов');
                const requests = await response.json();
                const container = document.getElementById('requests');
                container.innerHTML = '';
                requests.forEach((req, index) => {
                    const div = document.createElement('div');
                    div.className = `request ${req.status}`;
                    div.innerHTML = `<strong>Запрос №${index + 1}</strong><br>
                        ФИО: ${req.fullName}<br>
                        Email: ${req.email}<br>
                        Статус: ${req.status === 'pending' ? 'Ожидает' : req.status === 'accept' ? 'Принят' : 'Отклонён'}<br>
                        <div class="buttons">
                            <button onclick="handleAction('${req.id}', 'accept', '${req.userId}')">Принять</button>
                            <button onclick="handleAction('${req.id}', 'reject')">Отклонить</button>
                        </div>`;
                    container.appendChild(div);
                });
            } catch (error) {
                showNotification('Не удалось загрузить запросы', 'error');
            }
        }

        async function loadChatList() {
            try {
                const response = await fetch(`${BASE_URL}/messages`);
                if (!response.ok) throw new Error('Ошибка загрузки сообщений');
                const messages = await response.json();
                const userIds = [...new Set(messages.map(msg => msg.userId))];
                const chatList = document.getElementById('chat-list');
                chatList.innerHTML = '';
                userIds.forEach(userId => {
                    const chatItem = document.createElement('div');
                    chatItem.className = 'chat-item';
                    chatItem.innerHTML = `User ID: ${userId}`;
                    chatItem.onclick = () => {
                        currentUserId = userId;
                        loadChat(userId);
                    };
                    chatList.appendChild(chatItem);
                });
            } catch (error) {
                showNotification('Не удалось загрузить список чатов', 'error');
            }
        }

        async function loadChat(userId, forceUpdate = false) {
            try {
                currentUserId = userId;
                const response = await fetch(`${BASE_URL}/messages?userId=${userId}`);
                if (!response.ok) throw new Error('Ошибка загрузки чата');
                const messages = await response.json();
                const messagesString = JSON.stringify(messages);
                if (!forceUpdate && messagesString === JSON.stringify(lastMessages)) {
                    return;
                }
                lastMessages = messages;
                const chatContent = document.getElementById('chat-content');
                const replyInput = document.getElementById(`reply-${userId}`);
                const currentValue = replyInput ? replyInput.value : currentMessageDraft;
                chatContent.innerHTML = `
                    <h2>Чат с User ID: ${userId}</h2>
                    <div id="messages-${userId}"></div>
                    <div class="chat-input">
                        <input type="text" id="reply-${userId}" placeholder="Введите ответ..." value="${currentValue}">
                        <button onclick="sendReply('${userId}')">Отправить</button>
                        <button onclick="closeChat('${userId}')">Закрыть</button>
                        <button onclick="deleteChat('${userId}')">Удалить</button>
                    </div>`;
                const messagesDiv = document.getElementById(`messages-${userId}`);
                messagesDiv.innerHTML = messages.length > 0 ? messages.map(msg => `
                    <div class="chat-message">
                        <strong>${msg.sender}</strong><br>
                        ${msg.text}<br>
                        ${msg.timestamp}
                    </div>
                `).join('') : '<p>Сообщений пока нет.</p>';
                const newReplyInput = document.getElementById(`reply-${userId}`);
                newReplyInput.addEventListener('focus', () => {
                    isTyping = true;
                    currentMessageDraft = newReplyInput.value;
                });
                newReplyInput.addEventListener('blur', () => isTyping = false);
                newReplyInput.addEventListener('input', () => currentMessageDraft = newReplyInput.value);
            } catch (error) {
                showNotification('Не удалось загрузить чат', 'error');
            }
        }

        async function handleAction(requestId, action, userId) {
            try {
                const response = await fetch(`${BASE_URL}/action/${requestId}/${action}`, { method: 'POST' });
                if (!response.ok) throw new Error('Ошибка обработки запроса');
                if (action === 'accept') {
                    loadChat(userId, true);
                }
                loadRequests();
            } catch (error) {
                showNotification('Не удалось обработать запрос', 'error');
            }
        }

        async function sendReply(userId) {
            try {
                const replyInput = document.getElementById(`reply-${userId}`);
                const replyText = replyInput.value.trim();
                if (!replyText) {
                    showNotification('Введите текст сообщения', 'error');
                    return;
                }
                const message = {
                    id: Date.now().toString(),
                    sender: 'manager',
                    text: replyText,
                    timestamp: new Date().toLocaleString(),
                    userId
                };
                const response = await fetch(`${BASE_URL}/send_message`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(message)
                });
                if (!response.ok) throw new Error('Ошибка отправки сообщения');
                replyInput.value = '';
                currentMessageDraft = '';
                showNotification('Сообщение отправлено', 'success');
                loadChat(userId);
            } catch (error) {
                showNotification('Не удалось отправить сообщение', 'error');
            }
        }

        function closeChat(userId) {
            const chatContent = document.getElementById('chat-content');
            chatContent.innerHTML = '';
            currentUserId = null;
            currentMessageDraft = '';
            lastMessages = [];
            loadChatList();
            showNotification('Чат закрыт', 'success');
        }

        async function deleteChat(userId) {
            try {
                const response = await fetch(`${BASE_URL}/delete_messages`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ userId })
                });
                if (!response.ok) throw new Error('Ошибка удаления чата');
                const chatContent = document.getElementById('chat-content');
                chatContent.innerHTML = '';
                currentUserId = null;
                currentMessageDraft = '';
                lastMessages = [];
                loadChatList();
                showNotification('Чат удалён', 'success');
            } catch (error) {
                showNotification('Не удалось удалить чат', 'error');
            }
        }

        loadRequests();
        loadChatList();
        if (currentUserId) {
            loadChat(currentUserId);
        }
        setInterval(async () => {
            loadRequests();
            if (currentUserId && !isTyping) {
                try {
                    const response = await fetch(`${BASE_URL}/messages?userId=${currentUserId}`);
                    if (response.ok) loadChat(currentUserId);
                } catch (error) {
                    currentUserId = null;
                    currentMessageDraft = '';
                    lastMessages = [];
                    document.getElementById('chat-content').innerHTML = '';
                    showNotification('Ошибка обновления чата', 'error');
                }
            }
            loadChatList();
        }, 5000);
    </script>
</body>
</html>
'''

@app.route('/')
def login():
    if 'username' in session:
        return redirect(url_for('requests'))
    return render_template_string(LOGIN_TEMPLATE, error=None)

@app.route('/login', methods=['POST'])
def do_login():
    username = request.form['username']
    password = request.form['password']
    if username == VALID_USERNAME and password == VALID_PASSWORD:
        session['username'] = username
        return redirect(url_for('requests'))
    return render_template_string(LOGIN_TEMPLATE, error='Неверный логин или пароль')

@app.route('/requests')
def requests():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template_string(REQUESTS_TEMPLATE)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', 5001)))
