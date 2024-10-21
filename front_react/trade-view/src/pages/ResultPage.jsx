import React, { useState, useEffect } from "react";
import api from "../services/api.jsx";
import ResultChart from "../components/ResultChart.jsx";
import ResultTable from "../components/ResultTable.jsx";

function ResultPage() {
    const [profit, setProfit] = useState("0");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        api.get("/profit")
            .then((response) => {
                setProfit(response.data.profit);
                setLoading(false);
            })
            .catch((error) => {
                console.error(error);
                setError("Error fetching data");
            });
    }, []);

    const recLabels = ["id", "timestamp", "decision", "ratio", "reason", "result"];
    const astLabels = ["id", "timestamp", "btc_balance", "btc_avg_price", "btc_price", "krw_balance", "total_asset"];

    return (
        <div>
            <h1>Autotrading Results</h1>
            <h2>Total Return</h2>
            {error ? <p>{error}</p> : loading ? <p>Loading...</p> : <p>{profit}%</p>}
            <h2>Bitcoin Price and Decision Chart</h2>
            <ResultChart />
            <h2>AI Recommendation Table</h2>
            <ResultTable tableName="recommendations" labels={recLabels} />
            <h2>Asset Information Table</h2>
            <ResultTable tableName="asset" labels={astLabels} />
        </div>
    );
}

export default ResultPage;
