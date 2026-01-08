"""
visualizer.py
Visualization of building layouts using matplotlib
"""

import matplotlib.pyplot as plt # type: ignore
import matplotlib.patches as patches # type: ignore
from typing import List
from building import Building
from generator import Layout
from site_config import SiteConfig


class LayoutVisualizer:
    """Visualizes building layouts using matplotlib"""
    
    def __init__(self, config: SiteConfig = None):
        """
        Initialize visualizer with configuration
        
        Args:
            config: Site configuration (uses default if None)
        """
        self.config = config or SiteConfig()
        
        # Color scheme
        self.colors = {
            'site_bg': 'lightgray',
            'site_border': 'black',
            'plaza': 'yellow',
            'plaza_border': 'orange',
            'tower_a': 'royalblue',
            'tower_a_border': 'darkblue',
            'tower_b': 'mediumseagreen',
            'tower_b_border': 'darkgreen',
            'text_white': 'white',
            'text_black': 'black'
        }
    
    def draw_site_boundary(self, ax: plt.Axes):
        """Draw the site boundary"""
        site_boundary = patches.Rectangle(
            (0, 0),
            self.config.SITE_WIDTH,
            self.config.SITE_HEIGHT,
            linewidth=2,
            edgecolor=self.colors['site_border'],
            facecolor=self.colors['site_bg'],
            alpha=0.2
        )
        ax.add_patch(site_boundary)
    
    def draw_plaza(self, ax: plt.Axes):
        """Draw the central plaza"""
        plaza = patches.Rectangle(
            (self.config.PLAZA_X, self.config.PLAZA_Y),
            self.config.PLAZA_SIZE,
            self.config.PLAZA_SIZE,
            linewidth=2,
            edgecolor=self.colors['plaza_border'],
            facecolor=self.colors['plaza'],
            alpha=0.4
        )
        ax.add_patch(plaza)
        
        # Add label
        ax.text(
            self.config.PLAZA_X + self.config.PLAZA_SIZE / 2,
            self.config.PLAZA_Y + self.config.PLAZA_SIZE / 2,
            'PLAZA',
            ha='center',
            va='center',
            fontsize=10,
            fontweight='bold',
            color=self.colors['text_black']
        )
    
    def draw_building(self, ax: plt.Axes, building: Building):
        """Draw a single building"""
        # Determine colors based on building type
        if building.building_type == 'A':
            face_color = self.colors['tower_a']
            edge_color = self.colors['tower_a_border']
        else:  # 'B'
            face_color = self.colors['tower_b']
            edge_color = self.colors['tower_b_border']
        
        # Draw rectangle
        rect = patches.Rectangle(
            (building.x, building.y),
            building.width,
            building.height,
            linewidth=2,
            edgecolor=edge_color,
            facecolor=face_color,
            alpha=0.7
        )
        ax.add_patch(rect)
        
        # Add label
        cx, cy = building.center
        ax.text(
            cx, cy,
            f'T{building.building_type}',
            ha='center',
            va='center',
            fontsize=9,
            color=self.colors['text_white'],
            fontweight='bold'
        )
    
    def add_statistics_box(self, ax: plt.Axes, layout: Layout):
        """Add statistics text box to the plot"""
        stats_text = (
            f"Tower A: {layout.get_tower_count('A')}\n"
            f"Tower B: {layout.get_tower_count('B')}\n"
            f"Total: {len(layout.buildings)}\n"
            f"Area: {layout.get_total_area():.0f} m²"
        )
        
        ax.text(
            0.02, 0.98,
            stats_text,
            transform=ax.transAxes,
            fontsize=9,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        )
    
    def add_rules_box(self, ax: plt.Axes, layout: Layout):
        """Add rule compliance box to the plot"""
        rule_names = {
            'inside_site': 'Inside Site',
            'building_distance': 'Bldg Dist (15m)',
            'site_distance': 'Site Dist (10m)',
            'neighbor_mix': 'Neighbor Mix',
            'plaza_clear': 'Plaza Clear'
        }
        
        rule_lines = []
        for rule_key, rule_name in rule_names.items():
            status = '✓' if layout.rules_satisfied[rule_key] else '✗'
            rule_lines.append(f"{status} {rule_name}")
        
        rule_text = "Rules:\n" + "\n".join(rule_lines)
        
        ax.text(
            0.98, 0.98,
            rule_text,
            transform=ax.transAxes,
            fontsize=8,
            verticalalignment='top',
            horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8)
        )
    
    def visualize_layout(self, layout: Layout, layout_num: int, ax: plt.Axes):
        """
        Visualize a single layout on given axes
        
        Args:
            layout: Layout object to visualize
            layout_num: Layout number for title
            ax: Matplotlib axes to draw on
        """
        # Set up the plot
        ax.set_xlim(0, self.config.SITE_WIDTH)
        ax.set_ylim(0, self.config.SITE_HEIGHT)
        ax.set_aspect('equal')
        ax.set_xlabel('Width (m)', fontsize=10)
        ax.set_ylabel('Height (m)', fontsize=10)
        
        # Title with score and validation status
        all_passed = all(layout.rules_satisfied.values())
        title_color = 'green' if all_passed else 'red'
        ax.set_title(
            f'Layout {layout_num} - Score: {layout.score:.0f}',
            fontsize=12,
            fontweight='bold',
            color=title_color
        )
        
        # Draw site boundary
        self.draw_site_boundary(ax)
        
        # Draw central plaza
        self.draw_plaza(ax)
        
        # Draw all buildings
        for building in layout.buildings:
            self.draw_building(ax, building)
        
        # Add information boxes
        self.add_statistics_box(ax, layout)
        self.add_rules_box(ax, layout)
        
        # Add grid
        ax.grid(True, alpha=0.3)
    
    def visualize_multiple_layouts(self, layouts: List[Layout], 
                                   save_path: str = None,
                                   show_plot: bool = True):
        """
        Visualize multiple layouts in a grid
        
        Args:
            layouts: List of Layout objects to visualize
            save_path: Path to save figure (optional)
            show_plot: Whether to display the plot window
        """
        num_layouts = len(layouts)
        
        # Create figure with subplots (2x2 grid)
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(
            'Building Layout Generator - Random Search Algorithm',
            fontsize=16,
            fontweight='bold'
        )
        
        axes = axes.flatten()
        
        # Visualize each layout
        for i, layout in enumerate(layouts[:4]):  # Only show first 4
            self.visualize_layout(layout, i + 1, axes[i])
        
        # Hide unused subplots if fewer than 4 layouts
        for i in range(num_layouts, 4):
            axes[i].axis('off')
        
        plt.tight_layout()
        
        # Save if path provided
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"✓ Layout saved to: {save_path}")
        
        # Show plot
        if show_plot:
            plt.show()
    
    def visualize_single_layout(self, layout: Layout, 
                               save_path: str = None,
                               show_plot: bool = True):
        """
        Visualize a single layout in full size
        
        Args:
            layout: Layout object to visualize
            save_path: Path to save figure (optional)
            show_plot: Whether to display the plot window
        """
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        
        self.visualize_layout(layout, 1, ax)
        
        plt.tight_layout()
        
        # Save if path provided
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"✓ Layout saved to: {save_path}")
        
        # Show plot
        if show_plot:
            plt.show()
    
    def compare_layouts(self, layouts: List[Layout], 
                       save_path: str = None):
        """
        Create a comparison view of multiple layouts
        
        Args:
            layouts: List of Layout objects to compare
            save_path: Path to save figure (optional)
        """
        num_layouts = min(len(layouts), 4)
        
        fig, axes = plt.subplots(1, num_layouts, figsize=(5*num_layouts, 5))
        
        if num_layouts == 1:
            axes = [axes]
        
        fig.suptitle('Layout Comparison', fontsize=14, fontweight='bold')
        
        for i, layout in enumerate(layouts[:num_layouts]):
            self.visualize_layout(layout, i + 1, axes[i])
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"✓ Comparison saved to: {save_path}")
        
        plt.show()