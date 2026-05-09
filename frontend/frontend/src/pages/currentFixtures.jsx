import React, { useState } from "react";
import barcaLogo from "../pictures/barcelona-logo.png";
import madridLogo from "../pictures/real-madrid-logo.png";
import cityLogo from "../pictures/manchester-city-logo.png";
import "./currentFixtures.css";

// Child component: just a button/div to fetch Barca fixtures
function GetFixture({ teamName, endpoint, logo, setFixtures, setLoading, className, onClick }) {
  const fetchFixtures = async () => {
    setLoading(true);
    try {
      const res = await fetch(endpoint);
      const data = await res.json();
      setFixtures(data.response || []);
    } catch (err) {
      console.log(err);
    } finally {
      setLoading(false);
    }
  };

  return (
   <div
  className={className}
  onClick={() => {
    fetchFixtures();   // fetch the data
    onClick?.();       // hide top cards
  }}
>
      <img src={logo} alt={teamName} className="teamLogo" />
      <p>{teamName}</p>
      <p>Click and get to know about your team</p>
    </div>
  );
}
// Parent component: renders everything
function CurrentFixtures() {
  const [fixtures, setFixtures] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showTopCards, setShowTopCards] = useState(true);

const teams = [
  {
    name: "Barcelona",
    endpoint: "http://localhost:5000/api/barca-fixtures",
    logo: barcaLogo
  },
  {
    name: "Real Madrid",
    endpoint: "http://localhost:5000/api/madrid-fixtures",
    logo: madridLogo
  },
  {
    name: "Man City",
    endpoint: "http://localhost:5000/api/city-fixtures",
    logo: cityLogo
  },
];

  return (
    <div className="fixturesWrapper">
  <h2>Current Fixtures of Clubs</h2>

  {loading && <p className="loading">Loading current fixtures…</p>}

{showTopCards && (
  <div className="fixturesGrid">
    {teams.map((team) => (
      <GetFixture
        key={team.name}
        teamName={team.name}
        endpoint={team.endpoint}
        logo={team.logo}
        setFixtures={setFixtures}
        setLoading={setLoading}
        onClick={() => setShowTopCards(false)} 
        className="fixtureCard"
      />
    ))}
  </div>
)}

  {/* FIXTURES */}

<div className="fixturesGrid"> 
{fixtures.map((match) => (
  <div key={match.fixture.id} className="fixtureCard">
    <div className="teamsRow">
      <div className="team">
        <img src={match.teams.home.logo} alt={match.teams.home.name} className="teamLogo" />
        <p>{match.teams.home.name}</p>
      </div>

      <p className="score">
        {match.goals.home} - {match.goals.away}
      </p>

      <div className="team">
        <img src={match.teams.away.logo} alt={match.teams.away.name} className="teamLogo" />
        <p>{match.teams.away.name}</p>
      </div>
    </div>

    <p className="status">{match.fixture.status.short}</p>
    <p className="date">{new Date(match.fixture.date).toLocaleString()}</p>
  </div>
))}
</div>
</div>
    
  );
}

export default CurrentFixtures;