"""
generator.py
Layout generation using improved random search algorithm
"""

import random
from typing import List, Dict
from dataclasses import dataclass
from building import Building, BuildingType
from site_config import SiteConfig, GeometryUtils
from validator import RuleValidator


@dataclass
class Layout:
    """Represents a complete site layout with validation results"""
    buildings: List[Building]
    rules_satisfied: Dict[str, bool]
    score: float
    
    def get_tower_count(self, tower_type: str) -> int:
        """Count buildings of a specific type"""
        return sum(1 for b in self.buildings if b.building_type == tower_type)
    
    def get_total_area(self) -> float:
        """Calculate total built area"""
        return sum(b.area for b in self.buildings)
    
    def __repr__(self) -> str:
        return (f"Layout(buildings={len(self.buildings)}, "
                f"score={self.score:.0f}, "
                f"valid={all(self.rules_satisfied.values())})")


class LayoutGenerator:
    """Generates building layouts using improved random search algorithm"""
    
    def __init__(self, config: SiteConfig = None):
        """
        Initialize generator with configuration
        
        Args:
            config: Site configuration (uses default if None)
        """
        self.config = config or SiteConfig()
        self.validator = RuleValidator(self.config)
        self.geo = GeometryUtils()
    
    def is_valid_placement(self, new_building: Building, 
                          existing_buildings: List[Building]) -> bool:
        """
        Check if a new building can be placed without violations
        
        Args:
            new_building: Building to place
            existing_buildings: Already placed buildings
            
        Returns:
            True if placement is valid
        """
        # Check site boundaries
        if not self.validator.is_inside_site(new_building):
            return False
        
        # Check plaza overlap
        if self.validator.overlaps_plaza(new_building):
            return False
        
        # Check overlap with existing buildings
        for existing in existing_buildings:
            edge_dist = self.geo.edge_to_edge_distance(new_building, existing)
            if edge_dist < self.config.MIN_BUILDING_DISTANCE:
                return False
        
        return True
    
    def has_nearby_tower_b(self, tower_a: Building, existing_buildings: List[Building]) -> bool:
        """
        Check if a Tower A has at least one Tower B within range
        
        Args:
            tower_a: Tower A building to check
            existing_buildings: All existing buildings
            
        Returns:
            True if at least one Tower B is within neighbor distance
        """
        tower_b_buildings = [b for b in existing_buildings if b.building_type == 'B']
        
        for tower_b in tower_b_buildings:
            distance = self.geo.distance_between_buildings(tower_a, tower_b)
            if distance <= self.config.NEIGHBOR_DISTANCE:
                return True
        
        return False
    
    def generate_random_position(self, building_type: str) -> tuple:
        """
        Generate a random position for a building type
        
        Args:
            building_type: 'A' or 'B'
            
        Returns:
            (x, y) coordinates
        """
        width, height = BuildingType.get_dimensions(building_type)
        
        # Calculate valid ranges
        max_x = self.config.SITE_WIDTH - width - self.config.MIN_SITE_DISTANCE
        max_y = self.config.SITE_HEIGHT - height - self.config.MIN_SITE_DISTANCE
        
        x = random.uniform(self.config.MIN_SITE_DISTANCE, max_x)
        y = random.uniform(self.config.MIN_SITE_DISTANCE, max_y)
        
        return x, y
    
    def generate_single_layout_improved(self, max_buildings: int = 15, 
                                       max_attempts: int = 2000) -> List[Building]:
        """
        Generate a single layout with improved neighbor mix handling
        
        Args:
            max_buildings: Target number of buildings to place
            max_attempts: Maximum placement attempts
            
        Returns:
            List of placed buildings
        """
        buildings = []
        attempts = 0
        consecutive_failures = 0
        
        while len(buildings) < max_buildings and attempts < max_attempts:
            attempts += 1
            
            # Smart building type selection
            tower_a_count = sum(1 for b in buildings if b.building_type == 'A')
            tower_b_count = sum(1 for b in buildings if b.building_type == 'B')
            
            # If we have more Tower As than Bs, prefer placing Tower B
            if tower_a_count > tower_b_count + 1:
                building_type = 'B'
            # If we have Tower As without nearby Tower Bs, definitely place Tower B
            elif tower_a_count > 0 and tower_b_count == 0:
                building_type = 'B'
            # Otherwise, random with slight preference for balance
            else:
                building_type = random.choice(['A', 'B'])
            
            # Generate random position
            x, y = self.generate_random_position(building_type)
            
            # Create building
            new_building = BuildingType.create_building(building_type, x, y)
            
            # Check if valid placement
            if self.is_valid_placement(new_building, buildings):
                # Additional check: if placing Tower A, verify it will have a Tower B nearby
                if building_type == 'A':
                    # Check if there's at least one Tower B within range
                    has_neighbor = self.has_nearby_tower_b(new_building, buildings)
                    
                    # If no nearby Tower B and we have space for more buildings, skip this placement
                    if not has_neighbor and tower_b_count == 0 and len(buildings) < max_buildings - 1:
                        consecutive_failures += 1
                        if consecutive_failures > 50:
                            # Force place anyway if we're stuck
                            buildings.append(new_building)
                            consecutive_failures = 0
                        continue
                
                buildings.append(new_building)
                consecutive_failures = 0
        
        return buildings
    
    def generate_single_layout(self, max_buildings: int = 15, 
                              max_attempts: int = 2000,
                              tower_a_probability: float = 0.5) -> List[Building]:
        """
        Generate a single layout using random placement (original method)
        
        Args:
            max_buildings: Target number of buildings to place
            max_attempts: Maximum placement attempts
            tower_a_probability: Probability of choosing Tower A (0.0 to 1.0)
            
        Returns:
            List of placed buildings
        """
        buildings = []
        attempts = 0
        
        while len(buildings) < max_buildings and attempts < max_attempts:
            attempts += 1
            
            # Randomly choose building type
            building_type = 'A' if random.random() < tower_a_probability else 'B'
            
            # Generate random position
            x, y = self.generate_random_position(building_type)
            
            # Create building
            new_building = BuildingType.create_building(building_type, x, y)
            
            # Check if valid placement
            if self.is_valid_placement(new_building, buildings):
                buildings.append(new_building)
        
        return buildings
    
    def score_layout(self, buildings: List[Building], 
                    rules: Dict[str, bool]) -> float:
        """
        Score a layout based on building count and rule compliance
        
        Args:
            buildings: List of buildings in layout
            rules: Dictionary of rule satisfaction results
            
        Returns:
            Score (higher is better)
        """
        # Base score from building count
        score = len(buildings) * 10
        
        # Add bonus for rule compliance
        rule_weights = {
            'inside_site': 50,
            'building_distance': 50,
            'site_distance': 50,
            'neighbor_mix': 100,  # Most important rule
            'plaza_clear': 50
        }
        
        for rule, passed in rules.items():
            if passed:
                score += rule_weights.get(rule, 0)
        
        return score
    
    def generate_multiple_layouts(self, num_layouts: int = 4,
                                  max_buildings: int = 15,
                                  use_improved: bool = True) -> List[Layout]:
        """
        Generate multiple layouts and return them sorted by score
        
        Args:
            num_layouts: Number of layouts to generate
            max_buildings: Target buildings per layout
            use_improved: Use improved algorithm with neighbor mix awareness
            
        Returns:
            List of Layout objects sorted by score (best first)
        """
        layouts = []
        
        print(f"Generating {num_layouts} layouts...")
        
        for i in range(num_layouts):
            # Generate buildings using improved or standard method
            if use_improved:
                buildings = self.generate_single_layout_improved(max_buildings=max_buildings)
            else:
                buildings = self.generate_single_layout(max_buildings=max_buildings)
            
            # Validate rules
            rules = self.validator.validate_layout(buildings)
            
            # Calculate score
            score = self.score_layout(buildings, rules)
            
            # Create layout object
            layout = Layout(buildings, rules, score)
            layouts.append(layout)
            
            # Progress indicator
            status = "✓ VALID" if all(rules.values()) else "✗ VIOLATIONS"
            print(f"  Layout {i+1}: {len(buildings)} buildings, score {score:.0f} [{status}]")
        
        # Sort by score (highest first)
        layouts.sort(key=lambda x: x.score, reverse=True)
        
        print("Generation complete!\n")
        
        return layouts
    
    def generate_optimized_layout(self, num_candidates: int = 20) -> Layout:
        """
        Generate multiple candidate layouts and return the best one
        
        Args:
            num_candidates: Number of candidate layouts to try
            
        Returns:
            Best layout found
        """
        print(f"Optimizing layout (trying {num_candidates} candidates)...")
        
        layouts = self.generate_multiple_layouts(num_layouts=num_candidates, use_improved=True)
        best_layout = layouts[0]
        
        print(f"Best layout: {len(best_layout.buildings)} buildings, "
              f"score {best_layout.score:.0f}")
        
        return best_layout