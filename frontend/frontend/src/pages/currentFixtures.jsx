import React, { useEffect, useState } from "react";
import "./currentFixtures.css";
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import DashBoard from "../components/dashboard";



function CurrentFixtures() {

  return (
    <main className="mainBody">

      <DashBoard></DashBoard>
      <div className="mainGrid">
        <div className="firstCard">
          <h1>Team Score and Odds</h1>
          <p>
            Lorem ipsum dolor sit amet consectetur adipisicing elit. 
            Repellat non vel quasi quaerat exercitationem provident maxime iusto.
             Veniam laudantium cumque sapiente consequatur repudiandae ea esse adipisci, 
             libero excepturi alias eum dicta perspiciatis beatae nulla quam! Odit, soluta aliquid quos 
             alias temporibus laborum quia voluptate porro eligendi quod libero doloremque quisquam?
          </p>
        </div>

        <div className="secondCard"> 
              <h1>Player Score and Odds</h1>  
        </div>

        <div className="thirdCard">
               <h1>Predictions </h1>               
        </div>

      </div>


    </main>
  );
}

export default CurrentFixtures;