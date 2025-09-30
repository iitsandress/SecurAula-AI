"""
Metrics service for storing and retrieving system metrics
"""
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from ..models.metrics import Metrics
from ..models.client import Client
from ..core.logging import AuditLogger


class MetricsService:
    """Service for managing system metrics"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def store_metrics(
        self,
        client_id: int,
        session_id: Optional[int],
        metrics_data: Dict[str, Any]
    ) -> Metrics:
        """Store metrics data"""
        metrics = Metrics(
            client_id=client_id,
            session_id=session_id,
            cpu_percent=metrics_data.get('cpu_percent', 0.0),
            memory_percent=metrics_data.get('memory_percent', 0.0),
            memory_used=metrics_data.get('memory_used'),
            memory_total=metrics_data.get('memory_total'),
            disk_percent=metrics_data.get('disk_percent'),
            disk_used=metrics_data.get('disk_used'),
            disk_total=metrics_data.get('disk_total'),
            uptime_seconds=metrics_data.get('uptime_seconds', 0),
            network_sent=metrics_data.get('network_sent'),
            network_recv=metrics_data.get('network_recv'),
            process_count=metrics_data.get('process_count'),
            active_window=metrics_data.get('active_window'),
            load_average=metrics_data.get('load_average'),
            temperature=metrics_data.get('temperature')
        )
        
        self.db.add(metrics)
        self.db.commit()
        self.db.refresh(metrics)
        
        return metrics
    
    def get_latest_metrics(self, client_id: int) -> Optional[Metrics]:
        """Get latest metrics for a client"""
        return self.db.query(Metrics).filter(
            Metrics.client_id == client_id
        ).order_by(desc(Metrics.timestamp)).first()
    
    def get_metrics_history(
        self,
        client_id: int,
        hours: int = 24,
        limit: int = 1000
    ) -> List[Metrics]:
        """Get metrics history for a client"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        return self.db.query(Metrics).filter(
            and_(
                Metrics.client_id == client_id,
                Metrics.timestamp >= cutoff_time
            )
        ).order_by(desc(Metrics.timestamp)).limit(limit).all()
    
    def get_aggregated_metrics(
        self,
        client_id: int,
        hours: int = 24,
        interval_minutes: int = 5
    ) -> List[Dict[str, Any]]:
        """Get aggregated metrics for a client"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        # Group by time intervals
        time_bucket = func.strftime(
            '%Y-%m-%d %H:%M',
            func.datetime(
                Metrics.timestamp,
                f'+{interval_minutes} minutes',
                'start of day',
                f'+{interval_minutes} minutes'
            )
        )
        
        results = self.db.query(
            time_bucket.label('time_bucket'),
            func.avg(Metrics.cpu_percent).label('avg_cpu'),
            func.max(Metrics.cpu_percent).label('max_cpu'),
            func.avg(Metrics.memory_percent).label('avg_memory'),
            func.max(Metrics.memory_percent).label('max_memory'),
            func.count(Metrics.id).label('sample_count')
        ).filter(
            and_(
                Metrics.client_id == client_id,
                Metrics.timestamp >= cutoff_time
            )
        ).group_by(time_bucket).order_by(time_bucket).all()
        
        return [
            {
                "timestamp": result.time_bucket,
                "avg_cpu": float(result.avg_cpu) if result.avg_cpu else 0,
                "max_cpu": float(result.max_cpu) if result.max_cpu else 0,
                "avg_memory": float(result.avg_memory) if result.avg_memory else 0,
                "max_memory": float(result.max_memory) if result.max_memory else 0,
                "sample_count": result.sample_count
            }
            for result in results
        ]
    
    def get_classroom_metrics_summary(self, classroom_id: int) -> Dict[str, Any]:
        """Get metrics summary for all clients in a classroom"""
        # Get latest metrics for each client in the classroom
        subquery = self.db.query(
            Metrics.client_id,
            func.max(Metrics.timestamp).label('latest_timestamp')
        ).join(Client).filter(
            Client.classroom_id == classroom_id
        ).group_by(Metrics.client_id).subquery()
        
        latest_metrics = self.db.query(Metrics).join(
            subquery,
            and_(
                Metrics.client_id == subquery.c.client_id,
                Metrics.timestamp == subquery.c.latest_timestamp
            )
        ).all()
        
        if not latest_metrics:
            return {
                "client_count": 0,
                "avg_cpu": 0,
                "avg_memory": 0,
                "max_cpu": 0,
                "max_memory": 0,
                "clients": []
            }
        
        # Calculate aggregates
        cpu_values = [m.cpu_percent for m in latest_metrics]
        memory_values = [m.memory_percent for m in latest_metrics]
        
        return {
            "client_count": len(latest_metrics),
            "avg_cpu": sum(cpu_values) / len(cpu_values),
            "avg_memory": sum(memory_values) / len(memory_values),
            "max_cpu": max(cpu_values),
            "max_memory": max(memory_values),
            "clients": [
                {
                    "client_id": m.client_id,
                    "device_id": m.client.device_id if m.client else None,
                    "hostname": m.client.hostname if m.client else None,
                    "cpu_percent": m.cpu_percent,
                    "memory_percent": m.memory_percent,
                    "timestamp": m.timestamp.isoformat()
                }
                for m in latest_metrics
            ]
        }
    
    def cleanup_old_metrics(self, retention_days: int = 7) -> int:
        """Clean up old metrics data"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=retention_days)
        
        deleted_count = self.db.query(Metrics).filter(
            Metrics.timestamp < cutoff_time
        ).delete()
        
        if deleted_count > 0:
            self.db.commit()
            AuditLogger.log_system_action(
                action="metrics_cleanup",
                details={
                    "deleted_count": deleted_count,
                    "retention_days": retention_days
                }
            )
        
        return deleted_count
    
    def get_system_health_summary(self) -> Dict[str, Any]:
        """Get overall system health summary"""
        # Get metrics from last 5 minutes
        recent_time = datetime.now(timezone.utc) - timedelta(minutes=5)
        
        recent_metrics = self.db.query(Metrics).filter(
            Metrics.timestamp >= recent_time
        ).all()
        
        if not recent_metrics:
            return {
                "status": "no_data",
                "active_clients": 0,
                "avg_cpu": 0,
                "avg_memory": 0,
                "alerts": []
            }
        
        # Group by client to get latest metrics per client
        client_metrics = {}
        for metric in recent_metrics:
            if metric.client_id not in client_metrics or metric.timestamp > client_metrics[metric.client_id].timestamp:
                client_metrics[metric.client_id] = metric
        
        latest_metrics = list(client_metrics.values())
        cpu_values = [m.cpu_percent for m in latest_metrics]
        memory_values = [m.memory_percent for m in latest_metrics]
        
        avg_cpu = sum(cpu_values) / len(cpu_values)
        avg_memory = sum(memory_values) / len(memory_values)
        
        # Generate alerts
        alerts = []
        high_cpu_clients = [m for m in latest_metrics if m.cpu_percent > 90]
        high_memory_clients = [m for m in latest_metrics if m.memory_percent > 90]
        
        if high_cpu_clients:
            alerts.append({
                "type": "high_cpu",
                "message": f"{len(high_cpu_clients)} clients with high CPU usage",
                "clients": [m.client.device_id for m in high_cpu_clients if m.client]
            })
        
        if high_memory_clients:
            alerts.append({
                "type": "high_memory",
                "message": f"{len(high_memory_clients)} clients with high memory usage",
                "clients": [m.client.device_id for m in high_memory_clients if m.client]
            })
        
        # Determine overall status
        status = "healthy"
        if avg_cpu > 80 or avg_memory > 80:
            status = "warning"
        if avg_cpu > 95 or avg_memory > 95:
            status = "critical"
        
        return {
            "status": status,
            "active_clients": len(latest_metrics),
            "avg_cpu": avg_cpu,
            "avg_memory": avg_memory,
            "max_cpu": max(cpu_values),
            "max_memory": max(memory_values),
            "alerts": alerts
        }