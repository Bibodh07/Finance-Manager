import React, { useState } from "react";
import NavBar from "./components/navBar";
import CurrentFixtures from "./pages/currentFixtures";

function App() {
  const [page, setPage] = useState("fixtures");

  const background = page === "fixtures" 
    ? "black" 
    : "linear-gradient(135deg, #1a1a2e, #16213e, #0f3460)";

  return (
    <div style={{ minHeight: "100vh", background }}>
      <NavBar page={page} setPage={setPage} />
      {page === "fixtures" && <CurrentFixtures />}
    </div>
  );
}

export default App;