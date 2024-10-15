import { BrowserRouter as Router, Route, Routes, Navigate } from "react-router-dom";
import Header from "./components/Header.jsx";
import StatusPage from "./pages/StatusPage.jsx";
import ResultPage from "./pages/ResultPage.jsx";
import BacktestingPage from "./pages/BacktestingPage.jsx";
import ReportPage from "./pages/ReportPage.jsx";

function App() {
    return (
        <Router>
            <Header />
            <Routes>
                <Route path="/status" element={<StatusPage />} />
                <Route path="/result" element={<ResultPage />} />
                <Route path="/backtesting" element={<BacktestingPage />} />
                <Route path="/report" element={<ReportPage />} />
                <Route path="/" element={<Navigate replace to="/status" />} />
            </Routes>
        </Router>
    );
}

export default App;
