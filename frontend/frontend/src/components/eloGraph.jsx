import React, { useState, useEffect } from "react";
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import "./eloGraph.css";

function EloGraph( {team} ) {

    const[graphData, setgraphData] = useState([])

    useEffect(() =>{
        axios
            .get(`http://127.0.0.1:5000/elo/${team}`)
            .then(res => setgraphData(res.data))
            .catch(err => console.log(err))
    }, [team])


    return (
        <main>
            <div className="graphWrapper">
                 <p className="chartTitle">{team} — Elo History</p>
                    <ResponsiveContainer width="100%" height={400}>

                        <LineChart data={graphData} margin={{ top: 10, right: 20, left: 10, bottom: 10 }}>
                        <CartesianGrid
                            stroke="rgba(255,255,255,0.08)"
                            strokeDasharray="4 4"
                        />

                        <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="game_id" stroke="#00b4d8" tick={{ fill: '#00b4d8', fontSize: 11 }} label={{ value: 'Game', position: 'insideBottom', fill: '#00b4d8', offset: -2 }}></XAxis>
                            <YAxis domain={['auto', 'auto']} stroke="#00b4d8" tick={{ fill: '#00b4d8', fontSize: 11 }} tickFormatter={(value) => value.toFixed(0)} label={{ value: 'Elo', angle: -90, position: 'insideLeft', fill: '#00b4d8'}}></YAxis>
                            <Tooltip contentStyle={{ backgroundColor: '#0d0d0d', border: '1px solid #f97316', color: '#f97316', fontFamily: 'Ubuntu Mono' }} labelStyle={{ color: '#00b4d8' }} formatter={(value) => [value.toFixed(1), 'Elo']} />
                            <Line type="monotone" dataKey="elo" stroke="#f97316" strokeWidth={2} dot={{ fill: '#f97316', r: 3 }} activeDot={{ fill: '#ffffff', r: 5 }} />
                            <Line type="monotone" dataKey="predicted" stroke="#7c8cf8" strokeWidth={2} dot={false} strokeDasharray="5 5" name="Predicted ELO" />  
                        </LineChart>
                    </ResponsiveContainer>
            </div>
        </main>
    );
}

export default EloGraph;