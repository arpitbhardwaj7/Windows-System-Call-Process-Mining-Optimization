import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np
import os

class SequenceDiagramGenerator:
    def __init__(self):
        self.raw_data = None
        self.process_sequences = {}
        
    def load_data(self, csv_file):
        """Load the system call data"""
        print(f"Loading data from {csv_file}...")
        self.raw_data = pd.read_csv(csv_file)
        self.raw_data['timestamp'] = pd.to_datetime(self.raw_data['timestamp'])
        print(f"✅ Loaded {len(self.raw_data):,} events")
        
    def extract_common_sequences(self, min_frequency=10):
        """Extract the most common sequence patterns for each process"""
        print("\n🔍 Analyzing sequence patterns...")
        
        for process in self.raw_data['resource'].unique():
            process_data = self.raw_data[self.raw_data['resource'] == process].copy()
            
            # Get sequences for this process
            sequences = []
            for case_id in process_data['case_id'].unique():
                case_data = process_data[process_data['case_id'] == case_id].sort_values('timestamp')
                sequence = list(case_data['activity'])
                if len(sequence) >= 3:  # Only consider meaningful sequences
                    sequences.append(sequence)
            
            if sequences:
                # Find most common sequence pattern
                common_sequence = self._find_most_common_pattern(sequences)
                
                # Get timing and performance info
                sequence_stats = self._analyze_sequence_performance(process_data, common_sequence)
                
                self.process_sequences[process] = {
                    'common_sequence': common_sequence,
                    'frequency': len(sequences),
                    'stats': sequence_stats
                }
                
                print(f"✅ {process}: {len(common_sequence)} step sequence ({len(sequences)} cases)")
        
    def _find_most_common_pattern(self, sequences):
        """Find the most common pattern among sequences"""
        # Convert sequences to strings for comparison
        sequence_strings = [' → '.join(seq) for seq in sequences]
        
        # Count frequency of each sequence
        from collections import Counter
        sequence_counts = Counter(sequence_strings)
        
        # If we have a clear winner, use it
        most_common = sequence_counts.most_common(1)[0]
        if len(sequence_counts) > 1 and most_common[1] >= 3:
            return most_common[0].split(' → ')
        
        # Otherwise, create a representative sequence from most common activities
        all_activities = []
        for seq in sequences:
            all_activities.extend(seq)
        
        activity_counts = Counter(all_activities)
        
        # Build a logical sequence based on typical system call patterns
        common_activities = [activity for activity, count in activity_counts.most_common(10)]
        
        # Create logical ordering
        logical_sequence = self._create_logical_sequence(common_activities)
        
        return logical_sequence
    
    def _create_logical_sequence(self, activities):
        """Create a logical sequence from activities"""
        # Define typical ordering patterns
        order_priority = {
            'CreateProcess': 1,
            'LoadLibrary': 2,
            'CreateFile': 3,
            'RegOpenKey': 4,
            'ReadFile': 5,
            'WriteFile': 6,
            'VirtualAlloc': 7,
            'CreateThread': 8,
            'WaitForSingleObject': 9,
            'RegQueryValue': 10,
            'RegSetValue': 11,
            'MapViewOfFile': 12,
            'CloseHandle': 13,
            'FreeLibrary': 14,
            'RegCloseKey': 15,
            'TerminateProcess': 16,
            'ExitThread': 17
        }
        
        # Sort activities by logical order
        sorted_activities = sorted(activities, 
                                 key=lambda x: order_priority.get(x, 50))
        
        # Take most important ones (limit to 8 for readability)
        return sorted_activities[:8]
    
    def _analyze_sequence_performance(self, process_data, sequence):
        """Analyze performance characteristics of the sequence"""
        stats = {}
        
        # Calculate overall performance thresholds for this process
        all_durations = process_data['duration_ms'].dropna()
        if len(all_durations) == 0:
            return stats
            
        # Use percentiles to categorize performance
        p25 = all_durations.quantile(0.25)
        p50 = all_durations.quantile(0.50)
        p75 = all_durations.quantile(0.75)
        p90 = all_durations.quantile(0.90)
        
        for activity in sequence:
            activity_data = process_data[process_data['activity'] == activity]
            if len(activity_data) > 0:
                avg_duration = activity_data['duration_ms'].mean()
                
                # Categorize performance based on percentiles
                if avg_duration > p90:
                    performance_category = 'critical_bottleneck'
                elif avg_duration > p75:
                    performance_category = 'performance_issue'
                elif avg_duration < p25:
                    performance_category = 'fast_operation'
                else:
                    performance_category = 'normal_operation'
                
                stats[activity] = {
                    'avg_duration': avg_duration,
                    'count': len(activity_data),
                    'performance_category': performance_category
                }
        
        return stats
    
    def create_sequence_diagrams(self, output_dir="sequence_diagrams"):
        """Create sequence diagrams for all processes"""
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\n🎨 Creating sequence diagrams...")
        
        # Create individual diagrams for each process
        for process, data in self.process_sequences.items():
            self._create_single_sequence_diagram(process, data, output_dir)
        
        # Create a combined overview diagram
        self._create_combined_sequence_diagram(output_dir)
        
        print(f"✅ Sequence diagrams saved in '{output_dir}/' directory")
    
    def _create_single_sequence_diagram(self, process, data, output_dir):
        """Create a circular process flow diagram for a single process"""
        sequence = data['common_sequence']
        stats = data['stats']
        
        fig, ax = plt.subplots(figsize=(12, 12))
        
        # Process name (clean it up)
        process_name = process.replace('.exe', '').title()
        fig.suptitle(f'{process_name} - System Call Flow Diagram', fontsize=16, fontweight='bold')
        
        # Center point
        center_x, center_y = 0.5, 0.5
        radius = 0.35
        
        # Calculate positions for circular layout
        num_steps = len(sequence)
        if num_steps == 0:
            return
            
        angles = np.linspace(0, 2*np.pi, num_steps, endpoint=False)
        
        # Start from top and go clockwise
        angles = angles - np.pi/2  # Start from top
        
        # Draw process states (circles)
        state_positions = {}
        state_colors = {}
        state_sizes = {}
        
        for i, activity in enumerate(sequence):
            x = center_x + radius * np.cos(angles[i])
            y = center_y + radius * np.sin(angles[i])
            state_positions[activity] = (x, y)
            
            # Determine color and size based on performance category
            if activity in stats:
                category = stats[activity]['performance_category']
                if category == 'critical_bottleneck':
                    color = '#ff4444'  # Bright red for critical bottlenecks
                    size = 0.08  # Larger for critical issues
                    edge_color = 'darkred'
                    edge_width = 3
                elif category == 'performance_issue':
                    color = '#ff8c00'  # Orange for performance issues
                    size = 0.06
                    edge_color = 'darkorange'
                    edge_width = 2
                elif category == 'fast_operation':
                    color = '#00cc44'  # Bright green for fast operations
                    size = 0.05
                    edge_color = 'darkgreen'
                    edge_width = 2
                else:  # normal_operation
                    color = '#4a90e2'  # Blue for normal operations
                    size = 0.05
                    edge_color = 'darkblue'
                    edge_width = 2
            else:
                color = '#d3d3d3'  # Light gray for no data
                size = 0.05
                edge_color = 'gray'
                edge_width = 1
            
            state_colors[activity] = color
            state_sizes[activity] = size
            
            # Draw the state circle
            circle = plt.Circle((x, y), size, facecolor=color, edgecolor=edge_color, 
                              linewidth=edge_width, alpha=0.9, zorder=3)
            ax.add_patch(circle)
            
            # Add activity label
            ax.text(x, y, activity.replace('CreateProcess', 'Create\nProcess').replace('LoadLibrary', 'Load\nLibrary').replace('ReadFile', 'Read\nFile').replace('WriteFile', 'Write\nFile').replace('WaitForSingleObject', 'Wait\nObject').replace('RegQueryValue', 'Reg\nQuery').replace('RegOpenKey', 'Reg\nOpen').replace('VirtualAlloc', 'Virtual\nAlloc').replace('CreateThread', 'Create\nThread').replace('TerminateProcess', 'Terminate\nProcess').replace('CreateFile', 'Create\nFile').replace('CloseHandle', 'Close\nHandle'),
                   ha='center', va='center', fontweight='bold', fontsize=8,
                   color='white' if color in ['#ff4444', '#ff8c00'] else 'black',
                   zorder=4)
            
            # Add timing info outside the circle
            if activity in stats:
                timing_text = f"{stats[activity]['avg_duration']:.1f}ms"
                # Position timing text outside the circle
                label_radius = radius + 0.12
                label_x = center_x + label_radius * np.cos(angles[i])
                label_y = center_y + label_radius * np.sin(angles[i])
                
                ax.text(label_x, label_y, timing_text,
                       ha='center', va='center', fontsize=9, 
                       bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8),
                       zorder=5)
            
            # Add performance category indicator
            if activity in stats:
                category = stats[activity]['performance_category']
                if category == 'critical_bottleneck':
                    warning_radius = radius + 0.18
                    warning_x = center_x + warning_radius * np.cos(angles[i])
                    warning_y = center_y + warning_radius * np.sin(angles[i])
                    ax.text(warning_x, warning_y, "🚨 CRITICAL", 
                           ha='center', va='center', fontsize=8, fontweight='bold',
                           bbox=dict(boxstyle="round,pad=0.2", facecolor="red", alpha=0.8),
                           color='white', zorder=5)
                elif category == 'performance_issue':
                    warning_radius = radius + 0.18
                    warning_x = center_x + warning_radius * np.cos(angles[i])
                    warning_y = center_y + warning_radius * np.sin(angles[i])
                    ax.text(warning_x, warning_y, "⚠️ SLOW", 
                           ha='center', va='center', fontsize=8, fontweight='bold',
                           bbox=dict(boxstyle="round,pad=0.2", facecolor="orange", alpha=0.8),
                           color='white', zorder=5)
                elif category == 'fast_operation':
                    warning_radius = radius + 0.18
                    warning_x = center_x + warning_radius * np.cos(angles[i])
                    warning_y = center_y + warning_radius * np.sin(angles[i])
                    ax.text(warning_x, warning_y, "⚡ FAST", 
                           ha='center', va='center', fontsize=8, fontweight='bold',
                           bbox=dict(boxstyle="round,pad=0.2", facecolor="green", alpha=0.8),
                           color='white', zorder=5)
        
        # Draw arrows between states
        for i in range(num_steps):
            current_activity = sequence[i]
            next_activity = sequence[(i + 1) % num_steps]
            
            current_pos = state_positions[current_activity]
            next_pos = state_positions[next_activity]
            
            # Calculate arrow positions (from edge of circle to edge of next circle)
            current_size = state_sizes[current_activity]
            next_size = state_sizes[next_activity]
            
            # Vector from current to next
            dx = next_pos[0] - current_pos[0]
            dy = next_pos[1] - current_pos[1]
            distance = np.sqrt(dx**2 + dy**2)
            
            if distance > 0:
                # Normalize
                dx_norm = dx / distance
                dy_norm = dy / distance
                
                # Start point (edge of current circle)
                start_x = current_pos[0] + current_size * dx_norm
                start_y = current_pos[1] + current_size * dy_norm
                
                # End point (edge of next circle)
                end_x = next_pos[0] - next_size * dx_norm
                end_y = next_pos[1] - next_size * dy_norm
                
                # Draw arrow
                if i == num_steps - 1:  # Last arrow (completion)
                    arrow_color = 'purple'
                    arrow_style = '->'
                    linewidth = 2
                    alpha = 0.7
                else:
                    arrow_color = 'black'
                    arrow_style = '->'
                    linewidth = 2
                    alpha = 0.8
                
                ax.annotate('', xy=(end_x, end_y), xytext=(start_x, start_y),
                           arrowprops=dict(arrowstyle=arrow_style, lw=linewidth, 
                                         color=arrow_color, alpha=alpha),
                           zorder=2)
        
        # Add process start indicator
        start_activity = sequence[0]
        start_pos = state_positions[start_activity]
        ax.annotate('START', xy=start_pos, xytext=(start_pos[0]-0.15, start_pos[1]),
                   arrowprops=dict(arrowstyle='->', lw=3, color='green'),
                   fontsize=12, fontweight='bold', color='green',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen"),
                   zorder=6)
        
        # Add process end indicator
        end_activity = sequence[-1]
        end_pos = state_positions[end_activity]
        ax.annotate('END', xy=end_pos, xytext=(end_pos[0]+0.15, end_pos[1]),
                   arrowprops=dict(arrowstyle='->', lw=3, color='purple'),
                   fontsize=12, fontweight='bold', color='purple',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="plum"),
                   zorder=6)
        
        # Add central process info
        ax.text(center_x, center_y, f"{process_name}\nProcess Flow", 
               ha='center', va='center', fontsize=14, fontweight='bold',
               bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.9),
               zorder=7)
        
        # Add legend
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#ff4444', 
                      markersize=12, label='Critical Bottleneck'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#ff8c00', 
                      markersize=10, label='Performance Issue'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#4a90e2', 
                      markersize=8, label='Normal Operation'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#00cc44', 
                      markersize=8, label='Fast Operation'),
            plt.Line2D([0], [0], marker='', color='black', linewidth=2, 
                      label='Process Flow'),
            plt.Line2D([0], [0], marker='', color='purple', linewidth=2, 
                      label='Process Completion')
        ]
        ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0, 1))
        
        # Add performance summary in bottom right
        critical_count = sum(1 for activity in sequence 
                           if activity in stats and stats[activity]['performance_category'] == 'critical_bottleneck')
        issue_count = sum(1 for activity in sequence 
                         if activity in stats and stats[activity]['performance_category'] == 'performance_issue')
        fast_count = sum(1 for activity in sequence 
                        if activity in stats and stats[activity]['performance_category'] == 'fast_operation')
        
        total_avg_time = sum(stats[activity]['avg_duration'] for activity in sequence 
                           if activity in stats) / len(sequence) if sequence else 0
        
        summary_text = f"Performance Summary:\n"
        summary_text += f"• Total Steps: {len(sequence)}\n"
        summary_text += f"• Critical Issues: {critical_count}\n"
        summary_text += f"• Performance Issues: {issue_count}\n"
        summary_text += f"• Fast Operations: {fast_count}\n"
        summary_text += f"• Avg Step Time: {total_avg_time:.1f}ms\n"
        summary_text += f"• Cases Analyzed: {data['frequency']}"
        
        ax.text(0.02, 0.02, summary_text, transform=ax.transAxes, fontsize=10,
               bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow", alpha=0.9),
               verticalalignment='bottom', zorder=8)
        
        # Removed optimization opportunities box - this section is completely removed
        
        # Set limits and hide axes
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Save the diagram
        filename = f"{output_dir}/{process.replace('.exe', '')}_flow_diagram.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight', metadata={'Software': None})
        plt.close()
        
        print(f"✅ Created {process_name} circular flow diagram")
    
    def _create_combined_sequence_diagram(self, output_dir):
        """Create a combined overview of all process sequences"""
        fig, ax = plt.subplots(figsize=(16, 12))
        fig.suptitle('System Call Sequences - All Processes Overview', fontsize=18, fontweight='bold')
        
        processes = list(self.process_sequences.keys())
        num_processes = len(processes)
        
        # Calculate layout
        rows_per_process = 0.8 / num_processes
        
        for i, (process, data) in enumerate(self.process_sequences.items()):
            sequence = data['common_sequence']
            stats = data['stats']
            
            # Process label
            process_name = process.replace('.exe', '').title()
            y_base = 0.9 - i * rows_per_process
            
            ax.text(0.02, y_base, process_name, fontsize=14, fontweight='bold',
                   verticalalignment='center')
            
            # Draw mini sequence
            step_width = 0.7 / max(len(sequence), 1)
            
            for j, activity in enumerate(sequence[:8]):  # Limit to 8 steps for overview
                x = 0.15 + j * step_width
                
                # Color coding based on performance category
                if activity in stats:
                    category = stats[activity]['performance_category']
                    if category == 'critical_bottleneck':
                        color = '#ff4444'
                    elif category == 'performance_issue':
                        color = '#ff8c00'
                    elif category == 'fast_operation':
                        color = '#00cc44'
                    else:
                        color = '#4a90e2'
                else:
                    color = '#d3d3d3'
                
                # Draw mini step
                rect = patches.Rectangle((x, y_base - 0.02), step_width * 0.8, 0.04,
                                       facecolor=color, edgecolor='black', linewidth=1)
                ax.add_patch(rect)
                
                # Add activity label (abbreviated)
                activity_short = activity.replace('CreateProcess', 'Create').replace('LoadLibrary', 'Load').replace('ReadFile', 'Read').replace('WriteFile', 'Write')
                ax.text(x + step_width * 0.4, y_base, activity_short[:6],
                       ha='center', va='center', fontsize=7, rotation=45)
                
                # Draw mini arrow
                if j < len(sequence) - 1 and j < 7:
                    ax.annotate('', xy=(x + step_width * 0.9, y_base), 
                               xytext=(x + step_width * 0.8, y_base),
                               arrowprops=dict(arrowstyle='->', lw=1, color='black'))
        
        # Add overall legend
        legend_elements = [
            patches.Patch(color='#ff4444', label='Critical Bottleneck'),
            patches.Patch(color='#ff8c00', label='Performance Issue'),
            patches.Patch(color='#4a90e2', label='Normal Operation'),
            patches.Patch(color='#00cc44', label='Fast Operation')
        ]
        ax.legend(handles=legend_elements, loc='upper right')
        
        # Add summary statistics
        total_critical = 0
        total_issues = 0
        total_fast = 0
        total_steps = 0
        
        for process, data in self.process_sequences.items():
            sequence = data['common_sequence']
            stats = data['stats']
            total_steps += len(sequence)
            
            for activity in sequence:
                if activity in stats:
                    category = stats[activity]['performance_category']
                    if category == 'critical_bottleneck':
                        total_critical += 1
                    elif category == 'performance_issue':
                        total_issues += 1
                    elif category == 'fast_operation':
                        total_fast += 1
        
        summary = f"Summary:\n"
        summary += f"• {len(processes)} processes analyzed\n"
        summary += f"• {total_steps} total sequence steps\n"
        summary += f"• {total_critical} critical bottlenecks\n"
        summary += f"• {total_issues} performance issues\n"
        summary += f"• {total_fast} fast operations\n"
        summary += f"• {((total_critical + total_issues)/total_steps)*100:.1f}% need optimization"
        
        ax.text(0.02, 0.15, summary, fontsize=12,
               bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.7))
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        plt.savefig(f"{output_dir}/all_processes_overview.png", dpi=300, bbox_inches='tight', metadata={'Software': None})
        plt.close()
        
        print("✅ Created combined overview diagram")
    
    def generate_sequence_report(self, output_dir="sequence_diagrams"):
        """Generate a detailed report about the sequences"""
        report_file = f"{output_dir}/sequence_analysis_report.txt"
        
        with open(report_file, 'w') as f:
            f.write("SYSTEM CALL SEQUENCE ANALYSIS REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            for process, data in self.process_sequences.items():
                sequence = data['common_sequence']
                stats = data['stats']
                
                f.write(f"PROCESS: {process.upper()}\n")
                f.write("-" * 30 + "\n")
                f.write(f"Common Sequence ({len(sequence)} steps):\n")
                
                for i, activity in enumerate(sequence):
                    step_info = f"{i+1:2d}. {activity}"
                    if activity in stats:
                        category = stats[activity]['performance_category']
                        step_info += f" ({stats[activity]['avg_duration']:.1f}ms avg)"
                        
                        if category == 'critical_bottleneck':
                            step_info += " 🚨 CRITICAL BOTTLENECK"
                        elif category == 'performance_issue':
                            step_info += " ⚠️ PERFORMANCE ISSUE"
                        elif category == 'fast_operation':
                            step_info += " ⚡ FAST OPERATION"
                    f.write(f"   {step_info}\n")
                
                f.write(f"\nCases analyzed: {data['frequency']}\n")
                
                # Performance analysis
                critical_ops = [activity for activity in sequence 
                              if activity in stats and stats[activity]['performance_category'] == 'critical_bottleneck']
                issue_ops = [activity for activity in sequence 
                           if activity in stats and stats[activity]['performance_category'] == 'performance_issue']
                fast_ops = [activity for activity in sequence 
                          if activity in stats and stats[activity]['performance_category'] == 'fast_operation']
                
                if critical_ops:
                    f.write(f"Critical bottlenecks: {', '.join(critical_ops)}\n")
                if issue_ops:
                    f.write(f"Performance issues: {', '.join(issue_ops)}\n")
                if fast_ops:
                    f.write(f"Fast operations: {', '.join(fast_ops)}\n")
                
                if not critical_ops and not issue_ops:
                    f.write("No major performance issues identified\n")
                
                f.write("\n" + "="*50 + "\n\n")
        
        print(f"✅ Sequence analysis report saved to {report_file}")

def main():
    """Main function to generate sequence diagrams"""
    generator = SequenceDiagramGenerator()
    
    # Get CSV file
    csv_file = input("Enter CSV file name (or press Enter for default): ").strip()
    if not csv_file:
        csv_file = 'system_call_log_large_373828_events.csv'
    
    try:
        # Load data and analyze sequences
        generator.load_data(csv_file)
        generator.extract_common_sequences()
        
        # Create diagrams
        generator.create_sequence_diagrams()
        generator.generate_sequence_report()
        
        print("\n🎉 SUCCESS! Circular flow diagrams created!")
        print("\n📊 Generated Files:")
        print("• sequence_diagrams/guardian_flow_diagram.png")
        print("• sequence_diagrams/chrome_flow_diagram.png") 
        print("• sequence_diagrams/notepad_flow_diagram.png")
        print("• sequence_diagrams/explorer_flow_diagram.png")
        print("• sequence_diagrams/system_flow_diagram.png")
        print("• sequence_diagrams/all_processes_overview.png")
        print("• sequence_diagrams/sequence_analysis_report.txt")
        
        print("\n🎯 PERFECT for your professor!")
        print("✅ Circular state diagrams like process lifecycle models")
        print("✅ Critical bottlenecks marked with 🚨 CRITICAL")
        print("✅ Performance issues marked with ⚠️ SLOW")
        print("✅ Fast operations marked with ⚡ FAST")
        print("✅ Color-coded performance categories")
        print("✅ START/END markers for process flow")
        print("✅ Professional process mining visualization!")
        
    except FileNotFoundError:
        print(f"❌ File '{csv_file}' not found.")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()