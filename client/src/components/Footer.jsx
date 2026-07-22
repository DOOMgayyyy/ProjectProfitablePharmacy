import './Footer.css';

export default function Footer() {
  return (
    <footer className="cp-footer">
      <div className="cp-footer__line" />
      <div className="cp-footer__inner">
        <span className="cp-footer__copy">
          <span className="cp-tag">PHARMA//NET</span> © {new Date().getFullYear()} — агрегатор цен на лекарства
        </span>
        <div className="cp-footer__credits">
          <span>Планета Здоровья</span>
          <span className="sep">|</span>
          <span>Бережная Аптека</span>
          <span className="sep">|</span>
          <span>ГосАптека</span>
        </div>
      </div>
    </footer>
  );
}
