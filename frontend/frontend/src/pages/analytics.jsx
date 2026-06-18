import React, { useEffect, useState } from "react";
import "./analytics.css";
import axios from 'axios';

function Analytics() {
    const [teamStat, setteamStat] = useState({})
    const [isB2B, setisB2B] = useState([])
    const [sortKey, setSortKey] = useState("elo")
    const [sortDir, setSortDir] = useState("desc")

    useEffect(() => {
        axios.get("http://127.0.0.1:5000/team-stats")
            .then(res => setteamStat(res.data))
            .catch(err => console.error(err))

        axios.get("http://127.0.0.1:5000/team-b2b")
            .then(res => setisB2B(res.data))
            .catch(err => console.error(err))
    }, [])

    const b2bMap = isB2B.reduce((acc, item) => {
        acc[item.team] = item.b2b_count
        return acc
    }, {})

    const tableData = Object.entries(teamStat).map(([team, stats]) => ({
        team,
        winPct: ((stats.total_wins / stats.games_played) * 100).toFixed(1),
        homeRecord: `${stats.home_wins}-${stats.home_games - stats.home_wins}`,
        awayRecord: `${stats.away_wins}-${stats.away_games - stats.away_wins}`,
        form: `${stats.last_10_wins}/10`,
        netRating: stats.avg_point_diff.toFixed(1),
        elo: stats.elo.toFixed(1),
        b2b: b2bMap[team] || 0
    }))

    const sorted = [...tableData].sort((a, b) => {
        const aVal = parseFloat(a[sortKey])
        const bVal = parseFloat(b[sortKey])
        return sortDir === "desc" ? bVal - aVal : aVal - bVal
    })

    const handleSort = (key) => {
        if (sortKey === key) setSortDir(sortDir === "desc" ? "asc" : "desc")
        else { setSortKey(key); setSortDir("desc") }
    }

    const eloSorted = [...tableData].sort((a, b) => parseFloat(b.elo) - parseFloat(a.elo))
    const b2bSorted = [...isB2B].sort((a, b) => b.b2b_count - a.b2b_count)

    return (
        <main className="mainBody">
            <p className="chartTitle">Team Analytics</p>

            {/* Full width stats table */}
            <div className="analyticsSection">
                <p className="cardTitle">Team Stats</p>
                <p className="cardSubtitle">Click headers to sort</p>
                <div className="tableWrapper">
                    <table className="team-elo-table">
                        <thead>
                            <tr>
                                <th onClick={() => handleSort("team")}>Team</th>
                                <th onClick={() => handleSort("winPct")}>Win %</th>
                                <th>Home</th>
                                <th>Away</th>
                                <th onClick={() => handleSort("form")}>Form</th>
                                <th onClick={() => handleSort("netRating")}>Net Rtg</th>
                                <th onClick={() => handleSort("elo")}>
                                    ELO {sortKey === "elo" ? (sortDir === "desc" ? "↓" : "↑") : ""}
                                </th>
                                <th onClick={() => handleSort("b2b")}>B2Bs</th>
                            </tr>
                        </thead>
                        <tbody>
                            {sorted.map((row) => (
                                <tr key={row.team}>
                                    <td>{row.team}</td>
                                    <td>{row.winPct}%</td>
                                    <td>{row.homeRecord}</td>
                                    <td>{row.awayRecord}</td>
                                    <td>{row.form}</td>
                                    <td className={parseFloat(row.netRating) >= 0 ? "positive" : "negative"}>
                                        {parseFloat(row.netRating) >= 0 ? "+" : ""}{row.netRating}
                                    </td>
                                    <td className={parseFloat(row.elo) >= 1600 ? "positive" : parseFloat(row.elo) >= 1400 ? "neutral" : "negative"}>
                                        {row.elo}
                                    </td>
                                    <td>{row.b2b}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Two column bottom section */}
            <div className="bottomGrid">

                <div className="analyticsSection">
                    <p className="cardTitle">ELO Rankings</p>
                    <div className="tableWrapper">
                        <table className="team-elo-table">
                            <thead>
                                <tr>
                                    <th>#</th>
                                    <th>Team</th>
                                    <th>ELO</th>
                                </tr>
                            </thead>
                            <tbody>
                                {eloSorted.map((row, i) => (
                                    <tr key={row.team}>
                                        <td>{i + 1}</td>
                                        <td>{row.team}</td>
                                        <td className={parseFloat(row.elo) >= 1600 ? "positive" : parseFloat(row.elo) >= 1400 ? "neutral" : "negative"}>
                                            {row.elo}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                <div className="analyticsSection">
                    <p className="cardTitle">B2B Report</p>
                    <div className="tableWrapper">
                        <table className="team-elo-table">
                            <thead>
                                <tr>
                                    <th>#</th>
                                    <th>Team</th>
                                    <th>B2Bs</th>
                                </tr>
                            </thead>
                            <tbody>
                                {b2bSorted.map((row, i) => (
                                    <tr key={row.team}>
                                        <td>{i + 1}</td>
                                        <td>{row.team}</td>
                                        <td className={row.b2b_count >= 16 ? "negative" : row.b2b_count >= 14 ? "neutral" : "positive"}>
                                            {row.b2b_count}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

            </div>
        </main>
    )
}

export default Analytics;