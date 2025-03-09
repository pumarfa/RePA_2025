import { useEffect, useState } from "react";

import UserBox from "./components/UsersBox";
import CreateUser from "./components/CreateUser";

import logo from "./logo.svg";
import "./App.css";

function App() {
  useEffect(() => {
    fetch("http://localhost:8000/users/")
      .then((res) => res.json())
      .then((res) => console.log(res));
  }, []);
  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Edit <code>src/App.js</code> and save to reload...
        </p>
      </header>
    </div>
  );
}

export default App;
