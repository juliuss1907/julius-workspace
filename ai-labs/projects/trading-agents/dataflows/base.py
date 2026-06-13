"""
Base Data Source Interface
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime


class DataSource(ABC):
    """Abstract base class for all data sources"""
    
    def __init__(self, name: str):
        self.name = name
        self.last_fetch = None
        self.error_count = 0
    
    @abstractmethod
    async def fetch(self, *args, **kwargs) -> Any:
        """Fetch data from source"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if source is available"""
        pass
    
    def record_success(self):
        """Record successful fetch"""
        self.last_fetch = datetime.now()
        self.error_count = 0
    
    def record_error(self):
        """Record failed fetch"""
        self.error_count += 1
