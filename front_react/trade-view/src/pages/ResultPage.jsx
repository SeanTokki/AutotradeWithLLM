import React, { useState, useEffect } from "react";
import api from "../services/api.jsx";
import ResultChart from "../components/ResultChart.jsx";
import ResultTable from "../components/ResultTable.jsx";

function ResultPage() {
    const [records, setRecords] = useState([]);
    const [profit, setProfit] = useState("0");

    useEffect(() => {
        api.get("/profit")
            .then((response) => setProfit(response.data.profit))
            .catch((error) => console.error(error));
    }, []);

    return (
        <div>
            <h1>Autotrading Results</h1>
            <h2>Total Return</h2>
            <p>{profit}%</p>
            <h2>Bitcoin Price and Decision Chart</h2>
            <ResultChart />
            <h2>AI Recommendation Table</h2>
            <ResultTable />
        </div>
    );
}

export default ResultPage;
