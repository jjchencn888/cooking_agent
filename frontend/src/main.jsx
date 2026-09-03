import React from 'react';
import ReactDOM from 'react-dom/client';
import './styles.css';

function App() {
  const [query, setQuery] = React.useState('番茄鸡蛋面');
  const [result, setResult] = React.useState(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState('');

  const searchRecipe = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await fetch('http://127.0.0.1:8000/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error('搜索失败');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message || '请求失败，请确认后端服务已经启动。');
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-shell">
      <h1>智能菜谱助手</h1>
      <div className="search-box">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="输入菜名或食材，例如：番茄鸡蛋面"
        />
        <button onClick={searchRecipe} disabled={loading}>
          {loading ? '搜索中……' : '搜索菜谱'}
        </button>
      </div>

      {error && <div className="error-box">{error}</div>}

      {result && (
        <div className="result-panel">
          <h2>{result.query}</h2>
          <p className="message">{result.message}</p>

          {result.results?.length ? (
            result.results.map((item, index) => (
              <div className="recipe-card" key={`${item.title}-${index}`}>
                <h3>{item.title}</h3>
                <div className="meta">来源：{item.source}</div>
                <div className="section">
                  <h4>食材</h4>
                  <ul>
                    {item.ingredients?.length ? (
                      item.ingredients.map((ing, i) => <li key={`${ing}-${i}`}>{ing}</li>)
                    ) : (
                      <li>暂无食材信息</li>
                    )}
                  </ul>
                </div>
                <div className="section">
                  <h4>烹饪步骤</h4>
                  {item.steps?.length ? (
                    <ol>
                      {item.steps.map((step, stepIndex) => (
                        <li key={`${item.title}-step-${stepIndex}`}>{step}</li>
                      ))}
                    </ol>
                  ) : (
                    <p>{item.instructions || '暂无步骤说明'}</p>
                  )}
                </div>
              </div>
            ))
          ) : (
            <p>没有找到匹配的菜谱。</p>
          )}
        </div>
      )}
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
