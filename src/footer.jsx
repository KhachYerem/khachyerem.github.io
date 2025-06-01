import React from 'react';
import './main.css';

const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer-content">
        {/* Left Section: Logo and Description */}
        <div className="footer-section">
          <div className="footer-logo">
            <span className="logo-icon">⚖️</span>
            <span className="logo-text">FSSPRU.NET - ПРОВЕРКА ДОЛГОВ</span>
          </div>
          <p>
            FSSPRU.NET Официальный сервис проверки задолженности в базе судебных приставов. Не является официальным сайтом ФССП.
          </p>
          <p>Безопасность операции подтверждена сертификатом международного стандарта PCI DSS.</p>
        </div>

        {/* Middle Section: Site Sections */}
        <div className="footer-section">
          <h3>РАЗДЕЛЫ САЙТА</h3>
          <ul>
            <li>Проверить задолженность физлиц</li>
            <li>Проверить задолженность юрлиц</li>
            <li>Проверить задолженность ИП</li>
            <li>Способы оплаты и проверки</li>
            <li>Контакты</li>
          </ul>
        </div>

        {/* Right Section: Contact Info */}
        <div className="footer-section">
          <p>info@fsspu.net</p>
          <p>ВСЕМ ВОПРОСАМ:</p>
          <p className="phone">8 (800) 350 34 86</p>
          <p>Бесплатная гор. консультация:</p>
          <div className="app-links">
            <a href="#" className="app-link">Доступна</a>
            <a href="#" className="app-link">Загрузить в</a>
            <div className="store-buttons">
              <span className="store-icon">🎮</span> Google Play
              <span className="store-icon">🍎</span> App Store
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Section: Legal Information */}
      <div className="footer-bottom">
        <p>
          Ваши персональные данные защищены согласно приказу № 107 от 14.07.2023 на сайте проверки долгов оператором
          состояния в реестре РКН по номером 36-23-009650
        </p>
        <p>
          Юридическое лицо оператора денежных средств осуществляет ООО НКО «МОБИ.Деньги» (лицензия ЦБ № 3523-К от 06.12.2013 г.)
        </p>
        <div className="footer-links">
          <a href="#">ДОГОВОР ОФЕРТЫ</a>
          <a href="#">ПОЛИТИКА КОНФИДЕНЦИАЛЬНОСТИ</a>
        </div>
      </div>
    </footer>
  );
};

export default Footer;