import json
import os
from datetime import datetime
from collections import Counter
from typing import Dict, List

class QueryLogger:
    """
    Simple query logger for LLMOps monitoring.
    
    In production, this would integrate with:
    - CloudWatch, Datadog, or similar
    - Database for persistent storage
    - Real-time alerting systems
    
    For portfolio: Demonstrates monitoring principles
    """
    
    def __init__(self, log_file="logs/query_log.json"):
        self.log_file = log_file
        self._ensure_log_file()
    
    def _ensure_log_file(self):
        """Create log file if it doesn't exist"""
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                json.dump([], f)
    
    def log_query(self, query: str, intent: str, response_time: float, 
                  sources: List[str] = None, user_email: str = None):
        """
        Log a query with metadata.
        
        LLMOps Practice: Comprehensive logging for analysis
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "intent": intent,
            "response_time_ms": round(response_time * 1000, 2),
            "sources": sources or [],
            "user_email": user_email,
            "query_length": len(query)
        }
        
        # Append to log file
        logs = self._read_logs()
        logs.append(log_entry)
        
        with open(self.log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def _read_logs(self) -> List[Dict]:
        """Read all logs from file"""
        try:
            with open(self.log_file, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def get_metrics(self) -> Dict:
        """
        Calculate monitoring metrics.
        """
        logs = self._read_logs()
        
        if not logs:
            return {
                "total_queries": 0,
                "avg_response_time_ms": 0,
                "total_rag_queries": 0,
                "most_common_queries": [],
                "source_usage": {},
                "queries_by_intent": {}
            }
        
        # Calculate metrics
        total_queries = len(logs)
        avg_response_time = sum(log["response_time_ms"] for log in logs) / total_queries
        
        # RAG-specific queries
        rag_queries = [log for log in logs if log["intent"] == "general_knowledge"]
        total_rag_queries = len(rag_queries)
        
        # Most common queries (normalize to lowercase)
        query_texts = [log["query"].lower() for log in logs]
        most_common = Counter(query_texts).most_common(10)
        
        # Source document usage
        all_sources = []
        for log in rag_queries:
            all_sources.extend(log.get("sources", []))
        
        source_usage = dict(Counter(all_sources).most_common())
        
        # Queries by intent
        intents = [log["intent"] for log in logs]
        queries_by_intent = dict(Counter(intents))
        
        return {
            "total_queries": total_queries,
            "avg_response_time_ms": round(avg_response_time, 2),
            "total_rag_queries": total_rag_queries,
            "most_common_queries": most_common,
            "source_usage": source_usage,
            "queries_by_intent": queries_by_intent,
            "recent_queries": logs[-10:]  # Last 10 queries
        }

# Singleton instance
_logger_instance = None

def get_query_logger():
    """Get or create query logger instance"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = QueryLogger()
    return _logger_instance