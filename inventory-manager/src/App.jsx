import { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [items, setItems] = useState([]);
  const [weightStats, setWeightStats] = useState({ current: 0, max: 100 });
  const [statusMessage, setStatusMessage] = useState({
    text: "",
    isError: false,
    rarity: "",
  });

  const fetchInventory = () => {
    fetch("http://127.0.0.1:5000/api/inventory")
      .then((res) => res.json())
      .then((data) => {
        setItems(data.items);
        setWeightStats({ current: data.current_weight, max: data.max_weight });
      })
      .catch((err) => console.error(err));
  };

  useEffect(() => {
    fetchInventory();
  }, []);

  const rollForLoot = () => {
    setStatusMessage({ text: "", isError: false, rarity: "" });

    fetch("http://127.0.0.1:5000/api/loot/roll", { method: "POST" })
      .then(async (res) => {
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || "Failed to roll loot");
        return data;
      })
      .then((data) => {
        setStatusMessage({
          text: `You found loot! You stashed a ${data.new_item.rarity} ${data.new_item.name}!`,
          isError: false,
          rarity: data.new_item.rarity,
        });
        fetchInventory();
      })
      .catch((err) => {
        setStatusMessage({ text: err.message, isError: true, rarity: "" });
      });
  };

  const clearAllInventory = () => {
    fetch("http://127.0.0.1:5000/api/inventory/clear", { method: "POST" }).then(
      () => {
        setStatusMessage({
          text: "🧹 Emptied your inventory bag.",
          isError: false,
          rarity: "",
        });
        fetchInventory();
      },
    );
  };

// bar color
  const getWeightMeterClass = () => {
    const ratio = weightStats.current / weightStats.max;
    if (ratio >= 1.0) return "fill-danger";
    if (ratio > 0.8) return "fill-warning";
    return "fill-safe";
  };

  return (
    <div className="gacha-container">
      <h1 className="gacha-title">DUNGEON LOOTER</h1>

      <div className="weight-dashboard">
        <div className="weight-header">
          <span>
            Bag Weight:{" "}
            <strong>
              {weightStats.current.toFixed(1)} / {weightStats.max} lbs
            </strong>
          </span>
          <span>Items: {items.length}</span>
        </div>
        <div className="progress-track">
          <div
            className={`progress-fill ${getWeightMeterClass()}`}
            style={{
              width: `${Math.min((weightStats.current / weightStats.max) * 100, 100)}%`,
            }}
          />
        </div>
      </div>

      {/* buttons Panel */}
      <div className="control-panel">
        <button onClick={rollForLoot} className="btn-roll">
          ⚔️ EXPLORE DUNGEON (Roll Loot)
        </button>
        <button onClick={clearAllInventory} className="btn-clear">
          Trash Items
        </button>
      </div>

      {statusMessage.text && (
        <div
          className={`status-banner ${statusMessage.isError ? "status-error" : `rarity-${statusMessage.rarity}`}`}
        >
          {statusMessage.text}
        </div>
      )}

      <h3>🎒 ADVENTURER'S PACK</h3>
      <div className="stash-list">
        {items.length === 0 ? (
          <p className="empty-message">
            Your inventory is empty. Go raid the dungeon!
          </p>
        ) : (
          [...items].reverse().map((item) => (
            <div key={item.id} className={`loot-card rarity-${item.rarity}`}>
              <div>
                <span className="item-name">💎 {item.name}</span>
                <span className="item-meta">[{item.type}]</span>
              </div>
              <span className="item-weight">⚖️ {item.weight} lbs</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default App;
