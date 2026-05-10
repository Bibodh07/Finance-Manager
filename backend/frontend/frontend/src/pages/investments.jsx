import "./investments.css";
import React, { useState, useEffect } from "react";

function Investments() {
  const [principal, setPrincipalAmount] = useState("");
  const [team, setTeam] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const [selectedTeam, setSelectedTeam] = useState(null);

   const isReady = principal && selectedTeam;

   const handleInvestment = async () => {
        try {
            const res = await fetch("http://127.0.0.1:5000/add/userInvestment", {
            method: "POST",
            headers: {
                    "Content-Type": "application/json"
                },
            body: JSON.stringify({
            amount: principal,
            teamid: selectedTeam[0],      // or selectedTeam.teamid
            teamname: selectedTeam[2]     // optional
            })
        });

    const data = await res.json();

    console.log("🔥 Button clicked");
    console.log("principal:", principal);
    console.log("selectedTeam:", selectedTeam);
    console.log("isReady:", isReady);
    console.log("response:", data);

  } catch (err) {
    console.log(err);
    console.log(t)
  }
};

  const teamsForDropDown = async () => {
    try {
      const res = await fetch("http://127.0.0.1:5000/get/investment-team");
      const data = await res.json();
      setTeam(data || []);
    } catch (err) {
      console.log(err);
    }
  };

  useEffect(() => {
    if (isOpen) {
      teamsForDropDown();
    }
  }, [isOpen]);

  return (
    <div className="mainBody">

      <input
        className="searchBar"
        type="text"
        placeholder="$"
        value={principal}
        onChange={(e) => setPrincipalAmount(e.target.value)}
      />

      <div className={`DropDown ${isOpen ? "open" : ""}`}>

        {/* header */}
        <div
          className="selected"
          onClick={() => setIsOpen(!isOpen)}
        >
          {selectedTeam ? selectedTeam[2] : "Select team"}
        </div>

        {/* list */}
        {isOpen && (
          <div className="dropdownList">
            {team.map((t) => (
              <div
                key={t[0]}
                className="dropdownItem"
                onClick={() => {
                  setSelectedTeam(t);
                  setIsOpen(false);
                }}
              >
                {t[2]}
              
              </div>
            ))}
          </div>
        )}

      </div>
     
      <input
        className="searchButton"
        type="button"
        value="Confirm"
        onClick={handleInvestment}
        disabled={!isReady}
                        
      />




    </div>
  );
}

export default Investments;