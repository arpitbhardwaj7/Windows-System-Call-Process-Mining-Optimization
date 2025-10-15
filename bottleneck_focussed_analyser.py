import pandas as pd
import pm4py
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import os

class BottleneckAnalyzer:
    def __init__(self):
        self.raw_data = None
        self.bottleneck_data = None
        self.bottleneck_log = None
        self.analysis_results = {}
        
    def load_data(self, csv_file):
        """Load the system call event log"""
        print(f"Loading data from {csv_file}...")
        
        try:
            self.raw_data = pd.read_csv(csv_file)
            self.raw_data['timestamp'] = pd.to_datetime(self.raw_data['timestamp'])
            print(f"✅ Loaded {len(self.raw_data):,} events")
            
            if 'duration_ms' not in self.raw_data.columns:
                raise ValueError("Duration data required for bottleneck analysis")
                
            self._initial_bottleneck_overview()
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            raise
            
    def _initial_bottleneck_overview(self):
        """Show initial overview of potential bottlenecks"""
        print("\n=== Initial Bottleneck Overview ===")
        
        # Basic duration statistics
        duration_stats = self.raw_data['duration_ms'].describe()
        print("Duration Statistics (ms):")
        for stat, value in duration_stats.items():
            print(f"  {stat}: {value:.2f}")
            
        # Identify threshold for bottlenecks
        p95_threshold = self.raw_data['duration_ms'].quantile(0.95)
        p99_threshold = self.raw_data['duration_ms'].quantile(0.99)
        
        p95_count = len(self.raw_data[self.raw_data['duration_ms'] > p95_threshold])
        p99_count = len(self.raw_data[self.raw_data['duration_ms'] > p99_threshold])
        
        print(f"\nBottleneck Candidates:")
        print(f"  95th percentile (>{p95_threshold:.1f}ms): {p95_count:,} events ({p95_count/len(self.raw_data)*100:.2f}%)")
        print(f"  99th percentile (>{p99_threshold:.1f}ms): {p99_count:,} events ({p99_count/len(self.raw_data)*100:.2f}%)")
        
    def identify_bottlenecks(self, threshold_percentile=95, min_frequency=10):
        """
        Identify bottlenecks using statistical analysis
        
        Parameters:
        - threshold_percentile: Percentile above which events are considered slow
        - min_frequency: Minimum frequency for an activity to be considered
        """
        print(f"\n=== Identifying Bottlenecks (>{threshold_percentile}th percentile) ===")
        
        # Calculate threshold
        threshold = self.raw_data['duration_ms'].quantile(threshold_percentile / 100)
        print(f"Bottleneck threshold: {threshold:.2f}ms")
        
        # Extract bottleneck events
        self.bottleneck_data = self.raw_data[self.raw_data['duration_ms'] > threshold].copy()
        
        print(f"Identified {len(self.bottleneck_data):,} bottleneck events ({len(self.bottleneck_data)/len(self.raw_data)*100:.2f}%)")
        
        # Analyze bottlenecks by different dimensions
        self._analyze_bottleneck_patterns()
        
        # Create filtered event log focusing on bottleneck sequences
        self._create_bottleneck_event_log()
        
    def _analyze_bottleneck_patterns(self):
        """Analyze patterns in bottleneck events"""
        print("\n=== Bottleneck Pattern Analysis ===")
        
        # 1. By Activity
        activity_bottlenecks = self.bottleneck_data.groupby('activity').agg({
            'duration_ms': ['count', 'mean', 'median', 'std', 'max'],
            'case_id': 'nunique'
        }).round(2)
        activity_bottlenecks.columns = ['Count', 'Mean_Duration', 'Median_Duration', 'Std_Duration', 'Max_Duration', 'Affected_Cases']
        activity_bottlenecks = activity_bottlenecks.sort_values('Count', ascending=False)
        
        print("🎯 Top Bottleneck Activities:")
        print(activity_bottlenecks.head(10))
        
        # 2. By Resource (Process)
        resource_bottlenecks = self.bottleneck_data.groupby('resource').agg({
            'duration_ms': ['count', 'mean', 'median', 'max'],
            'case_id': 'nunique'
        }).round(2)
        resource_bottlenecks.columns = ['Count', 'Mean_Duration', 'Median_Duration', 'Max_Duration', 'Affected_Cases']
        resource_bottlenecks = resource_bottlenecks.sort_values('Count', ascending=False)
        
        print("\n🎯 Bottlenecks by Process:")
        print(resource_bottlenecks)
        
        # 3. Combined (Resource + Activity)
        combined_bottlenecks = self.bottleneck_data.groupby(['resource', 'activity']).agg({
            'duration_ms': ['count', 'mean', 'median'],
            'case_id': 'nunique'
        }).round(2)
        combined_bottlenecks.columns = ['Count', 'Mean_Duration', 'Median_Duration', 'Affected_Cases']
        combined_bottlenecks = combined_bottlenecks.sort_values('Count', ascending=False)
        
        print("\n🎯 Top Combined Bottlenecks (Process + Activity):")
        print(combined_bottlenecks.head(15))
        
        # 4. Temporal patterns
        self.bottleneck_data['hour'] = self.bottleneck_data['timestamp'].dt.hour
        hourly_bottlenecks = self.bottleneck_data.groupby('hour').size()
        
        print(f"\n🕐 Bottleneck Peak Hours:")
        top_hours = hourly_bottlenecks.nlargest(3)
        for hour, count in top_hours.items():
            print(f"  {hour:02d}:00 - {count} bottleneck events")
            
        # Store results
        self.analysis_results = {
            'activity_bottlenecks': activity_bottlenecks,
            'resource_bottlenecks': resource_bottlenecks,
            'combined_bottlenecks': combined_bottlenecks,
            'hourly_bottlenecks': hourly_bottlenecks
        }
        
    def _create_bottleneck_event_log(self):
        """Create event log focusing on cases with bottlenecks"""
        print("\n=== Creating Bottleneck-Focused Event Log ===")
        
        # Get cases that contain bottleneck events
        bottleneck_case_ids = self.bottleneck_data['case_id'].unique()
        
        # Extract all events from these cases (not just bottleneck events)
        bottleneck_cases_data = self.raw_data[self.raw_data['case_id'].isin(bottleneck_case_ids)].copy()
        
        print(f"Cases with bottlenecks: {len(bottleneck_case_ids):,}")
        print(f"Total events in these cases: {len(bottleneck_cases_data):,}")
        
        # Add bottleneck flag
        bottleneck_cases_data['is_bottleneck'] = bottleneck_cases_data.apply(
            lambda row: 'BOTTLENECK' if row['duration_ms'] > self.raw_data['duration_ms'].quantile(0.95) else 'NORMAL',
            axis=1
        )
        
        # Prepare for pm4py
        bottleneck_cases_data['case:concept:name'] = bottleneck_cases_data['case_id']
        bottleneck_cases_data['concept:name'] = bottleneck_cases_data['activity'] + '_' + bottleneck_cases_data['is_bottleneck']
        bottleneck_cases_data['time:timestamp'] = bottleneck_cases_data['timestamp']
        
        # Convert to event log
        self.bottleneck_log = pm4py.convert_to_event_log(bottleneck_cases_data)
        print(f"✅ Bottleneck event log created with {len(self.bottleneck_log)} cases")
        
    def discover_bottleneck_processes(self):
        """Discover process models highlighting bottleneck patterns"""
        if self.bottleneck_log is None:
            raise ValueError("Bottleneck event log not created. Call identify_bottlenecks() first.")
            
        print(f"\n=== Bottleneck Process Discovery ===")
        
        try:
            # Create output directory
            output_dir = "bottleneck_analysis"
            os.makedirs(output_dir, exist_ok=True)
            
            # Discover process model
            net, initial_marking, final_marking = pm4py.discover_petri_net_inductive(self.bottleneck_log)
            
            # Visualize bottleneck process
            gviz = pm4py.vis.view_petri_net(net, initial_marking, final_marking, format="png")
            output_path = f"{output_dir}/bottleneck_process_model"
            gviz.render(output_path, format='png', cleanup=True)
            
            print(f"✅ Bottleneck process model saved to {output_path}.png")
            
            # Create simplified view for each major bottleneck type
            self._create_bottleneck_type_models()
            
            return net, initial_marking, final_marking
            
        except Exception as e:
            print(f"❌ Error in bottleneck process discovery: {e}")
            return None, None, None
            
    def _create_bottleneck_type_models(self):
        """Create separate models for different types of bottlenecks"""
        print("\n=== Creating Bottleneck Type Models ===")
        
        output_dir = "bottleneck_analysis"
        
        # Get top 3 bottleneck activities
        top_bottleneck_activities = self.analysis_results['activity_bottlenecks'].head(3).index
        
        for activity in top_bottleneck_activities:
            try:
                # Filter data for this specific bottleneck activity
                activity_data = self.raw_data[
                    (self.raw_data['activity'] == activity) & 
                    (self.raw_data['duration_ms'] > self.raw_data['duration_ms'].quantile(0.90))
                ].copy()
                
                if len(activity_data) < 10:  # Skip if too few events
                    continue
                    
                # Get cases with this bottleneck
                case_ids = activity_data['case_id'].unique()
                case_data = self.raw_data[self.raw_data['case_id'].isin(case_ids)].copy()
                
                # Prepare for pm4py
                case_data['case:concept:name'] = case_data['case_id']
                case_data['concept:name'] = case_data['activity']
                case_data['time:timestamp'] = case_data['timestamp']
                
                # Convert to event log
                activity_log = pm4py.convert_to_event_log(case_data)
                
                # Discover model
                net, im, fm = pm4py.discover_petri_net_inductive(activity_log)
                
                # Visualize
                gviz = pm4py.vis.view_petri_net(net, im, fm, format="png")
                output_path = f"{output_dir}/bottleneck_{activity.replace('/', '_')}_model"
                gviz.render(output_path, format='png', cleanup=True)
                
                print(f"✅ {activity} bottleneck model saved to {output_path}.png")
                
            except Exception as e:
                print(f"⚠️  Could not create model for {activity}: {e}")
                
    def analyze_bottleneck_impact(self):
        """Analyze the impact of bottlenecks on overall system performance"""
        print(f"\n=== Bottleneck Impact Analysis ===")
        
        # Calculate impact metrics
        total_time = self.raw_data['duration_ms'].sum()
        bottleneck_time = self.bottleneck_data['duration_ms'].sum()
        impact_percentage = (bottleneck_time / total_time) * 100
        
        print(f"💥 PERFORMANCE IMPACT")
        print(f"Total system time: {total_time/1000:.1f} seconds")
        print(f"Bottleneck time: {bottleneck_time/1000:.1f} seconds")
        print(f"Bottleneck impact: {impact_percentage:.1f}% of total time")
        
        # Case-level impact
        total_cases = self.raw_data['case_id'].nunique()
        affected_cases = self.bottleneck_data['case_id'].nunique()
        case_impact = (affected_cases / total_cases) * 100
        
        print(f"\n📊 CASE IMPACT")
        print(f"Total cases: {total_cases:,}")
        print(f"Cases affected by bottlenecks: {affected_cases:,}")
        print(f"Case impact: {case_impact:.1f}% of cases affected")
        
        # Frequency impact
        frequency_impact = (len(self.bottleneck_data) / len(self.raw_data)) * 100
        
        print(f"\n📈 FREQUENCY IMPACT")
        print(f"Bottleneck events: {len(self.bottleneck_data):,} out of {len(self.raw_data):,}")
        print(f"Frequency impact: {frequency_impact:.2f}% of events are bottlenecks")
        
        return {
            'time_impact': impact_percentage,
            'case_impact': case_impact,
            'frequency_impact': frequency_impact
        }
        
    def suggest_optimizations(self):
        """Suggest specific optimizations based on bottleneck analysis"""
        print(f"\n=== Optimization Suggestions ===")
        
        top_bottlenecks = self.analysis_results['combined_bottlenecks'].head(5)
        
        suggestions = {
            ('guardian.exe', 'ReadFile'): [
                "🔧 Enable file scanning cache to avoid re-scanning recently checked files",
                "🔧 Implement asynchronous file scanning to avoid blocking operations",
                "🔧 Exclude system files and known safe directories from deep scanning",
                "🔧 Use file reputation databases for faster threat assessment"
            ],
            ('guardian.exe', 'WaitForSingleObject'): [
                "🔧 Optimize thread pool size to reduce waiting times",
                "🔧 Implement lock-free data structures where possible",
                "🔧 Use asynchronous I/O operations to reduce thread blocking",
                "🔧 Profile and optimize critical sections in antivirus engine"
            ],
            ('chrome.exe', 'VirtualAlloc'): [
                "🔧 Implement memory pooling to reduce allocation overhead",
                "🔧 Tune garbage collection settings for better performance",
                "🔧 Use memory-mapped files for large data structures",
                "🔧 Enable memory compression features"
            ],
            ('explorer.exe', 'RegQueryValue'): [
                "🔧 Cache frequently accessed registry values",
                "🔧 Batch registry operations where possible",
                "🔧 Use registry notification APIs instead of polling",
                "🔧 Optimize registry hive locations and structure"
            ],
            ('system', 'CreateProcess'): [
                "🔧 Implement process pooling for frequently launched applications",
                "🔧 Optimize DLL loading through prebinding",
                "🔧 Use application prefetching mechanisms",
                "🔧 Reduce startup dependencies and optimize initialization"
            ]
        }
        
        print("🎯 TOP OPTIMIZATION OPPORTUNITIES:")
        for i, (index, row) in enumerate(top_bottlenecks.iterrows()):
            resource, activity = index
            print(f"\n{i+1}. {resource} - {activity}")
            print(f"   Impact: {row['Count']} events, {row['Mean_Duration']:.1f}ms average")
            
            key = (resource, activity)
            if key in suggestions:
                for suggestion in suggestions[key]:
                    print(f"   {suggestion}")
            else:
                print(f"   🔧 Profile {activity} operation in {resource}")
                print(f"   🔧 Implement caching for {activity} results")
                print(f"   🔧 Consider asynchronous execution of {activity}")
                
        print(f"\n💡 GENERAL OPTIMIZATION STRATEGIES:")
        print("🔧 Implement operation prioritization (critical vs non-critical)")
        print("🔧 Use batch processing for similar operations")
        print("🔧 Implement adaptive timeouts based on system load")
        print("🔧 Add performance monitoring and alerting")
        print("🔧 Use SSD storage for frequently accessed files")
        
    def create_bottleneck_visualizations(self):
        """Create comprehensive visualizations for bottleneck analysis"""
        output_dir = "bottleneck_analysis"
        os.makedirs(output_dir, exist_ok=True)
        
        # Set plotting style
        plt.style.use('default')
        sns.set_palette("rocket")
        
        # 1. Bottleneck distribution by activity
        plt.figure(figsize=(15, 10))
        
        plt.subplot(2, 3, 1)
        top_activities = self.analysis_results['activity_bottlenecks'].head(8)
        plt.barh(range(len(top_activities)), top_activities['Count'])
        plt.yticks(range(len(top_activities)), top_activities.index)
        plt.xlabel('Bottleneck Count')
        plt.title('Top Bottleneck Activities')
        plt.gca().invert_yaxis()
        
        # 2. Duration vs Frequency scatter
        plt.subplot(2, 3, 2)
        activity_stats = self.analysis_results['activity_bottlenecks']
        plt.scatter(activity_stats['Count'], activity_stats['Mean_Duration'], 
                   s=activity_stats['Affected_Cases']*2, alpha=0.6)
        plt.xlabel('Frequency (Count)')
        plt.ylabel('Mean Duration (ms)')
        plt.title('Duration vs Frequency\n(Size = Affected Cases)')
        
        # 3. Bottlenecks by process
        plt.subplot(2, 3, 3)
        resource_stats = self.analysis_results['resource_bottlenecks']
        plt.pie(resource_stats['Count'], labels=resource_stats.index, autopct='%1.1f%%')
        plt.title('Bottlenecks by Process')
        
        # 4. Hourly bottleneck pattern
        plt.subplot(2, 3, 4)
        hourly_data = self.analysis_results['hourly_bottlenecks']
        plt.plot(hourly_data.index, hourly_data.values, marker='o', linewidth=2)
        plt.xlabel('Hour of Day')
        plt.ylabel('Bottleneck Events')
        plt.title('Bottleneck Timeline (24-hour)')
        plt.grid(True, alpha=0.3)
        
        # 5. Duration distribution comparison
        plt.subplot(2, 3, 5)
        plt.hist(self.raw_data['duration_ms'], bins=50, alpha=0.5, label='All Events', density=True)
        plt.hist(self.bottleneck_data['duration_ms'], bins=50, alpha=0.7, label='Bottlenecks', density=True)
        plt.xlabel('Duration (ms)')
        plt.ylabel('Density')
        plt.title('Duration Distribution')
        plt.legend()
        plt.yscale('log')
        
        # 6. Impact analysis
        plt.subplot(2, 3, 6)
        impact_data = self.analyze_bottleneck_impact()
        impacts = ['Time Impact', 'Case Impact', 'Frequency Impact']
        values = [impact_data['time_impact'], impact_data['case_impact'], impact_data['frequency_impact']]
        colors = ['red', 'orange', 'yellow']
        bars = plt.bar(impacts, values, color=colors, alpha=0.7)
        plt.ylabel('Impact (%)')
        plt.title('Bottleneck Impact Analysis')
        plt.xticks(rotation=45)
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                    f'{value:.1f}%', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/bottleneck_analysis_dashboard.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Create detailed heatmap
        plt.figure(figsize=(12, 8))
        
        # Bottleneck heatmap by process and activity
        bottleneck_pivot = self.bottleneck_data.groupby(['resource', 'activity']).size().reset_index(name='count')
        heatmap_data = bottleneck_pivot.pivot(index='resource', columns='activity', values='count').fillna(0)
        
        sns.heatmap(heatmap_data, annot=True, fmt='.0f', cmap='Reds', cbar_kws={'label': 'Bottleneck Count'})
        plt.title('Bottleneck Heatmap: Process vs Activity')
        plt.xlabel('Activity')
        plt.ylabel('Process')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f'{output_dir}/bottleneck_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Bottleneck visualizations saved in {output_dir}/")
        
    def generate_bottleneck_report(self):
        """Generate comprehensive bottleneck analysis report"""
        print(f"\n" + "="*70)
        print("BOTTLENECK ANALYSIS REPORT")
        print("="*70)
        
        impact_data = self.analyze_bottleneck_impact()
        
        print(f"\n📊 EXECUTIVE SUMMARY")
        print(f"Total Events Analyzed: {len(self.raw_data):,}")
        print(f"Bottleneck Events: {len(self.bottleneck_data):,}")
        print(f"Performance Impact: {impact_data['time_impact']:.1f}% of total execution time")
        print(f"System Coverage: {impact_data['case_impact']:.1f}% of processes affected")
        
        print(f"\n🎯 TOP 5 BOTTLENECK SOURCES")
        top_5 = self.analysis_results['combined_bottlenecks'].head(5)
        for i, (index, row) in enumerate(top_5.iterrows()):
            resource, activity = index
            print(f"{i+1}. {resource} → {activity}")
            print(f"   Events: {row['Count']}, Avg Duration: {row['Mean_Duration']:.1f}ms")
            
        print(f"\n🔥 CRITICAL FINDINGS")
        worst_bottleneck = self.analysis_results['combined_bottlenecks'].iloc[0]
        worst_resource, worst_activity = self.analysis_results['combined_bottlenecks'].index[0]
        print(f"• Worst bottleneck: {worst_resource} → {worst_activity}")
        print(f"  ({worst_bottleneck['Count']} events, {worst_bottleneck['Mean_Duration']:.1f}ms avg)")
        
        peak_hour = self.analysis_results['hourly_bottlenecks'].idxmax()
        peak_count = self.analysis_results['hourly_bottlenecks'].max()
        print(f"• Peak bottleneck time: {peak_hour:02d}:00 ({peak_count} events)")
        
        worst_process = self.analysis_results['resource_bottlenecks'].iloc[0]
        worst_process_name = self.analysis_results['resource_bottlenecks'].index[0]
        print(f"• Most problematic process: {worst_process_name}")
        print(f"  ({worst_process['Count']} bottleneck events)")
        
        print(f"\n📁 GENERATED OUTPUTS")
        print("• bottleneck_analysis/bottleneck_process_model.png - Overall bottleneck flow")
        print("• bottleneck_analysis/bottleneck_*_model.png - Individual bottleneck models")
        print("• bottleneck_analysis/bottleneck_analysis_dashboard.png - Summary charts")
        print("• bottleneck_analysis/bottleneck_heatmap.png - Process vs Activity heatmap")
        
        print(f"\n🚀 NEXT STEPS")
        print("1. Focus optimization efforts on top 3 bottlenecks identified above")
        print("2. Implement suggested optimizations from the analysis")
        print("3. Monitor peak hours for targeted performance improvements")
        print("4. Re-run analysis after optimizations to measure improvements")

def main():
    analyzer = BottleneckAnalyzer()
    
    # Get CSV file
    csv_file = input("Enter CSV file name (or press Enter for default): ").strip()
    if not csv_file:
        csv_file = 'system_call_log_large_373828_events.csv'
    
    try:
        # Load data
        analyzer.load_data(csv_file)
        
        # Get threshold preference
        threshold = input("Enter bottleneck threshold percentile (or press Enter for 95): ").strip()
        threshold = int(threshold) if threshold else 95
        
        print(f"\n🔍 Running bottleneck analysis (>{threshold}th percentile)...")
        
        # Run complete bottleneck analysis
        analyzer.identify_bottlenecks(threshold_percentile=threshold)
        analyzer.discover_bottleneck_processes()
        analyzer.suggest_optimizations()
        analyzer.create_bottleneck_visualizations()
        analyzer.generate_bottleneck_report()
        
        print(f"\n✅ Bottleneck analysis completed!")
        print(f"Check the 'bottleneck_analysis/' directory for all outputs.")
        
    except FileNotFoundError:
        print(f"❌ File '{csv_file}' not found.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()