from flask import Flask, render_template_string
from monitoring import get_query_logger
import json

app = Flask(__name__)

# HTML template for dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>LLMOps Monitoring Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        h1 { color: #667eea; margin-bottom: 10px; }
        .subtitle { color: #666; }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .metric-card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .metric-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin: 10px 0;
        }
        .metric-label {
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .chart-section {
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        h2 {
            color: #667eea;
            margin-bottom: 20px;
            border-bottom: 2px solid #f0f0f0;
            padding-bottom: 10px;
        }
        .query-list {
            list-style: none;
        }
        .query-item {
            padding: 15px;
            border-bottom: 1px solid #f0f0f0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .query-item:hover {
            background: #f8f9fa;
        }
        .query-text {
            flex: 1;
            font-weight: 500;
        }
        .query-count {
            background: #667eea;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
        }
        .source-bar {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }
        .source-name {
            width: 200px;
            font-weight: 500;
        }
        .source-bar-fill {
            flex: 1;
            height: 30px;
            background: linear-gradient(90deg, #667eea, #764ba2);
            border-radius: 5px;
            display: flex;
            align-items: center;
            padding: 0 10px;
            color: white;
            font-weight: bold;
        }
        .recent-query {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 10px;
            border-left: 4px solid #667eea;
        }
        .query-meta {
            display: flex;
            gap: 20px;
            font-size: 0.85em;
            color: #666;
            margin-top: 8px;
        }
        .intent-badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
            margin-right: 10px;
        }
        .intent-general { background: #e3f2fd; color: #1976d2; }
        .intent-api { background: #f3e5f5; color: #7b1fa2; }
        .intent-billing { background: #fff3e0; color: #f57c00; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 LLMOps Monitoring Dashboard</h1>
            <p class="subtitle">Real-time monitoring for AI Chatbot with RAG</p>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Total Queries</div>
                <div class="metric-value">{{ metrics.total_queries }}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Avg Response Time</div>
                <div class="metric-value">{{ metrics.avg_response_time_ms }}ms</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">RAG Queries</div>
                <div class="metric-value">{{ metrics.total_rag_queries }}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Success Rate</div>
                <div class="metric-value">
                    {% if metrics.total_queries > 0 %}
                        {{ ((metrics.total_queries / metrics.total_queries) * 100) | round }}%
                    {% else %}
                        0%
                    {% endif %}
                </div>
            </div>
        </div>
        
        <div class="chart-section">
            <h2>📊 Queries by Intent</h2>
            {% for intent, count in metrics.queries_by_intent.items() %}
            <div class="source-bar">
                <div class="source-name">{{ intent }}</div>
                <div class="source-bar-fill" style="width: {{ (count / metrics.total_queries * 100) if metrics.total_queries > 0 else 0 }}%;">
                    {{ count }} queries
                </div>
            </div>
            {% endfor %}
        </div>
        
        <div class="chart-section">
            <h2>🔥 Most Common Questions</h2>
            <ul class="query-list">
                {% for query, count in metrics.most_common_queries %}
                <li class="query-item">
                    <span class="query-text">{{ query }}</span>
                    <span class="query-count">{{ count }}x</span>
                </li>
                {% endfor %}
            </ul>
        </div>
        
        {% if metrics.source_usage %}
        <div class="chart-section">
            <h2>📚 Knowledge Base Source Usage</h2>
            {% for source, count in metrics.source_usage.items() %}
            <div class="source-bar">
                <div class="source-name">{{ source.split('/')[-1] }}</div>
                <div class="source-bar-fill" style="width: {{ (count / metrics.total_rag_queries * 100) if metrics.total_rag_queries > 0 else 0 }}%;">
                    {{ count }} retrievals
                </div>
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        <div class="chart-section">
            <h2>🕐 Recent Queries</h2>
            {% for query in metrics.recent_queries|reverse %}
            <div class="recent-query">
                <div>
                    <span class="intent-badge intent-{{ query.intent.split('_')[0] }}">
                        {{ query.intent }}
                    </span>
                    <strong>{{ query.query }}</strong>
                </div>
                <div class="query-meta">
                    <span>⏱️ {{ query.response_time_ms }}ms</span>
                    <span>📅 {{ query.timestamp.split('T')[0] }}</span>
                    <span>🕐 {{ query.timestamp.split('T')[1].split('.')[0] }}</span>
                    {% if query.sources %}
                    <span>📄 {{ query.sources|length }} sources</span>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def dashboard():
    """Render monitoring dashboard"""
    logger = get_query_logger()
    metrics = logger.get_metrics()
    return render_template_string(DASHBOARD_HTML, metrics=metrics)

if __name__ == '__main__':
    print("📊 Starting LLMOps Monitoring Dashboard...")
    print("🌐 Open: http://localhost:5001")
    app.run(debug=True, port=5001)