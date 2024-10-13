import React, { useState, useEffect } from "react";
import { LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip } from "recharts";
import "./ResultChart.css";

// generating data for just test
function generateRandomData(numPoints) {
    const data = [];
    const currentTime = new Date();
    for (let i = 0; i < numPoints; i++) {
        const time = new Date(currentTime.getTime() - i * 60 * 60 * 1000 * 4); // 4시간 간격
        const price = Math.round(50000 + Math.random() * 5000); // 임의의 가격 생성
        data.push({ time: time.toLocaleTimeString(), price });
    }
    return data.reverse();
}

const ResultChart = () => {
    const [data, setData] = useState([]);

    // Initial api request for data
    useEffect(() => {
        // api.get("/data")
        //     .then((response) => setData(response.data.data))
        //     .catch((error) => console.error(error));
        setData(generateRandomData(20));
    }, []);

    return (
        <LineChart width={600} height={300} data={data}>
            <Line type="monotone" dataKey="price" stroke="#8884d8" />
            <CartesianGrid stroke="#ccc" strokeDasharray="5 5" />
            <XAxis dataKey="time" />
            <YAxis type="number" domain={["auto", "auto"]} />
            <Tooltip />
        </LineChart>
    );
};

export default ResultChart;
