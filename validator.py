"""
validator.py
Rule validation for building layouts
"""

from typing import List, Dict
from building import Building
from site_config import SiteConfig, GeometryUtils


class RuleValidator:
    """Validates building layouts against placement rules"""
    
    def __init__(self, config: SiteConfig):
        """
        Initialize validator with site configuration
        
        Args:
            config: Site configuration object
        """
        self.config = config
        self.geo = GeometryUtils()
    
    def is_inside_site(self, building: Building) -> bool:
        """
        Rule 1 & 3: Check if building is inside site with proper setback
        
        Args:
            building: Building to check
            
        Returns:
            True if building respects site boundaries and setback
        """
        return self.geo.is_inside_rectangle(
            building.x, building.y,
            building.width, building.height,
            self.config.SITE_WIDTH, self.config.SITE_HEIGHT,
            self.config.MIN_SITE_DISTANCE
        )
    
    def overlaps_plaza(self, building: Building) -> bool:
        """
        Rule 5: Check if building overlaps the central plaza
        
        Args:
            building: Building to check
            
        Returns:
            True if building overlaps plaza
        """
        plaza = self.config.get_plaza_building()
        return self.geo.rectangles_overlap(building, plaza, 0)
    
    def check_building_distances(self, buildings: List[Building]) -> bool:
        """
        Rule 2: Check if all buildings maintain minimum distance
        
        Args:
            buildings: List of all buildings in layout
            
        Returns:
            True if all building pairs respect minimum distance
        """
        for i in range(len(buildings)):
            for j in range(i + 1, len(buildings)):
                edge_dist = self.geo.edge_to_edge_distance(buildings[i], buildings[j])
                if edge_dist < self.config.MIN_BUILDING_DISTANCE:
                    return False
        return True
    
    def check_neighbor_mix(self, buildings: List[Building]) -> bool:
        """
        Rule 4: Check if each Tower A has at least one Tower B within 60m
        
        Args:
            buildings: List of all buildings in layout
            
        Returns:
            True if neighbor mix rule is satisfied
        """
        tower_a_buildings = [b for b in buildings if b.building_type == 'A']
        tower_b_buildings = [b for b in buildings if b.building_type == 'B']
        
        # If no Tower A buildings, rule is satisfied
        if not tower_a_buildings:
            return True
        
        # Check each Tower A
        for tower_a in tower_a_buildings:
            has_nearby_b = any(
                self.geo.distance_between_buildings(tower_a, tower_b) <= self.config.NEIGHBOR_DISTANCE
                for tower_b in tower_b_buildings
            )
            if not has_nearby_b:
                return False
        
        return True
    
    def validate_layout(self, buildings: List[Building]) -> Dict[str, bool]:
        """
        Validate all rules for a complete layout
        
        Args:
            buildings: List of all buildings in layout
            
        Returns:
            Dictionary with rule names as keys and pass/fail as values
        """
        rules = {
            'inside_site': True,
            'building_distance': True,
            'site_distance': True,
            'neighbor_mix': True,
            'plaza_clear': True
        }
        
        # Check each building individually
        for building in buildings:
            # Rule 1 & 3: Inside site with setback
            if not self.is_inside_site(building):
                rules['inside_site'] = False
                rules['site_distance'] = False
            
            # Rule 5: Plaza clear
            if self.overlaps_plaza(building):
                rules['plaza_clear'] = False
        
        # Rule 2: Building distances
        rules['building_distance'] = self.check_building_distances(buildings)
        
        # Rule 4: Neighbor mix
        rules['neighbor_mix'] = self.check_neighbor_mix(buildings)
        
        return rules
    
    def get_violations(self, buildings: List[Building]) -> List[str]:
        """
        Get a list of violated rules
        
        Args:
            buildings: List of all buildings in layout
            
        Returns:
            List of rule names that are violated
        """
        rules = self.validate_layout(buildings)
        violations = [rule for rule, passed in rules.items() if not passed]
        return violations
    
    def is_valid_layout(self, buildings: List[Building]) -> bool:
        """
        Check if layout satisfies all rules
        
        Args:
            buildings: List of all buildings in layout
            
        Returns:
            True if all rules are satisfied
        """
        rules = self.validate_layout(buildings)
        return all(rules.values())