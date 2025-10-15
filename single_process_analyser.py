import pandas as pd
import pm4py
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

class SingleProcessAnalyzer:
    def __init__(self):
        self.raw_data = None
        self.filtered_data = None
        self.event_log = None
        self.selected_process = None
        self.process_stats = {}
        
    def load_data(self, csv_file):
        """Load the system call event log"""
        print(f"Loading data from {csv_file}...")
        
        try:
            self.raw_data = pd.read_csv(csv_file)
            self.raw_data['timestamp'] = pd.to_datetime(self.raw_data['timestamp'])
            print(f"✅ Loaded {len(self.raw_data):,} events")
            
            # Show available processes
            self._show_available_processes()
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            raise
            
    def _show_available_processes(self):
        """Display available processes for selection"""
        print("\n=== Available Processes ===")
        process_stats = self.raw_data.groupby('resource').agg({
            'case_id': 'nunique',
            'activity': 'count',
            'duration_ms': ['mean', 'sum']
        }).round(2)
        
        process_stats.columns = ['Sessions', 'Total_Events', 'Avg_Duration_ms', 'Total_Time_ms']
        process_stats = process_stats.sort_values('Total_Events', ascending=False)
        
        print(process_stats)
        print("\nProcess descriptions:")
        descriptions = {
            'guardian.exe': 'Antivirus software - file scanning, threat detection',
            'chrome.exe': 'Web browser - memory intensive, multi-threaded',
            'notepad.exe': 'Text editor - simple file operations',
            'explorer.exe': 'File manager - registry and file system operations',
            'system': 'System processes - low-level OS operations'
        }
        
        for process in process_stats.index:
            desc = descriptions.get(process, 'Unknown process')
            print(f"  {process}: {desc}")
            
    def select_process(self, process_name=None):
        """Select a specific process for analysis"""
        if process_name is None:
            available_processes = self.raw_data['resource'].unique()
            print(f"\nAvailable processes: {list(available_processes)}")
            process_name = input("Enter process name to analyze: ").strip()
            
        if process_name not in self.raw_data['resource'].values:
            raise ValueError(f"Process '{process_name}' not found in data")
            
        self.selected_process = process_name
        self.filtered_data = self.raw_data[self.raw_data['resource'] == process_name].copy()
        
        print(f"\n=== Selected Process: {process_name} ===")
        print(f"Total events: {len(self.filtered_data):,}")
        print(f"Unique sessions: {self.filtered_data['case_id'].nunique():,}")
        print(f"Time span: {self.filtered_data['timestamp'].min()} to {self.filtered_data['timestamp'].max()}")
        
        # Prepare for pm4py
        self.filtered_data['case:concept:name'] = self.filtered_data['case_id']
        self.filtered_data['concept:name'] = self.filtered_data['activity']
        self.filtered_data['time:timestamp'] = self.filtered_data['timestamp']
        
        # Convert to event log
        self.event_log = pm4py.convert_to_event_log(self.filtered_data)
        print(f"✅ Created event log with {len(self.event_log)} cases")
        
    def analyze_process_behavior(self):
        """Analyze the selected process behavior in detail"""
        if self.selected_process is None:
            raise ValueError("No process selected. Call select_process() first.")
            
        print(f"\n=== {self.selected_process} Behavior Analysis ===")
        
        # Activity frequency analysis
        activity_stats = self.filtered_data.groupby('activity').agg({
            'duration_ms': ['count', 'mean', 'median', 'std', 'min', 'max'],
            'case_id': 'nunique'
        }).round(2)
        
        activity_stats.columns = ['Count', 'Mean_Duration', 'Median_Duration', 'Std_Duration', 'Min_Duration', 'Max_Duration', 'Cases_Used']
        activity_stats = activity_stats.sort_values('Count', ascending=False)
        
        print("\n📊 Activity Statistics:")
        print(activity_stats)
        
        # Temporal patterns
        self.filtered_data['hour'] = self.filtered_data['timestamp'].dt.hour
        hourly_activity = self.filtered_data.groupby('hour').size()
        
        print(f"\n🕐 Most active hour: {hourly_activity.idxmax()}:00 ({hourly_activity.max()} events)")
        print(f"🕐 Least active hour: {hourly_activity.idxmin()}:00 ({hourly_activity.min()} events)")
        
        # Performance patterns
        if 'duration_ms' in self.filtered_data.columns:
            slow_operations = self.filtered_data[self.filtered_data['duration_ms'] > self.filtered_data['duration_ms'].quantile(0.95)]
            print(f"\n⚠️  Slow operations (95th percentile): {len(slow_operations)} events")
            print("Top slow activities:")
            print(slow_operations['activity'].value_counts().head())
            
        self.process_stats = {
            'activity_stats': activity_stats,
            'hourly_activity': hourly_activity,
            'slow_operations': slow_operations if 'duration_ms' in self.filtered_data.columns else None
        }
        
    def discover_process_model(self):
        """Discover process model for the selected process"""
        if self.event_log is None:
            raise ValueError("Event log not created. Call select_process() first.")
            
        print(f"\n=== Process Discovery for {self.selected_process} ===")
        
        try:
            # Use Inductive Miner (best for single process)
            net, initial_marking, final_marking = pm4py.discover_petri_net_inductive(self.event_log)
            
            # Create output directory
            output_dir = f"single_process_analysis/{self.selected_process.replace('.exe', '')}"
            os.makedirs(output_dir, exist_ok=True)
            
            # Visualize and save
            gviz = pm4py.vis.view_petri_net(net, initial_marking, final_marking, format="png")
            output_path = f"{output_dir}/process_model"
            gviz.render(output_path, format='png', cleanup=True)
            
            print(f"✅ Process model saved to {output_path}.png")
            
            # Also try BPMN for better readability
            try:
                bpmn_model = pm4py.convert_to_bpmn(net, initial_marking, final_marking)
                gviz_bpmn = pm4py.vis.view_bpmn(bpmn_model, format="png")
                bpmn_path = f"{output_dir}/process_model_bpmn"
                gviz_bpmn.render(bpmn_path, format='png', cleanup=True)
                print(f"✅ BPMN model saved to {bpmn_path}.png")
            except:
                print("⚠️  BPMN conversion not available")
            
            return net, initial_marking, final_marking
            
        except Exception as e:
            print(f"❌ Error in process discovery: {e}")
            return None, None, None
            
    def analyze_variants(self, top_n=10):
        """Analyze process variants for the selected process"""
        print(f"\n=== Process Variants for {self.selected_process} ===")
        
        variants = pm4py.get_variants(self.event_log)
        
        # Convert to list for easier handling
        variants_list = []
        for variant, cases in variants.items():
            variants_list.append({
                'variant': ' → '.join(variant),
                'count': len(cases),
                'percentage': len(cases) / len(self.event_log) * 100
            })
        
        variants_sorted = sorted(variants_list, key=lambda x: x['count'], reverse=True)
        
        print(f"Total variants: {len(variants_sorted)}")
        print(f"\nTop {min(top_n, len(variants_sorted))} variants:")
        
        for i, variant in enumerate(variants_sorted[:top_n]):
            print(f"{i+1:2d}. {variant['variant']}")
            print(f"    Count: {variant['count']} ({variant['percentage']:.1f}%)")
            print()
            
        # Coverage analysis
        top_5_coverage = sum(v['count'] for v in variants_sorted[:5]) / len(self.event_log) * 100
        top_10_coverage = sum(v['count'] for v in variants_sorted[:10]) / len(self.event_log) * 100
        
        print(f"📊 Top 5 variants cover {top_5_coverage:.1f}% of cases")
        print(f"📊 Top 10 variants cover {top_10_coverage:.1f}% of cases")
        
        return variants_sorted
        
    def create_visualizations(self):
        """Create helpful visualizations for the selected process"""
        if self.selected_process is None:
            raise ValueError("No process selected.")
            
        output_dir = f"single_process_analysis/{self.selected_process.replace('.exe', '')}"
        os.makedirs(output_dir, exist_ok=True)
        
        # Set up plotting style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # 1. Activity frequency chart
        plt.figure(figsize=(12, 6))
        activity_counts = self.filtered_data['activity'].value_counts()
        plt.subplot(1, 2, 1)
        activity_counts.plot(kind='bar')
        plt.title(f'{self.selected_process} - Activity Frequency')
        plt.xlabel('Activity')
        plt.ylabel('Count')
        plt.xticks(rotation=45)
        
        # 2. Duration distribution
        if 'duration_ms' in self.filtered_data.columns:
            plt.subplot(1, 2, 2)
            self.filtered_data['duration_ms'].hist(bins=50)
            plt.title(f'{self.selected_process} - Duration Distribution')
            plt.xlabel('Duration (ms)')
            plt.ylabel('Frequency')
            
        plt.tight_layout()
        plt.savefig(f'{output_dir}/activity_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. Timeline activity
        plt.figure(figsize=(14, 6))
        hourly_activity = self.filtered_data.groupby(self.filtered_data['timestamp'].dt.hour).size()
        plt.plot(hourly_activity.index, hourly_activity.values, marker='o')
        plt.title(f'{self.selected_process} - Activity Timeline (24-hour)')
        plt.xlabel('Hour of Day')
        plt.ylabel('Number of Events')
        plt.grid(True, alpha=0.3)
        plt.savefig(f'{output_dir}/timeline_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Visualizations saved in {output_dir}/")
        
    def generate_process_report(self):
        """Generate a comprehensive report for the selected process"""
        if self.selected_process is None:
            raise ValueError("No process selected.")
            
        output_dir = f"single_process_analysis/{self.selected_process.replace('.exe', '')}"
        
        print(f"\n" + "="*60)
        print(f"SINGLE PROCESS ANALYSIS REPORT: {self.selected_process.upper()}")
        print("="*60)
        
        print(f"\n📊 OVERVIEW")
        print(f"Total Events: {len(self.filtered_data):,}")
        print(f"Unique Sessions: {self.filtered_data['case_id'].nunique():,}")
        print(f"Unique Activities: {self.filtered_data['activity'].nunique()}")
        print(f"Average Events per Session: {len(self.filtered_data) / self.filtered_data['case_id'].nunique():.1f}")
        
        if 'duration_ms' in self.filtered_data.columns:
            print(f"Average Duration: {self.filtered_data['duration_ms'].mean():.2f}ms")
            print(f"Total Processing Time: {self.filtered_data['duration_ms'].sum() / 1000:.1f} seconds")
            
        print(f"\n🎯 KEY FINDINGS")
        most_common_activity = self.filtered_data['activity'].value_counts().index[0]
        most_common_count = self.filtered_data['activity'].value_counts().iloc[0]
        print(f"Most Common Activity: {most_common_activity} ({most_common_count:,} times)")
        
        if 'duration_ms' in self.filtered_data.columns:
            slowest_activity = self.filtered_data.groupby('activity')['duration_ms'].mean().idxmax()
            slowest_duration = self.filtered_data.groupby('activity')['duration_ms'].mean().max()
            print(f"Slowest Activity: {slowest_activity} ({slowest_duration:.2f}ms avg)")
            
        print(f"\n📁 OUTPUT FILES")
        print(f"Process Model: {output_dir}/process_model.png")
        print(f"BPMN Model: {output_dir}/process_model_bpmn.png (if available)")
        print(f"Activity Charts: {output_dir}/activity_analysis.png")
        print(f"Timeline Chart: {output_dir}/timeline_analysis.png")

def main():
    analyzer = SingleProcessAnalyzer()
    
    # Get CSV file
    csv_file = input("Enter CSV file name (or press Enter for default): ").strip()
    if not csv_file:
        csv_file = 'system_call_log_large_373828_events.csv'
    
    try:
        # Load data and show options
        analyzer.load_data(csv_file)
        
        # Let user select process
        analyzer.select_process()
        
        # Run complete analysis
        print("\n🔍 Running comprehensive analysis...")
        analyzer.analyze_process_behavior()
        analyzer.discover_process_model()
        analyzer.analyze_variants(top_n=15)
        analyzer.create_visualizations()
        analyzer.generate_process_report()
        
        print(f"\n✅ Single process analysis completed!")
        print(f"Check the 'single_process_analysis/{analyzer.selected_process.replace('.exe', '')}/' directory for all outputs.")
        
    except FileNotFoundError:
        print(f"❌ File '{csv_file}' not found.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()