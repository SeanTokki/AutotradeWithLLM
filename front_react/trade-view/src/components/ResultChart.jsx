import React, { useState, useEffect } from "react";
import api from "../services/api.jsx";
import { ResponsiveContainer, LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip } from "recharts";
import "./ResultChart.css";

function ResultChart() {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Initial api request for chart data
    useEffect(() => {
        api.get("/chartData")
            .then((response) => {
                setData(response.data.data);
                setLoading(false);
            })
            .catch((error) => {
                console.error(error);
                setError("Error fetching data");
            });
    }, []);

    // Color the dots according to the AI decision
    const CustomizedDot = ({ cx, cy, stroke, payload, value }) => {
        if (payload.decision === "sell") {
            return <circle cx={cx} cy={cy} r={5} fill="red" />;
        } else if (payload.decision === "buy") {
            return <circle cx={cx} cy={cy} r={5} fill="green" />;
        } else {
            return <circle cx={cx} cy={cy} r={5} fill="gray" />;
        }
    };

    // Custom tooltip appears when mouse is on the dot
    const CustomTooltip = ({ active, payload, label }) => {
        if (active && payload && payload.length) {
            const data = payload[0].payload;
            return (
                <div className="custom-tooltip">
                    <p className="main">{`BTC Price : ${data.btc_price.toLocaleString("ko-KR")}￦`}</p>
                    <p className="sub">{`Timestamp: ${data.timestamp}`}</p>
                    <p className="sub">{`AI Decision : ${data.decision.toUpperCase()} ${data.ratio}%`}</p>
                </div>
            );
        }

        return null;
    };

    // Custom X axis format
    const formatXAxis = (xTick) => {
        let [date_tick, time_tick] = xTick.split(/\s+/g);
        return `${time_tick}`;
    };

    // Custom Y axis format
    const formatYAxis = (yTick) => {
        return `${yTick.toLocaleString("ko-KR")}`;
    };

    if (error) return <p>{error}</p>;
    if (loading) return <p>{"Loading..."}</p>;

    return (
        <ResponsiveContainer width="90%" height={300}>
            <LineChart data={data} margin={{ top: 10, right: 10, bottom: 10, left: 25 }}>
                <Line type="monotone" dataKey="btc_price" stroke="#FF8300" strokeWidth={2} dot={<CustomizedDot />} />
                <CartesianGrid strokeDasharray="5 5" />
                <XAxis
                    dataKey="timestamp"
                    strokeWidth={3}
                    tickLine={false}
                    tickFormatter={formatXAxis}
                    tickCount={10}
                    style={{ fontSize: "0.9rem" }}
                />
                <YAxis
                    dataKey="btc_price"
                    type="number"
                    domain={["auto", "auto"]}
                    strokeWidth={3}
                    color="black"
                    tickLine={false}
                    tickFormatter={formatYAxis}
                    style={{ fontSize: "0.9rem" }}
                />
                <Tooltip content={<CustomTooltip />} />
            </LineChart>
        </ResponsiveContainer>
    );
}

export default ResultChart;
