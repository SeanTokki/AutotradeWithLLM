import React, { useState, useEffect } from "react";
import api from "../services/api.jsx";
import "./ResultTable.css";

function ResultTable() {
    const [records, setRecords] = useState([
        {
            decision: "none",
            id: 0,
            ratio: 0,
            reason: "no reason",
            result: "FAIL",
            timestamp: "2024-01-01 00:00:00",
        },
    ]);

    useEffect(() => {
        api.get("/recommendations")
            .then((response) => setRecords(response.data.recommendations))
            .catch((error) => console.error(error));
    }, []);

    return (
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
    );
}

export default ResultTable;
