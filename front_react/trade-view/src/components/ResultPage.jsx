import React, { useState, useEffect } from "react";
import ResultChart from "./ResultChart.jsx";
import "./ResultPage.css";

function ResultPage() {
    const [records, setRecords] = useState([]);
    const [profit, setProfit] = useState("0");

    useEffect(() => {
        // api.get("/result")
        //     .then((response) => setRecords(response.data.records))
        //     .then((response) => setProfit(response.data.profit))
        //     .catch((error) => console.error(error));

        setRecords([
            {
                id: "1",
                date: "2024-01-01",
                decision: "buy",
                ratio: "0.3",
                reason: "I just wanted to buy...",
                result: "success",
            },
            {
                id: "2",
                date: "2024-01-02",
                decision: "sell",
                ratio: "0.1",
                reason: "I just wanted to sell...",
                result: "success",
            },
            {
                id: "3",
                date: "2024-01-03",
                decision: "sell",
                ratio: "0.1",
                reason: "I just wanted to sell...",
                result: "success",
            },
            {
                id: "4",
                date: "2024-01-04",
                decision: "sell",
                ratio: "0.1",
                reason: "I just wanted to sell...",
                result: "success",
            },
        ]);

        setProfit("3")
    }, []);

    return (
        <div>
            <h1>Autotrading Results</h1>
            <h2>Total Return</h2>
            <h3>{profit}%</h3>
            <h2>Bitcoin Price Chart</h2>
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
                                <td>{record.date}</td>
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
