import React, { useEffect, useState } from "react";
import "./currentFixtures.css";
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function GetTeamEloData({ setData }) {
  useEffect(() => {
    axios
      .get("http://127.0.0.1:5000/current-market-data")
      .then((response) => {
        setData(response.data);
      })
      .catch((err) => {
        console.log(err);
      });
  }, []);

  return null;
}


function GetGraphData({setgraphData, team}){

    useEffect (() =>{

      axios.
              get(`http://127.0.0.1:5000/elo/${team}`)
            .then((response) =>{
              setgraphData(response.data)
            })
            .catch( (err) =>{
              console.log(err)
            })
 

    }, [team]);

    return null;


}

function CurrentFixtures() {
  const [data, setData] = useState([]);
  const [graphData, setgraphData] = useState([])
  const [selectedTeam, setSelectedTeam] = useState("BOS");

  const getRowClass = (elo) => {
  if (elo >= 1600) return "row-green";
  if (elo >= 1400) return "row-yellow";
  return "row-red";
  };

  return (
    <main className="mainBody">
      <GetTeamEloData setData={setData} />
      <div className="tableWrapper">
      <table className="team-elo-table">
      <thead>
        <tr>
          <th>Team</th>
          <th>Starting Elo</th>
          <th>Current Elo</th>
          <th>PI</th>
        </tr>
       </thead>
       <tbody>
          {data.map((team) => {
              const diff = (team.current_elo - team.starting_elo).toFixed(1);
              const isPositive = diff >= 0;
              return (
                  <tr key={team.team} className={getRowClass(team.current_elo)}>
                    <td>{team.team}</td>
                    <td>{team.starting_elo.toFixed(1)}</td>
                    <td>{team.current_elo.toFixed(1)}</td>
                    <td className={isPositive ? "positive" : "negative"}>
                        {isPositive ? "+" : ""}{diff}
                    </td>
                  </tr>
    );
  })}
          </tbody>
      </table>
      </div>

      <GetGraphData setgraphData={setgraphData} team={selectedTeam} />
      
      <div className="graphWrapper">
        <p className="chartTitle">{selectedTeam} — Elo History</p>
        <ResponsiveContainer width="100%" height={400}>
        <LineChart data={graphData} margin={{ top: 10, right: 20, left: 10, bottom: 10 }}>
             <CartesianGrid strokeDasharray="3 3" stroke="#1a1a2e" />
<XAxis
  dataKey="game_id"
  stroke="#00b4d8"
  tick={{ fill: '#00b4d8', fontSize: 11 }}
  label={{ value: 'Game', position: 'insideBottom', fill: '#00b4d8', offset: -2 }}
/>
<YAxis
  domain={['auto', 'auto']}
  stroke="#00b4d8"
  tick={{ fill: '#00b4d8', fontSize: 11 }}
  tickFormatter={(value) => value.toFixed(0)}
  label={{ value: 'Elo', angle: -90, position: 'insideLeft', fill: '#00b4d8' }}
/>
<Tooltip
  contentStyle={{ backgroundColor: '#0d0d0d', border: '1px solid #f97316', color: '#f97316', fontFamily: 'Ubuntu Mono' }}
  labelStyle={{ color: '#00b4d8' }}
  formatter={(value) => [value.toFixed(1), 'Elo']}
/>
<Line
  type="monotone"
  dataKey="elo"
  stroke="#f97316"
  strokeWidth={2}
  dot={{ fill: '#f97316', r: 3 }}
  activeDot={{ fill: '#ffffff', r: 5 }}
/>
              </LineChart>
        </ResponsiveContainer>
      </div>

    </main>
  );
}

export default CurrentFixtures;