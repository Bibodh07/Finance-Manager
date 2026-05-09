import "./home.css";
import React, { useState, useEffect } from "react"; // ✅ include useEffect
import Graph from "../components/graph";


function GetInvestments({ setInvestmentData, setLoading }) {
  useEffect(() => {
    const fetchInvestments = async () => {
      setLoading(true);
      try {
        const res = await fetch('http://localhost:5000/get/user-investments');
        const data = await res.json();
        setInvestmentData(data || []);
        console.log(data)
    
      } catch (err) {
        console.log(err);
      } finally {
        setLoading(false);
      }
    };
    fetchInvestments();
  }, []); 

  return null; // no visible UI
}




function Home() {
    const [stateDisplay, showStateInfo] = useState(false)
    const [investmentData, setInvestmentData] = useState([])
    const [loading, setLoading] = useState(true)
    
  return (
    <div className="homeWrapper">
        <div className="graph">
        <Graph />
        </div>  


        <div className={`investmentBoard ${stateDisplay ? "close" : ""}`}
           onClick={() => showStateInfo(true)}>   
                          View your investments
                          </div>
       
        { stateDisplay && (
            <div className= "dropDown"
            onClick={ () => {
                
               showStateInfo(false)
              
            }
            }>
                
            <GetInvestments
                setInvestmentData={setInvestmentData}
                setLoading={setLoading}
            />
            

            {loading ? (
                <p>Loading investments…</p>
                ) : investmentData.length === 0 ? (
                 <p>No investments yet</p>
                ) : (

                <div>
                    <p>View your investments</p>
                 {investmentData.map((inv) => {
  
                    const invested = parseFloat(inv[3]);
                    const current = parseFloat(inv[5]);
                    const isProfit = current > invested;

  
                    return (
                        
                        <div key={inv[0]} className="investmentItem">
                        <p><strong>Name:</strong> {inv[2]}</p>
                        <p><strong>Invested Amount:</strong> ${inv[3]}</p>
                        <p><strong>Date:</strong> {new Date(inv[4]).toLocaleDateString()}</p>

                        <p style={{ color: isProfit ? "green" : "red" }}>
                 <strong>Current Amount:</strong> ${inv[5]}
                </p>
                 </div>
                );
            })}

                </div>
                    
        )}

              </div>
             
    )}
         
       
  
    </div>
  );
} export default Home;