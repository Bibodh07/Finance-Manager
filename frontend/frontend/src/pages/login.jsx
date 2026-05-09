import React, { useState, useRef } from "react";
import "./login.css";

function Login({ loggedIn, setLoggedIn }) {
    const userName = useRef(null);
    const password = useRef(null);

    const [loginStatus, setLoginStatus] = useState(null);

    const loginVerif = async () => {
        try {
            const res = await fetch("http://127.0.0.1:5000/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    username: userName.current.value,
                    password: password.current.value
                })
            });

            const data = await res.json();
            console.log(data);

            if (data.successStatus) {
                setLoginStatus(true);
                setLoggedIn(true)
            } else {
                setLoginStatus(false);
            }


            

        } catch (err) {
            console.log(err);
            setLogInStatus(false);
        }
    };

    function handleVerification() {
        console.log(userName.current.value);
        console.log(password.current.value);

        if (userName.current.value && password.current.value) {
            loginVerif();
        }
    }

    return (
        <div className="container">
  <div className="card">
    <h1>Welcome Back</h1>

    <input ref={userName} type="text" placeholder="Username" className="input" />
    <input ref={password} type="password" placeholder="Password" className="input" />

    <button onClick={handleVerification} className="btn">
      Login
    </button>

    {loginStatus === true && <p className="success">Login Successful 🚀</p>}
    {loginStatus === false && <p className="error">Invalid credentials ❌</p>}
  </div>
</div>
    );
}

export default Login;