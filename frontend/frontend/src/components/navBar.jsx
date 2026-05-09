import React from "react";
import "./navBar.css";

export default function NavBar({ page, setPage }) {
  return (
    <nav className="navBar">
      <ul className="navLinks">
        <li
          className={page === "home" ? "active" : ""}
          onClick={() => setPage("home")}
        >
          Home
        </li>
        <li
          className={page === "fixtures" ? "active" : ""}
          onClick={() => setPage("fixtures")}
        >
          Current Fixtures
        </li>
        <li
          className={page === "investment" ? "active" : ""}
          onClick={() => setPage("investment")}
        >
          Investment
        </li>
      </ul>
    </nav>
  );
}