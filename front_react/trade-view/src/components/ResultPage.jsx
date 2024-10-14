import React, { useState, useEffect } from "react";
import api from "../services/api.jsx";
import ResultChart from "./ResultChart.jsx";
import "./ResultPage.css";

function ResultPage() {
    const [records, setRecords] = useState([]);
    const [profit, setProfit] = useState("0");

    useEffect(() => {
        api.get("/recommendations")
            .then((response) => setRecords(response.data.recommendations))
            .catch((error) => console.error(error));

        api.get("/profit")
            .then((response) => setProfit(response.data.profit))
            .catch((error) => console.error(error));
    }, []);

    return (
        <div>
            <h1>Autotrading Results</h1>
            <h2>Total Return</h2>
            <h3>{profit}%</h3>
            <h2>Bitcoin Price and Decision Chart</h2>
            <ResultChart />
            <h2>AI Recommendation Table</h2>
            <div className="table-container">
                <table className="table">
                    <thead>
                        <tr>
                            <th>id</th>
                            <th>timestamp</th>
                            <th>decision</th>
                            <th>ratio</th>
                            <th>reason</th>
                            <th>result</th>
                            {/* 기타 항목 */}
                        </tr>
                    </thead>
                    <tbody>
                        {records.map((record, index) => (
                            <tr key={index}>
                                <td>{record.id}</td>
                                <td>{record.timestamp}</td>
                                <td>{record.decision}</td>
                                <td>{record.ratio}</td>
                                <td>{record.reason}</td>
                                <td>{record.result}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

export default ResultPage;
