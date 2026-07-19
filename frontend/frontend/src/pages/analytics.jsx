import React, { useState, useEffect } from "react";
import "./analytics.css";
import axios from 'axios';
import BOS from '../pictures/BOS.png'
import LAL from '../pictures/LAL.png'
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const LOGOS = {
    "Boston Celtics": BOS,
    "Los Angeles Lakers": LAL
}

function GetDBdata({ setData, team1, team2 }) {
    useEffect(() => {
        axios
            .get(`http://127.0.0.1:5000/game-analytics/${team1}/${team2}`)
            .then(res => setData(res.data))
            .catch(err => console.error(err))
    }, [team1, team2])

    return null
}


function GETOddsData({ setTeamData }) {
    useEffect(() => {
        axios
            .get("http://127.0.0.1:5000/getTeamOdds")
            .then(res => {
                const topFive = [...res.data]
                    .sort((a, b) => b.net_rating - a.net_rating)
                    .slice(0, 5);

                setTeamData(topFive);
            })
            .catch(err => console.error(err));
    }, []);

    return null
}


function GETPlayerData({ setPlayerData }) {
    useEffect(() =>{
        axios
        .get("http://127.0.0.1:5000/player-analytics")
        .then(res => setPlayerData(res.data))
        .catch(err => console.error(err))
    }, [])
}


function GETScatterData({ setScatterData }) {
    useEffect(() =>{
        axios
        .get("http://127.0.0.1:5000/scatter-data")
        .then(res => setScatterData(res.data))
        .catch( err => console.log(err))
    }, [])
}


function Analytics() {
    const [data, setData] = useState(null)
    const [getTeamData, setTeamData] = useState([])
    const [playerData, setPlayerData] = useState([])
    const [scatterData, setScatterData] = useState([])
    const selectedTeam = "Boston Celtics"
    const opponent = "Los Angeles Lakers"

    return (
        <main className="mainBody">
            <GetDBdata
                setData={setData}
                team1={selectedTeam}
                team2={opponent}
            />

            <GETOddsData
                setTeamData={setTeamData}
            />

            <GETPlayerData
                setPlayerData={setPlayerData}
            />

            <GETScatterData
             setScatterData={setScatterData}
             />

            <div className="dashboard">
                <div className="topCard">
                    <div className="matchupLayout">

                        {/* Left — selected team */}
                        <div className="selectedTeam">
                            <img src={LOGOS[selectedTeam]} alt={selectedTeam} className="teamLogo" />
                            <p className="teamName">{selectedTeam}</p>
                        </div>

                        {/* Right — fixture + stats */}
                        <div className="fixtureSection">
                            <p className="sectionLabel">Latest Fixture</p>
                            <div className="fixtureHeader">
                                <img src={LOGOS[selectedTeam]} alt={selectedTeam} className="fixtureLogo" />
                                <p className="fixtureTitle">VS</p>
                                <img src={LOGOS[opponent]} alt={opponent} className="fixtureLogo" />
                            </div>

                            {data && (
                                <div className="statsGrid">
                                    <div className="statBox">
                                        <p className="statLabel">Expected Pts</p>
                                        <p className="statValue">{data.expected_points.home.expected_points}</p>
                                    </div>
                                    <div className="statBox">
                                        <p className="statLabel">Pts Allowed</p>
                                        <p className="statValue">{data.expected_points.home.expected_points_allowed}</p>
                                    </div>
                                    <div className="statBox">
                                        <p className="statLabel">Win Prob</p>
                                        <p className="statValue accent">{(data.prediction.probability * 100).toFixed(0)}%</p>
                                    </div>
                                    <div className="statBox">
                                        <p className="statLabel">Player to Watch</p>
                                        <p className="statValue">{data.home_player.name}</p>
                                        <p className="statSub">{data.home_player.pts} pts · {data.home_player.ast} ast · {data.home_player.reb} reb</p>
                                    </div>
                                    <div className="statBox">
                                        <p className="statLabel">Player to Watch (Away)</p>
                                        <p className="statValue">{data.away_player.name}</p>
                                        <p className="statSub">{data.away_player.pts} pts · {data.away_player.ast} ast · {data.away_player.reb} reb</p>
                                    </div>
                                </div>
                            )}
                        </div>

                    </div>
                </div>

                <div className="secondCard">
                    <p className="secondCardTitle sectionLabel">Best Turnover Rates (Net Rating)</p>
                    <table className="ratingTable">
                        <thead>
                            <tr>
                                <th>Rank</th>
                                <th>Team</th>
                                <th>Net Rating</th>
                                <th>Current Elo</th>
                            </tr>
                        </thead>
                        <tbody>
                            {getTeamData.map((team, i) => (
                                <tr key={team.id}>
                                    <td>
                                        <span className={`rankBadge rank-${i + 1}`}>{i + 1}</span>
                                    </td>
                                    <td className="teamCell">{team.team_name}</td>
                                    <td className="ratingCell">{team.net_rating.toFixed(3)}</td>
                                    <td className="ratingCell">{(team.elo_after).toFixed(3)}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                 <div className="thirdCard">

                     <p className="secondCardTitle sectionLabel">Best Players</p>

                    <table className="ratingTable">
                        <thead>
                            <tr>
                                <th>Player ID</th>
                                <th>Player Name</th>
                                <th>Impact rating</th>
                                <th>Production rating</th>
                                <th>Overall rating</th>
                            </tr>
                        </thead>


                    <tbody>

                        {playerData.map((player, i) => (

                            <tr key={player.id}>

                                <td>
                                    <span className={`rankBadge rank-${i + 1}`}>{i + 1}</span>
                                </td>
                                <td className="playerName fontAppearance">{player.name}</td>
                                <td className="impactScore fontStatAppearance">{(player.impact_score * 100).toFixed(2)}</td>
                                <td className="productionScore fontStatAppearance">{(player.production_score * 100).toFixed(2)}</td>
                                <td className="overallScore fontStatAppearance">{(player.overall_score * 100).toFixed(2)}</td>


                            </tr>


  
                        ))}

                    </tbody>



                </table>



                 </div>

                 <div className="fourthCard">

<ResponsiveContainer width="100%" height={350}>
    <ScatterChart margin={{ top: 20, right: 20, bottom: 10, left: 10 }}>
        <CartesianGrid strokeDasharray="3 3" />
<XAxis 
    dataKey="avg_point_scored" 
    type="number" 
    name="Points Scored"
    domain={['dataMin - 2', 'dataMax + 2']}
    tickFormatter={(value) => value.toFixed(0)}
    tick={{ fill: '#8892a4', fontSize: 11 }}
/>
<YAxis 
    dataKey="avg_point_allowed" 
    type="number" 
    name="Points Allowed"
    domain={['dataMin - 2', 'dataMax + 2']}
    tickFormatter={(value) => value.toFixed(0)}
    tick={{ fill: '#8892a4', fontSize: 11 }}
/>
<Tooltip 
    cursor={{ strokeDasharray: '3 3' }}
    content={({ payload }) => {
        if (!payload || !payload.length) return null
        const point = payload[0].payload
        return (
            <div style={{ backgroundColor: '#1e2a3a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', padding: '10px 14px' }}>
                <p style={{ color: '#ffffff', margin: '0 0 4px', fontWeight: 600 }}>{point.team}</p>
                <p style={{ color: '#f97316', margin: 0, fontSize: 13 }}>Points Scored: {point.avg_point_scored.toFixed(1)}</p>
                <p style={{ color: '#00b4d8', margin: 0, fontSize: 13 }}>Points Allowed: {point.avg_point_allowed.toFixed(1)}</p>
            </div>
        )
    }}
/>
        <Scatter data={scatterData} fill="#00b4d8" />
    </ScatterChart>
</ResponsiveContainer>



                 </div>


            </div>
        </main>
    )
}

export default Analytics