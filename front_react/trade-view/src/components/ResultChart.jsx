import React, { useState, useEffect } from "react";
import api from "../services/api.jsx";
import { ResponsiveContainer, LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip } from "recharts";
import "./ResultChart.css";

const ResultChart = () => {
    const [data, setData] = useState([]);

    // Initial api request for chart data
    useEffect(() => {
        api.get("/chartData")
            .then((response) => setData(response.data.data))
            .catch((error) => console.error(error));
    }, []);

    const CustomizedDot = ({ cx, cy, stroke, payload, value }) => {
        if (payload.decision === "sell") {
            return <circle cx={cx} cy={cy} r={5} fill="green" />;
        } else if (payload.decision === "buy") {
            return <circle cx={cx} cy={cy} r={5} fill="red" />;
        } else {
            return <circle cx={cx} cy={cy} r={5} fill="gray" />;
        }
    };

    const CustomTooltip = ({ active, payload, label }) => {
        if (active && payload && payload.length) {
            const data = payload[0].payload;
            return (
                <div className="custom-tooltip">
                    <p className="main">{`BTC Price : ${data.btc_price.toLocaleString("ko-KR")}￦`}</p>
                    <p className="sub">{`Timestamp: ${data.timestamp}`}</p>
                    <p className="sub">{`AI Decision : ${data.decision.toUpperCase()} ${data.ratio * 100}%`}</p>
                </div>
            );
        }

        return null;
    };

    return (
        <ResponsiveContainer width="90%" height={300}>
            <LineChart data={data} margin={{ top: 10, right: 10, bottom: 10, left: 10 }}>
                <Line type="monotone" dataKey="btc_price" stroke="black" dot={<CustomizedDot />} />
                <CartesianGrid strokeDasharray="5 5" />
                <XAxis dataKey="timestamp" />
                <YAxis dataKey="btc_price" type="number" domain={["auto", "auto"]} />
                <Tooltip content={<CustomTooltip />} />
            </LineChart>
        </ResponsiveContainer>
    );
};

export default ResultChart;
