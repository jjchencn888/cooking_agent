import React from 'react';
import ReactDOM from 'react-dom/client';
import './styles.css';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');

function App() {
  const [query, setQuery] = React.useState('鸡蛋，番茄');
  const [result, setResult] = React.useState(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState('');

  const searchRecipe = async (event) => {
    event?.preventDefault();
    const normalizedQuery = query.trim();
    if (!normalizedQuery) {
      setError('请输入至少一种原材料。');
      setResult(null);
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch(`${API_BASE_URL}/api/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: normalizedQuery }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || '搜索失败，请稍后重试。');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message || '暂时无法连接菜谱服务，请稍后重试。');
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-shell">
      <h1>智能菜谱助手</h1>
      <form className="search-box" onSubmit={searchRecipe}>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="输入原材料，用逗号分隔，例如：鸡蛋，番茄"
        />
        <button type="submit" disabled={loading || !query.trim()}>
          {loading ? '搜索中……' : '搜索菜谱'}
        </button>
      </form>
      <div className="demo-examples" aria-label="演示样例">
        <span>试试：</span>
        {['番茄，鸡蛋', '土豆，青椒', '黄瓜，鸡蛋'].map((example) => (
          <button type="button" key={example} onClick={() => setQuery(example)}>
            {example}
          </button>
        ))}
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
