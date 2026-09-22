import { Link } from "react-router-dom";

import houseLogo from "../../assets/홈버튼.png";

function Header() {
  return (
    <header className="site-header">
      <Link to="/" className="site-header-logo" aria-label="마냥이 홈으로 이동">
        <img src={houseLogo} alt="" />
      </Link>

      <span className="site-header-name">마냥이</span>
    </header>
  );
}

export default Header;
