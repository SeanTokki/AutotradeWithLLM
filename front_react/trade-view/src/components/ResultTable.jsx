import React, { useState, useEffect } from "react";
import api from "../services/api.jsx";
import "./ResultTable.css";

function ResultTable({ tableName, labels }) {
    const [records, setRecords] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        api.get(`/${tableName}`)
            .then((response) => {
                setRecords(response.data[tableName]);
                setLoading(false);
            })
            .catch((error) => {
                console.error(error);
                setError("Error fetching data");
            });
    }, []);

    if (error) return <p>{error}</p>;
    if (loading) return <p>{"Loading..."}</p>;

    return (
        <div className="table-container">
            <table className="table">
                <thead>
                    <tr>
                        {labels.map((label, index) => (
                            <th key={index}>{label}</th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {records.map((row, rowIndex) => (
                        <tr key={rowIndex}>
                            {labels.map((label, colIndex) => (
                                <td key={colIndex}>{row[label]}</td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

export default ResultTable;
