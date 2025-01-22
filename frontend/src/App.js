import React, { useState } from "react";
import axios from "axios";

const backendUrl = "http://127.0.0.1:5001/execute";
/* http://127.0.0.1:5001/execute, "https://tqsdk-quant-beh5e8agbebef4be.westus-01.azurewebsites.net"*/

function App() {
  const [mode, setMode] = useState(1);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [tradeSymbol1, setTradeSymbol1] = useState("");
  const [tradeSymbol2, setTradeSymbol2] = useState("");
  const [trackSymbol, setTrackSymbol] = useState("");
  const [positionPercent1, setPositionPercent1] = useState("");
  const [positionPercent2, setPositionPercent2] = useState("");
  const [trackSymbolBuyLow1, setTrackSymbolBuyLow1] = useState("");
  const [trackSymbolBuyHigh1, setTrackSymbolBuyHigh1] = useState("");
  const [trackSymbolBuyLow2, setTrackSymbolBuyLow2] = useState("");
  const [trackSymbolBuyHigh2, setTrackSymbolBuyHigh2] = useState("");
  const [sellAtProfitHigh1, setSellAtProfitHigh1] = useState("");
  const [sellAtProfitLow1, setSellAtProfitLow1] = useState("");
  const [sellAtProfitHigh2, setSellAtProfitHigh2] = useState("");
  const [sellAtProfitLow2, setSellAtProfitLow2] = useState("");
  const [sellAtLossMorning, setSellAtLossMorning] = useState("");
  const [sellAtLossAfternoon, setSellAtLossAfternoon] = useState("");
  const [trackSymmbolAddBuy, setTrackSymmbolAddBuy] = useState("");
  const [additionalPositionPercent, setAdditionalPositionPercent] =
    useState(0.1);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [response, setResponse] = useState(null);
  const [isRunning, setIsRunning] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    const payload = {
      mode,
      username,
      password,
      trade_symbol1: tradeSymbol1,
      trade_symbol2: tradeSymbol2,
      track_symbol: trackSymbol,
      position_percent1: positionPercent1,
      position_percent2: positionPercent2,
      track_symbol_buy_low1: trackSymbolBuyLow1,
      track_symbol_buy_high1: trackSymbolBuyHigh1,
      track_symbol_buy_low2: trackSymbolBuyLow2,
      track_symbol_buy_high2: trackSymbolBuyHigh2,
      sell_at_profit_high1: sellAtProfitHigh1,
      sell_at_profit_low1: sellAtProfitLow1,
      sell_at_profit_high2: sellAtProfitHigh2,
      sell_at_profit_low2: sellAtProfitLow2,
      sell_at_loss_morning: sellAtLossMorning,
      sell_at_loss_afternoon: sellAtLossAfternoon,
      track_symmbol_add_buy: trackSymmbolAddBuy,
      additional_position_percent: additionalPositionPercent,
      ...(mode === 2 && { start_date: startDate, end_date: endDate }),
    };

    console.log("Payload to be sent:", payload);

    try {
      const res = await axios.post(`${backendUrl}/execute`, payload);
      console.log("Response from backend:", res.data);
      setResponse(res.data);
    } catch (error) {
      console.error("Error during API call:", error);
      setResponse(
        error.response
          ? {
              error: error.response.data.error || "Server error",
              status: error.response.status,
            }
          : { error: "Network error. Please check your connection." }
      );
    }
  };

  const handleStop = async () => {
    try {
      const res = await axios.post(`${backendUrl}/stop`);
      alert(res.data.message);
    } catch (error) {
      alert("Error stopping strategy.");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-r from-blue-100 to-purple-200 flex items-center justify-center py-10">
      <div className="bg-white shadow-md rounded-lg p-8 max-w-4xl w-full">
        <h1 className="text-2xl font-bold text-gray-800 text-center mb-6">
          Trading Strategy
        </h1>
        <form onSubmit={handleSubmit} className="space-y-6">
          <label className="block text-gray-700 font-medium">
            Mode:
            <select
              value={mode}
              onChange={(e) => setMode(Number(e.target.value))}
              className="w-full border border-gray-300 p-2 rounded-md"
            >
              <option value={1}>Simulation</option>
              <option value={2}>Backtest</option>
            </select>
          </label>
          <br />
          <label className="block text-gray-700 font-medium">
            Username:
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              required
            />
          </label>
          <br />
          <label className="block text-gray-700 font-medium">
            Password:
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              required
            />
          </label>
          <br />
          <label>
            Trade Symbol 1:
            <input
              type="text"
              value={tradeSymbol1}
              onChange={(e) => setTradeSymbol1(e.target.value)}
              required
            />
          </label>
          <br />
          <label>
            Trade Symbol 2:
            <input
              type="text"
              value={tradeSymbol2}
              onChange={(e) => setTradeSymbol2(e.target.value)}
              required
            />
          </label>
          <br />
          <label>
            Track Symbol:
            <input
              type="text"
              value={trackSymbol}
              onChange={(e) => setTrackSymbol(e.target.value)}
              required
            />
          </label>
          <br />
          <label>
            Position Percent 1:
            <input
              type="number"
              value={positionPercent1}
              onChange={(e) => setPositionPercent1(e.target.value)}
              required
            />
          </label>
          <br />
          <label>
            Position Percent 2:
            <input
              type="number"
              value={positionPercent2}
              onChange={(e) => setPositionPercent2(e.target.value)}
              required
            />
          </label>
          <br />
          <label>
            Track Symbol Buy Low 1:
            <input
              type="number"
              value={trackSymbolBuyLow1}
              onChange={(e) => setTrackSymbolBuyLow1(e.target.value)}
            />
          </label>
          <br />
          <label>
            Track Symbol Buy High 1:
            <input
              type="number"
              value={trackSymbolBuyHigh1}
              onChange={(e) => setTrackSymbolBuyHigh1(e.target.value)}
            />
          </label>
          <br />
          <label>
            Track Symbol Buy Low 2:
            <input
              type="number"
              value={trackSymbolBuyLow2}
              onChange={(e) => setTrackSymbolBuyLow2(e.target.value)}
            />
          </label>
          <br />
          <label>
            Track Symbol Buy High 2:
            <input
              type="number"
              value={trackSymbolBuyHigh2}
              onChange={(e) => setTrackSymbolBuyHigh2(e.target.value)}
            />
          </label>
          <br />
          <label>
            Sell at Profit High 1:
            <input
              type="number"
              value={sellAtProfitHigh1}
              onChange={(e) => setSellAtProfitHigh1(e.target.value)}
            />
          </label>
          <br />
          <label>
            Sell at Profit Low 1:
            <input
              type="number"
              value={sellAtProfitLow1}
              onChange={(e) => setSellAtProfitLow1(e.target.value)}
            />
          </label>
          <br />
          <label>
            Sell at Profit High 2:
            <input
              type="number"
              value={sellAtProfitHigh2}
              onChange={(e) => setSellAtProfitHigh2(e.target.value)}
            />
          </label>
          <br />
          <label>
            Sell at Profit Low 2:
            <input
              type="number"
              value={sellAtProfitLow2}
              onChange={(e) => setSellAtProfitLow2(e.target.value)}
            />
          </label>
          <br />
          <label>
            Sell at Loss Morning:
            <input
              type="number"
              value={sellAtLossMorning}
              onChange={(e) => setSellAtLossMorning(e.target.value)}
            />
          </label>
          <br />
          <label>
            Sell at Loss Afternoon:
            <input
              type="number"
              value={sellAtLossAfternoon}
              onChange={(e) => setSellAtLossAfternoon(e.target.value)}
            />
          </label>
          <br />
          <label>
            Track Symbol Add Buy:
            <input
              type="number"
              value={trackSymmbolAddBuy}
              onChange={(e) => setTrackSymmbolAddBuy(e.target.value)}
            />
          </label>
          <br />
          <label>
            Additional Position Percent:
            <input
              type="number"
              value={additionalPositionPercent}
              onChange={(e) => setAdditionalPositionPercent(e.target.value)}
            />
          </label>
          <br />
          {mode === 2 && (
            <>
              <label>
                Start Date:
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  required
                />
              </label>
              <br />
              <label>
                End Date:
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  required
                />
              </label>
              <br />
            </>
          )}
          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            disabled={isRunning}
          >
            {isRunning ? "Strategy Running..." : "Run Strategy"}
          </button>
        </form>
        <button
          onClick={handleStop}
          className="w-full bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700 mt-4 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
        >
          Stop Strategy
        </button>
        {response && (
          <div className="mt-6 bg-gray-50 rounded-md p-4">
            <h2 className="text-lg font-semibold text-gray-800 mb-2">
              Response
            </h2>
            <pre className="bg-white p-4 rounded-md overflow-auto">
              {JSON.stringify(response, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
