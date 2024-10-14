import React, { useState, useEffect, useRef } from "react";
import api from "../services/api.jsx";
import "./statusPage.css";

function StatusPage() {
    const [status, setStatus] = useState("Loading...");
    const [strategy, setStrategy] = useState("");
    const textareaRef = useRef(null);

    // Initial api request for status checking
    useEffect(() => {
        api.get("/status")
            .then((response) => setStatus(response.data.status))
            .catch((error) => console.error(error));
    }, []);

    // Request server to start autotrading
    const handleStart = () => {
        api.post("/start", { strategy })
            .then((response) => {
                setStatus(response.data.status);
                alert(`Start Autotrade Program with strategy : ${strategy}`);
            })
            .catch((error) => console.error(error));
        setStrategy("");
    };

    // Request server to stop autotrading
    const handleStop = () => {
        api.post("/stop").then((response) => {
            setStatus(response.data.status);
            alert(`Stop Autotrade Program`);
        });
    };

    // For resizing and get value of textarea
    const handleChange = (event) => {
        setStrategy(event.target.value);
        textareaRef.current.style.height = "auto";
        textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    };

    return (
        <div className="container">
            <h1>Autotrade Status</h1>
            <p>Program status: {status}</p>
            <div className="input-container">
                <textarea
                    ref={textareaRef}
                    placeholder="Add new strategy"
                    value={strategy}
                    onChange={handleChange}
                    disabled={status === "Active" || status === "Loading..."}
                    rows="1"
                />
                <div className="button-container">
                    <button onClick={handleStart} disabled={status === "Active" || status === "Loading..."}>
                        Start
                    </button>
                    <button onClick={handleStop} disabled={status === "Deactive" || status === "Loading..."}>
                        Stop
                    </button>
                </div>
            </div>
        </div>
    );
}

export default StatusPage;
