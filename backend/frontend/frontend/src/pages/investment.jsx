import React, { useEffect, useState } from "react";
import "./investment.css";
import axios from 'axios';
import { ComposedChart, Scatter, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from "recharts"
import { act } from "react";

// Custom hook instead of component
function useEloData(setActData, setPredData) {
    useEffect(() => {
        axios.get("http://127.0.0.1:5000/elo-trend-line")
            .then((response) => {
                setActData(response.data.actual)
                setPredData(response.data.predicted)
            })
            .catch((error) => {
                console.error("Error fetching ELO data:", error)
            })
    }, [])
}

function Investment() {
    const [actData, setActData] = useState({})
    const [predData, setPredData] = useState({})

    useEloData(setActData, setPredData)

    const predMap = Array.isArray(predData) ? predData.reduce((acc, item) => {
    acc[item.team] = item.trend
    return acc
}, {}) : predData  // if it's already an object, use it directly

const chartData = Object.entries(actData).map(([team, actual]) => ({
    team,
    actual,
    predicted: predMap[team]
}))






    console.log(predData)
    console.log("pred Data")
    console.log(actData)

    return (
        <main>
            <div className="scatterChart">
                <ResponsiveContainer width="100%" height={400}>
    <ComposedChart data={chartData} margin={{ top: 20, right: 20, bottom: 60, left: 10 }}>
        <XAxis
  dataKey="team"
  type="category"
  name="Team"
  tick={{ fill: "#8892a4", fontSize: 11 }}
  angle={-45}
  textAnchor="end"
  height={60}
/>
        <YAxis domain={["auto", "auto"]} tick={{ fill: "#8892a4" }} />
        <Tooltip
            contentStyle={{
                backgroundColor: "#1e2a3a",
                border: "1px solid rgba(255,255,255,0.1)",
                borderRadius: "8px",
                color: "#ffffff"
            }}
        />
        <Legend wrapperStyle={{ color: "#8892a4" }} />
        <Scatter name="Actual ELO" dataKey="actual" fill="#7c8cf8" />
        <Scatter name="Predicted ELO" dataKey="predicted" fill="#4ade80" />
    </ComposedChart>
</ResponsiveContainer>

            </div>
        </main>
    )
}

export default Investment;