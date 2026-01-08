"""
site.py
Site configuration and geometry utilities
"""

import numpy as np # type: ignore
from building import Building


class SiteConfig:
    """Site and building configuration constants"""
    
    # Site dimensions
    SITE_WIDTH = 200.0  # meters
    SITE_HEIGHT = 140.0  # meters
    
    # Building dimensions
    TOWER_A_WIDTH = 30.0
    TOWER_A_HEIGHT = 20.0
    TOWER_B_WIDTH = 20.0
    TOWER_B_HEIGHT = 20.0
    
    # Placement rules
    MIN_BUILDING_DISTANCE = 15.0  # meters between buildings (edge-to-edge)
    MIN_SITE_DISTANCE = 10.0      # meters from site boundary
    NEIGHBOR_DISTANCE = 60.0      # meters for neighbor mix rule (center-to-center)
    
    # Central plaza
    PLAZA_SIZE = 40.0
    PLAZA_X = (SITE_WIDTH - PLAZA_SIZE) / 2  # Center horizontally
    PLAZA_Y = (SITE_HEIGHT - PLAZA_SIZE) / 2  # Center vertically
    
    @classmethod
    def get_plaza_building(cls) -> Building:
        """Returns a Building object representing the plaza"""
        return Building(cls.PLAZA_X, cls.PLAZA_Y, cls.PLAZA_SIZE, cls.PLAZA_SIZE, 'plaza')


class GeometryUtils:
    """Utility functions for geometric calculations"""
    
    @staticmethod
    def rectangles_overlap(r1: Building, r2: Building, margin: float = 0) -> bool:
        """
        Check if two rectangles overlap with optional margin
        
        Args:
            r1: First building
            r2: Second building
            margin: Additional spacing to check (default: 0)
            
        Returns:
            True if rectangles overlap (considering margin), False otherwise
        """
        return not (
            r1.x + r1.width + margin <= r2.x or
            r2.x + r2.width + margin <= r1.x or
            r1.y + r1.height + margin <= r2.y or
            r2.y + r2.height + margin <= r1.y
        )
    
    @staticmethod
    def distance_between_buildings(b1: Building, b2: Building) -> float:
        """
        Calculate Euclidean distance between building centers
        
        Args:
            b1: First building
            b2: Second building
            
        Returns:
            Distance in meters between centers
        """
        c1 = b1.center
        c2 = b2.center
        return np.sqrt((c2[0] - c1[0])**2 + (c2[1] - c1[1])**2)
    
    @staticmethod
    def edge_to_edge_distance(b1: Building, b2: Building) -> float:
        """
        Calculate minimum edge-to-edge distance between two buildings
        
        Args:
            b1: First building
            b2: Second building
            
        Returns:
            Minimum distance in meters between edges
        """
        # Horizontal distance
        if b1.x + b1.width < b2.x:
            dx = b2.x - (b1.x + b1.width)
        elif b2.x + b2.width < b1.x:
            dx = b1.x - (b2.x + b2.width)
        else:
            dx = 0
        
        # Vertical distance
        if b1.y + b1.height < b2.y:
            dy = b2.y - (b1.y + b1.height)
        elif b2.y + b2.height < b1.y:
            dy = b1.y - (b2.y + b2.height)
        else:
            dy = 0
        
        return np.sqrt(dx**2 + dy**2)
    
    @staticmethod
    def is_inside_rectangle(x: float, y: float, width: float, height: float,
                           container_width: float, container_height: float,
                           margin: float = 0) -> bool:
        """
        Check if a rectangle is fully inside a container with optional margin
        
        Args:
            x, y: Rectangle position
            width, height: Rectangle dimensions
            container_width, container_height: Container dimensions
            margin: Required margin from container edges
            
        Returns:
            True if rectangle is inside with proper margin
        """
        return (
            x >= margin and
            y >= margin and
            x + width <= container_width - margin and
            y + height <= container_height - margin
        )