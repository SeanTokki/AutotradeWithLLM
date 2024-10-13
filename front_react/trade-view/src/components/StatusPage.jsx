import React, { useState, useEffect } from "react";
//import api from "../services/api";

function StatusPage() {
    const [status, setStatus] = useState("Loading...");
    const [strategy, setStrategy] = useState("");

    // Initial api request for status checking
    useEffect(() => {
        // api.get("/status")
        //     .then((response) => setStatus(response.data.status))
        //     .catch((error) => console.error(error));
        setTimeout(() => setStatus("Active"), 3000);
    }, []);

    // Request server to start autotrading
    const handleStart = () => {
        // api.post("/start", { strategy })
        //     .then((response) => setStatus(response.data.status))
        //     .catch((error) => console.error(error));
        setStatus("Active");
        alert(`Start Autotrade Program with strategy : ${strategy}`);
        setStrategy("");
    };

    // Request server to stop autotrading
    const handleStop = () => {
        // api.post("/stop")
        //     .then((response) => setStatus(response.data.status))
        //     .catch((error) => console.error(error));
        setStatus("Deactive");
        alert(`Stop Autotrade Program`);
    };

    return (
        <div>
            <h1>Autotrade Status</h1>
            <p>Program status: {status}</p>
            <input
                placeholder="Add new strategy"
                value={strategy}
                onChange={(e) => setStrategy(e.target.value)}
                disabled={status === "Active" || status === "Loading..."}
            />
            <button onClick={handleStart} disabled={status === "Active" || status === "Loading..."}>
                Start
            </button>
            <button onClick={handleStop} disabled={status === "Deactive" || status === "Loading..."}>
                Stop
            </button>
        </div>
    );
}

export default StatusPage;
