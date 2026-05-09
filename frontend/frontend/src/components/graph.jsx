import React, { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import "./graph.css";

export default function Graph() {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetch("http://localhost:5000/api/barca-betting")  // your backend endpoint
      .then((res) => res.json())
      .then((json) => {
        // add game_day to each match
        const daysWithGameDay = json.map((match, index) => ({
          ...match,
          game_day: index + 1
        }));
        setData(daysWithGameDay);
      })
      .catch((err) => console.error(err));
  }, []);

  return (
    <div className="Graph">
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
         <XAxis
            dataKey="game_day"
          interval={4} // show every 5th tick (0, 5, 10, …)
         stroke="#fff"
         />
          <YAxis label={{ value: "Money", angle: -90, position: "insideLeft" }} />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="current_money" stroke="#8884d8" activeDot={{ r: 8 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}