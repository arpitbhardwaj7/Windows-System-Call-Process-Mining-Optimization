import pandas as pd
import pm4py
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import numpy as np

class SystemCallProcessMiner:
    def __init__(self):
        self.raw_data = None
        self.event_log = None
        self.filtered_log = None
        self.process_models = {}
        self.statistics = {}
        
    def load_data(self, csv_file):
        """Load and validate the system call event log"""
        print(f"Loading data from {csv_file}...")
        
        try:
            self.raw_data = pd.read_csv(csv_file)
            print(f"✅ Loaded {len(self.raw_data):,} events")
            
            # Validate required columns
            required_cols = ['case_id', 'activity', 'timestamp', 'resource']
            missing_cols = [col for col in required_cols if col not in self.raw_data.columns]
            
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")
                
            print("✅ Data validation passed")
            self._show_data_overview()
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            raise
            
    def _show_data_overview(self):
        """Display overview of the loaded data"""
        print("\n=== Data Overview ===")
        print(f"Date range: {self.raw_data['timestamp'].min()} to {self.raw_data['timestamp'].max()}")
        print(f"Unique cases: {self.raw_data['case_id'].nunique():,}")
        print(f"Unique activities: {self.raw_data['activity'].nunique()}")
        print(f"Unique resources: {self.raw_data['resource'].nunique()}")
        
        print("\n=== Top Activities ===")
        print(self.raw_data['activity'].value_counts().head())
        
        print("\n=== Resource Distribution ===")
        print(self.raw_data['resource'].value_counts())
        
    def preprocess_data(self, min_case_length=5, max_case_length=500, activity_threshold=10):
        """
        Preprocess the data for process mining
        
        Parameters:
        - min_case_length: Minimum number of events per case
        - max_case_length: Maximum number of events per case  
        - activity_threshold: Minimum frequency for activities to include
        """
        print("\n=== Data Preprocessing ===")
        
        # Convert timestamp to datetime
        self.raw_data['timestamp'] = pd.to_datetime(self.raw_data['timestamp'])
        
        # Sort by case and timestamp
        self.raw_data = self.raw_data.sort_values(['case_id', 'timestamp'])
        
        # Remove cases that are too short or too long
        case_lengths = self.raw_data.groupby('case_id').size()
        valid_cases = case_lengths[(case_lengths >= min_case_length) & 
                                  (case_lengths <= max_case_length)].index
        
        initial_cases = self.raw_data['case_id'].nunique()
        self.raw_data = self.raw_data[self.raw_data['case_id'].isin(valid_cases)]
        
        print(f"Filtered cases by length: {initial_cases:,} → {len(valid_cases):,}")
        
        # Remove rare activities (noise reduction)
        activity_counts = self.raw_data['activity'].value_counts()
        frequent_activities = activity_counts[activity_counts >= activity_threshold].index
        
        initial_activities = self.raw_data['activity'].nunique()
        self.raw_data = self.raw_data[self.raw_data['activity'].isin(frequent_activities)]
        
        print(f"Filtered activities by frequency: {initial_activities} → {len(frequent_activities)}")
        
        # Create pm4py compatible format
        self.raw_data['case:concept:name'] = self.raw_data['case_id']
        self.raw_data['concept:name'] = self.raw_data['activity']
        self.raw_data['time:timestamp'] = self.raw_data['timestamp']
        
        print(f"✅ Preprocessing complete: {len(self.raw_data):,} events remaining")
        
    def convert_to_event_log(self):
        """Convert preprocessed data to pm4py event log format"""
        print("\n=== Converting to Event Log Format ===")
        
        try:
            # Convert to pm4py event log
            self.event_log = pm4py.convert_to_event_log(self.raw_data)
            
            print(f"✅ Event log created with {len(self.event_log)} cases")
            
            # Calculate basic statistics
            self._calculate_basic_statistics()
            
        except Exception as e:
            print(f"❌ Error converting to event log: {e}")
            raise
            
    def _calculate_basic_statistics(self):
        """Calculate and store basic process statistics"""
        print("\n=== Basic Process Statistics ===")
        
        # Basic event log statistics
        self.statistics['total_cases'] = len(self.event_log)
        self.statistics['total_events'] = sum(len(trace) for trace in self.event_log)
        self.statistics['avg_case_length'] = self.statistics['total_events'] / self.statistics['total_cases']
        
        # Activity statistics
        activities = set()
        for trace in self.event_log:
            for event in trace:
                activities.add(event['concept:name'])
        self.statistics['unique_activities'] = len(activities)
        
        # Duration statistics (if duration available)
        if 'duration_ms' in self.raw_data.columns:
            self.statistics['avg_duration'] = self.raw_data['duration_ms'].mean()
            self.statistics['total_duration'] = self.raw_data['duration_ms'].sum()
        
        print(f"Total cases: {self.statistics['total_cases']:,}")
        print(f"Total events: {self.statistics['total_events']:,}")
        print(f"Average case length: {self.statistics['avg_case_length']:.1f}")
        print(f"Unique activities: {self.statistics['unique_activities']}")
        
        # Case length distribution
        case_lengths = [len(trace) for trace in self.event_log]
        print(f"Case length - Min: {min(case_lengths)}, Max: {max(case_lengths)}, Median: {sorted(case_lengths)[len(case_lengths)//2]}")
        
        return self.statistics
        
    def discover_processes(self, algorithms=['inductive', 'alpha', 'heuristic']):
        """
        Discover process models using different algorithms
        
        Parameters:
        - algorithms: List of algorithms to use ['inductive', 'alpha', 'heuristic']
        """
        print("\n=== Process Discovery ===")
        
        if self.event_log is None:
            raise ValueError("Event log not loaded. Call convert_to_event_log() first.")
        
        for algorithm in algorithms:
            print(f"\nApplying {algorithm.title()} Miner...")
            
            try:
                if algorithm == 'inductive':
                    # Inductive Miner - good for complex processes
                    net, initial_marking, final_marking = pm4py.discover_petri_net_inductive(self.event_log)
                    self.process_models[algorithm] = {
                        'type': 'petri_net',
                        'model': (net, initial_marking, final_marking)
                    }
                    
                elif algorithm == 'alpha':
                    # Alpha Miner - good for simple, structured processes
                    net, initial_marking, final_marking = pm4py.discover_petri_net_alpha(self.event_log)
                    self.process_models[algorithm] = {
                        'type': 'petri_net',
                        'model': (net, initial_marking, final_marking)
                    }
                    
                elif algorithm == 'heuristic':
                    # Heuristics Miner - handles noise well
                    heu_net = pm4py.discover_heuristics_net(self.event_log)
                    self.process_models[algorithm] = {
                        'type': 'heuristic_net',
                        'model': heu_net
                    }
                
                print(f"✅ {algorithm.title()} model discovered successfully")
                
            except Exception as e:
                print(f"❌ Error with {algorithm} miner: {e}")
                
        print(f"\n✅ Process discovery complete. Generated {len(self.process_models)} models.")
        
    def visualize_processes(self, save_dir="process_models"):
        """Visualize discovered process models"""
        print(f"\n=== Visualizing Process Models ===")
        
        import os
        os.makedirs(save_dir, exist_ok=True)
        
        for algorithm, model_data in self.process_models.items():
            print(f"Visualizing {algorithm} model...")
            
            try:
                if model_data['type'] == 'petri_net':
                    net, initial_marking, final_marking = model_data['model']
                    gviz = pm4py.vis.view_petri_net(net, initial_marking, final_marking, format="png")
                    
                elif model_data['type'] == 'heuristic_net':
                    gviz = pm4py.vis.view_heuristics_net(model_data['model'], format="png")
                
                # Save visualization with absolute path
                output_path = os.path.abspath(f"{save_dir}/{algorithm}_process_model")
                gviz.render(output_path, format='png', cleanup=True)
                
                print(f"✅ Saved {algorithm} model to {output_path}.png")
                
            except Exception as e:
                print(f"❌ Error visualizing {algorithm} model: {e}")
                print("Note: Visualization requires Graphviz to be installed on your system")
                
    def analyze_process_variants(self, top_n=10):
        """Analyze most common process variants"""
        print(f"\n=== Process Variant Analysis ===")
        
        if self.event_log is None:
            raise ValueError("Event log not loaded.")
            
        # Get trace variants
        variants = pm4py.get_variants(self.event_log)
        
        # Convert to list format for easier handling
        variants_list = []
        for variant, cases in variants.items():
            variants_list.append({
                'variant': ' → '.join(variant),
                'count': len(cases)
            })
        
        variants_sorted = sorted(variants_list, key=lambda x: x['count'], reverse=True)
        
        print(f"Total variants: {len(variants_sorted)}")
        print(f"Top {min(top_n, len(variants_sorted))} variants:")
        
        for i, variant in enumerate(variants_sorted[:top_n]):
            print(f"{i+1:2d}. {variant['variant']} (Count: {variant['count']})")
            
        # Calculate variant coverage
        total_cases = len(self.event_log)
        top_10_coverage = sum(v['count'] for v in variants_sorted[:10]) / total_cases * 100
        
        print(f"\nTop 10 variants cover {top_10_coverage:.1f}% of all cases")
        
        return variants_sorted
        
    def identify_bottlenecks(self):
        """Identify potential bottlenecks in the process"""
        print(f"\n=== Bottleneck Analysis ===")
        
        if 'duration_ms' not in self.raw_data.columns:
            print("❌ Duration data not available for bottleneck analysis")
            return
            
        # Activity-level bottlenecks
        activity_performance = self.raw_data.groupby('activity')['duration_ms'].agg([
            'count', 'mean', 'median', 'std', 'max'
        ]).sort_values('mean', ascending=False)
        
        print("=== Activity Performance (Top Slowest) ===")
        print(activity_performance.head(10))
        
        # Resource-level bottlenecks
        resource_performance = self.raw_data.groupby('resource')['duration_ms'].agg([
            'count', 'mean', 'median', 'std', 'max'
        ]).sort_values('mean', ascending=False)
        
        print("\n=== Resource Performance ===")
        print(resource_performance)
        
        # Combined bottlenecks (resource + activity)
        combined_performance = self.raw_data.groupby(['resource', 'activity'])['duration_ms'].agg([
            'count', 'mean', 'median'
        ]).sort_values('mean', ascending=False)
        
        print("\n=== Combined Bottlenecks (Resource + Activity) ===")
        print(combined_performance.head(15))
        
        # Statistical bottleneck detection
        duration_threshold = self.raw_data['duration_ms'].quantile(0.95)  # 95th percentile
        bottleneck_events = self.raw_data[self.raw_data['duration_ms'] > duration_threshold]
        
        print(f"\n=== Statistical Bottlenecks (>{duration_threshold:.1f}ms) ===")
        print(f"Bottleneck events: {len(bottleneck_events):,} ({len(bottleneck_events)/len(self.raw_data)*100:.1f}%)")
        
        bottleneck_activities = bottleneck_events['activity'].value_counts()
        print("Most problematic activities:")
        print(bottleneck_activities.head(10))
        
        return {
            'activity_performance': activity_performance,
            'resource_performance': resource_performance,
            'combined_performance': combined_performance,
            'bottleneck_events': bottleneck_events
        }
        
    def generate_summary_report(self):
        """Generate a comprehensive summary report"""
        print(f"\n" + "="*60)
        print("SYSTEM CALL PROCESS MINING SUMMARY REPORT")
        print("="*60)
        
        print(f"\n📊 DATASET OVERVIEW")
        print(f"Total Events: {self.statistics.get('total_events', 'N/A'):,}")
        print(f"Total Cases: {self.statistics.get('total_cases', 'N/A'):,}")
        print(f"Unique Activities: {self.statistics.get('unique_activities', 'N/A')}")
        print(f"Average Case Length: {self.statistics.get('avg_case_length', 'N/A'):.1f}")
        
        print(f"\n🔍 PROCESS MODELS DISCOVERED")
        for algorithm in self.process_models.keys():
            print(f"✅ {algorithm.title()} Miner")
            
        print(f"\n📈 PERFORMANCE INSIGHTS")
        if 'avg_duration' in self.statistics:
            print(f"Average Event Duration: {self.statistics['avg_duration']:.2f}ms")
            print(f"Total Processing Time: {self.statistics['total_duration']/1000:.1f} seconds")
            
        print(f"\n🎯 NEXT STEPS")
        print("1. Examine process visualizations in 'process_models/' directory")
        print("2. Analyze bottleneck patterns identified above")
        print("3. Design optimization experiments based on findings")
        print("4. Validate improvements with new data collection")

def main():
    """Main execution function"""
    print("🔧 System Call Process Mining Pipeline")
    print("=====================================")
    
    # Initialize the process miner
    miner = SystemCallProcessMiner()
    
    # Get CSV file name
    csv_file = input("Enter CSV file name (or press Enter for 'system_call_log_large_250000_events.csv'): ").strip()
    if not csv_file:
        csv_file = 'system_call_log_large_250000_events.csv'
    
    try:
        # Phase 3.1: Data Processing Pipeline
        miner.load_data(csv_file)
        miner.preprocess_data(min_case_length=5, max_case_length=200)
        miner.convert_to_event_log()
        
        # Phase 3.2: Process Discovery
        miner.discover_processes(['inductive', 'heuristic'])  # Skip alpha for large datasets
        
        # Phase 3.3: Process Analysis
        miner.analyze_process_variants(top_n=15)
        bottlenecks = miner.identify_bottlenecks()
        
        # Visualization
        miner.visualize_processes()
        
        # Final report
        miner.generate_summary_report()
        
        print(f"\n✅ Process mining pipeline completed successfully!")
        print(f"Check the 'process_models/' directory for visualizations.")
        
        return miner
        
    except FileNotFoundError:
        print(f"❌ File '{csv_file}' not found. Please generate the dataset first.")
    except Exception as e:
        print(f"❌ Error in process mining pipeline: {e}")
        raise

if __name__ == "__main__":
    miner = main()