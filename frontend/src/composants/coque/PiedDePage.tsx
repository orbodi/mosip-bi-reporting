import logo from '../../assets/anid-logo.svg';

export function PiedDePage() {
  return (
    <footer className="pied">
      <div className="pied__interieur">
        <div className="pied__marque">
          <img src={logo} alt="ANID, Agence nationale d'identification" className="pied__logo" />
          <span className="pied__app">BI Reporting</span>
        </div>
        <p className="pied__note">Agence nationale d’identification, Togo</p>
      </div>
    </footer>
  );
}
