import React, { useState } from "react";
import NavBar from "./components/navBar";
import CurrentFixtures from "./pages/currentFixtures";
import Home from "./pages/home";
import Investments from "./pages/investments";
import Login from  "./pages/login";

function App() {

  const [loggedIn, setLoggedIn] = useState(false)
  const [page, setPage] = useState("home"); // track current page

  

  return (
    <div>

    


      {loggedIn ? (

        <div>
    
      
      <NavBar page={page} setPage={setPage} />

      {page === "home" && <Home />}
      {page === "fixtures" && <CurrentFixtures />}
      {page === "investment" && <Investments />}

      </div>

      ) : (

        <Login loggedIn={loggedIn} setLoggedIn={setLoggedIn} />

      )}

  

    </div>
  );
}

export default App;