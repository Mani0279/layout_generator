"""
main.py
Entry point for the Building Layout Generator

This program automatically generates building layouts on a 200m × 140m site
while respecting geometric placement rules using a random search algorithm.
"""

from site_config import SiteConfig
from generator import LayoutGenerator
from visualizer import LayoutVisualizer


def print_header():
    """Print program header"""
    print("=" * 70)
    print("Building Layout Generator")
    print("=" * 70)


def print_configuration(config: SiteConfig):
    """Print site and building configuration"""
    print("\nSite Configuration:")
    print(f"  Site Size: {config.SITE_WIDTH}m × {config.SITE_HEIGHT}m")
    print(f"  Tower A: {config.TOWER_A_WIDTH}m × {config.TOWER_A_HEIGHT}m")
    print(f"  Tower B: {config.TOWER_B_WIDTH}m × {config.TOWER_B_HEIGHT}m")
    print(f"  Central Plaza: {config.PLAZA_SIZE}m × {config.PLAZA_SIZE}m")
    
    print("\nPlacement Rules:")
    print(f"  1. Buildings fully inside site")
    print(f"  2. Min distance between buildings: {config.MIN_BUILDING_DISTANCE}m")
    print(f"  3. Min distance from site edge: {config.MIN_SITE_DISTANCE}m")
    print(f"  4. Each Tower A needs Tower B within {config.NEIGHBOR_DISTANCE}m")
    print(f"  5. No buildings in central plaza")
    
    print("\n" + "=" * 70)


def print_layout_summary(layouts):
    """Print summary of generated layouts"""
    print(f"\nGenerated {len(layouts)} layouts:")
    print("-" * 70)
    
    for i, layout in enumerate(layouts, 1):
        all_rules_passed = all(layout.rules_satisfied.values())
        status = "✓ VALID" if all_rules_passed else "✗ VIOLATIONS"
        
        print(f"\nLayout {i} [{status}] - Score: {layout.score:.0f}")
        print(f"  Buildings: {len(layout.buildings)} total "
              f"(Tower A: {layout.get_tower_count('A')}, "
              f"Tower B: {layout.get_tower_count('B')})")
        print(f"  Total Area: {layout.get_total_area():.0f} m²")
        print(f"  Rules: ", end="")
        
        for rule_name, passed in layout.rules_satisfied.items():
            symbol = "✓" if passed else "✗"
            print(f"{symbol} {rule_name.replace('_', ' ').title()} ", end="")
        print()


def main():
    """Main execution function"""
    # Print header
    print_header()
    
    # Create configuration
    config = SiteConfig()
    
    # Print configuration
    print_configuration(config)
    
    # Create generator
    generator = LayoutGenerator(config)
    
    # Generate multiple layouts
    print("\nGenerating layouts using Improved Random Search algorithm...")
    print("-" * 70)
    
    # Use improved algorithm with neighbor mix awareness
    layouts = generator.generate_multiple_layouts(
        num_layouts=4, 
        max_buildings=15,
        use_improved=True  # Use improved algorithm
    )
    
    # Print summary
    print_layout_summary(layouts)
    
    print("\n" + "=" * 70)
    print("\nVisualizing layouts...")
    
    # Create visualizer
    visualizer = LayoutVisualizer(config)
    
    # Visualize all layouts
    visualizer.visualize_multiple_layouts(
        layouts,
        save_path='building_layouts.png',
        show_plot=True
    )
    
    print("\n" + "=" * 70)
    print("✓ Done! Close the plot window to exit.")
    print("=" * 70)


if __name__ == "__main__":
    main()