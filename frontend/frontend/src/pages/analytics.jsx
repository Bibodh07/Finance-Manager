import React, { useState, useEffect } from "react";
import "./analytics.css";
import axios from 'axios';
import BOS from '../pictures/BOS.png'
import LAL from '../pictures/LAL.png'

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

function Analytics() {
    const [data, setData] = useState(null)
    const [getTeamData, setTeamData] = useState([])
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
                            </tr>
                        </thead>
                        <tbody>
                            {getTeamData.map((team, i) => (
                                <tr key={team.id}>
                                    <td>
                                        <span className={`rankBadge rank-${i + 1}`}>{i + 1}</span>
                                    </td>
                                    <td className="teamCell">{team.team_name}</td>
                                    <td className="ratingCell">{team.net_rating.toFixed(1)}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                 <div className="thirdCard"> 

                 </div>

                 <div className="fourthCard">

                 </div>


            </div>
        </main>
    )
}

export default Analytics