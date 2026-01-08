"""
building.py
Building data structures and types
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class Building:
    """Represents a building on the site"""
    x: float
    y: float
    width: float
    height: float
    building_type: str  # 'A' or 'B'
    
    @property
    def center(self) -> Tuple[float, float]:
        """Returns center coordinates of the building"""
        return (self.x + self.width / 2, self.y + self.height / 2)
    
    @property
    def area(self) -> float:
        """Returns building footprint area"""
        return self.width * self.height
    
    def __repr__(self) -> str:
        return f"Building(type={self.building_type}, x={self.x:.1f}, y={self.y:.1f}, {self.width}x{self.height})"


class BuildingType:
    """Building type specifications"""
    
    @staticmethod
    def get_dimensions(building_type: str) -> Tuple[float, float]:
        """Get width and height for a building type"""
        if building_type == 'A':
            return (30.0, 20.0)  # Tower A: 30m x 20m
        elif building_type == 'B':
            return (20.0, 20.0)  # Tower B: 20m x 20m
        else:
            raise ValueError(f"Unknown building type: {building_type}")
    
    @staticmethod
    def create_building(building_type: str, x: float, y: float) -> Building:
        """Create a building instance of specified type"""
        width, height = BuildingType.get_dimensions(building_type)
        return Building(x, y, width, height, building_type)