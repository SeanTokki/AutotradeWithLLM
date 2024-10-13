import React from "react";
import { NavLink } from "react-router-dom";
import "./Header.css";

function Header() {
    return (
        <header className="header">
            <nav>
                <NavLink to="/status">Status</NavLink>
                <NavLink to="/result">Result</NavLink>
                <NavLink to="/backtesting">Backtesting</NavLink>
                <NavLink to="/report">Report</NavLink>
            </nav>
        </header>
    );
}

export default Header;
