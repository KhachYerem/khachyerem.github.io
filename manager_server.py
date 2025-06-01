from flask import Flask, request, render_template_string, redirect, url_for, session
from flask_cors import CORS
import requests


app = Flask(__name__)
CORS(app)
app.secret_key = 'your_secret_key_here'

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
        input { padding: 5px; width: 265px;   padding: 12px 16px; border: 1px solid #ccd1d5; border-radius: 4px; font-size: 16px; color: #364b66; background-color: white; transition: border-color 0.3s ease; margin-bottom: 15px }
        button { padding: 5px 10px; cursor: pointer; font-size: 18px; font-weight: bold; border: 1px solid #2862AC; color: #2862AC; border-radius: 4px; height: 48px; width: 100%; transition: background-color 0.3s ease; background-color: #ffffff; }
        label { color: #7c7c7d; font-size: 14px; }
        button:hover{ background-color: #2862AC; color: #ffffff; }
        h2{ margin-left: 14px; }
    </style>
</head>
<body>
    <div className="login-box">
        <h2>Вход для менеджеров</h2>
        {% if error %}
            <p style="color: red;">{{ error }}</p>
        {% endif %}
        <form method="POST" action="/login">
            <div className="form-group">
                <label>Логин:</label><br>
                <input type="text" name="username" required>
            </div>
            <div className="form-group">
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
        .request { border: 1px solid #ccc; padding: 10px; margin: 10px 0; border-radius: 5px; }
        .chat-message { border: 1px solid #ddd; padding: 10px; margin: 10px 0; border-radius: 5px; }
        .buttons { margin-top: 10px; }
        button { padding: 5px 10px; margin-right: 10px; cursor: pointer; }
        .accepted { background-color: #d4edda; }
        .rejected { background-color: #f8d7da; }
        .logout { margin-top: 20px; }
        .chat-input { display: flex; gap: 10px; margin-top: 10px; }
        input { padding: 5px; width: 265px;   padding: 12px 16px; border: 1px solid #ccd1d5; border-radius: 4px; font-size: 16px; color: #364b66; background-color: white; transition: border-color 0.3s ease; margin-bottom: 15px } }
        .chat-input button { padding: 5px 10px; }
        button { padding: 5px 10px; cursor: pointer; font-size: 18px; font-weight: bold; border: 1px solid #2862AC; color: #2862AC; border-radius: 4px; height: 43px; width: 330px; transition: background-color 0.3s ease; background-color: #ffffff; }   
        button:hover{ background-color: #2862AC; color: #ffffff; }

        
    </style>
</head>
<body>
    <h1>Список запросов</h1>
    <div id="requests"></div>
    <h1>Чат с пользователями</h1>
    <div id="chat"></div>
    <div className="logout">
        <button onclick="window.location.href='/logout'">Выйти</button>
    </div>

    <script>
        async function loadRequests() {
            const response = await fetch('http://localhost:5000/requests');
            const requests = await response.json();
            const container = document.getElementById('requests');
            container.innerHTML = '';
            const pendingRequests = requests.filter(req => req.status === 'pending');
            pendingRequests.forEach((req, index) => {
                const div = document.createElement('div');
                div.className = `request ${req.status}`;
                div.innerHTML = `<strong>Запрос №${index + 1}</strong><br>
                    Страна: ${req.country === 'RF' ? 'РФ' : 'Беларусь'}<br>
                    ФИО: ${req.fullName}<br>
                    Email: ${req.email}<br>
                    Гражданство: ${req.citizenship}<br>
                    Тип документа: ${req.documentType}<br>
                    Номер документа: ${req.documentNumber}<br>
                    Дата действительности документа: ${req.validityDate}<br>
                    Пол: ${req.gender || 'Не указан'}<br>
                    Дата рождения: ${req.dob}<br>
                    Время отправки: ${req.timestamp}<br>
                    Статус: ${req.status === 'pending' ? 'Ожидает' : req.status === 'accept' ? 'Принят' : 'Отклонён'}<br>
                    <div className="buttons">
                        <button onclick="handleAction('${req.id}', 'accept')">Принять</button>
                        <button onclick="handleAction('${req.id}', 'reject')">Отклонить</button>
                    </div>`;
                container.appendChild(div);
            });
        }

        async function loadMessages() {
            const response = await fetch('http://localhost:5000/messages');
            const messages = await response.json();
            const container = document.getElementById('chat');
            container.innerHTML = '';
            messages.forEach(msg => {
                const div = document.createElement('div');
                div.className = 'chat-message';
                div.innerHTML = `
                    <strong>${msg.sender === 'user' ? 'Пользователь' : 'Менеджер'}</strong><br>
                    Сообщение: ${msg.text}<br>
                    Время: ${msg.timestamp}<br>
                    ${msg.sender === 'user' ? `
                    <div className="chat-input">
                        <input type="text" id="reply-${msg.id}" placeholder="Введите ответ...">
                        <button onclick="sendReply('${msg.id}')">Отправить</button>
                    </div>` : ''}
                `;
                container.appendChild(div);
            });
        }

        async function handleAction(requestId, action) {
            await fetch(`http://localhost:5000/action/${requestId}/${action}`, { method: 'POST' });
            loadRequests();
        }

        async function sendReply(messageId) {
            const replyInput = document.getElementById(`reply-${messageId}`);
            const replyText = replyInput.value;
            if (!replyText.trim()) return;

            const message = {
                id: Date.now().toString(),
                sender: 'manager',
                text: replyText,
                timestamp: new Date().toLocaleString('ru-RU', {
                    day: '2-digit',
                    month: '2-digit',
                    year: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                }).replace(',', '')
            };

            await fetch('http://localhost:5000/send_message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(message)
            });
            replyInput.value = '';
            loadMessages();
        }

        loadRequests();
        loadMessages();
        setInterval(loadRequests, 10000);
        setInterval(loadMessages, 5000);
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
    app.run(debug=True, host='0.0.0.0', port=5001)