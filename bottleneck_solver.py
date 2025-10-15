import pandas as pd
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# LangChain imports - Updated for latest version
from langchain_community.llms import OpenAI, Ollama, HuggingFacePipeline
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.chains import LLMChain
from langchain_community.callbacks.manager import get_openai_callback
from langchain_community.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA

# Google Gemini imports
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
import google.generativeai as genai

class SimpleBottleneckSolver:
    def __init__(self):
        """Initialize with hardcoded Gemini settings"""
        # Hardcoded settings
        self.llm_provider = "gemini"
        self.model_name = "gemini-2.0-flash"
        self.api_key = "AIzaSyB6MCbZPUJlU0enDor0zx7_mrXqkUti4rM"
        self.temperature = 0.7
        self.max_tokens = 4000
        
        self.llm = None
        self.chat_model = None
        self.bottleneck_data = None
        self.solutions = {}
        self.cost_tracking = {}
        
        # Initialize LLM
        self._initialize_llm()
        
        # Initialize prompt templates
        self._setup_prompt_templates()
        
    def _initialize_llm(self):
        """Initialize Gemini with hardcoded settings"""
        try:
            print(f"🌟 Initializing Google Gemini {self.model_name}...")
            
            # Configure Gemini
            genai.configure(api_key=self.api_key)
            
            # Initialize Gemini chat model
            self.chat_model = ChatGoogleGenerativeAI(
                model=self.model_name,
                google_api_key=self.api_key,
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
                convert_system_message_to_human=True
            )
            
            print(f"✅ Google Gemini {self.model_name} ready!")
            
            # Test connection
            try:
                test_response = self.chat_model.invoke([HumanMessage(content="Hello")])
                print("✅ API connection validated")
            except Exception as test_error:
                print(f"❌ API validation failed: {test_error}")
                self.chat_model = None
                
        except Exception as e:
            print(f"❌ Error initializing Gemini: {e}")
            self.chat_model = None
    
    def _setup_prompt_templates(self):
        """Setup prompt templates"""
        self.system_message = """You are an expert system performance engineer with deep expertise in:
- Windows system optimization and performance tuning
- Process mining and bottleneck analysis  
- Enterprise software architecture and scaling
- Cost-benefit analysis for technical solutions
- Project management and implementation planning

Provide detailed, technical, and actionable solutions with realistic time and cost estimates."""

        self.analysis_template = """
# SYSTEM CALL BOTTLENECK ANALYSIS & SOLUTION REQUEST

## SYSTEM OVERVIEW
- **Total Events**: {total_events:,}
- **Bottleneck Events**: {bottleneck_events:,} 
- **Performance Impact**: {performance_impact:.1f}% of total execution time
- **Bottleneck Threshold**: {threshold_ms:.1f}ms
- **Time Lost**: {bottleneck_time:.1f} seconds

## TOP CRITICAL BOTTLENECKS
{critical_combinations}

## TECHNICAL CONTEXT
{system_context}

## REQUEST FOR SOLUTIONS

Provide detailed solutions including:

### 1. TECHNICAL SOLUTIONS
For each major bottleneck:
- Root cause analysis
- Specific technical solutions
- Implementation approach
- Expected performance improvement

### 2. IMPLEMENTATION COSTS & TIMELINE
- Development time (hours/days)
- Team requirements
- Cost breakdown (Dev rates: Senior $100/hr, Mid $75/hr, Junior $50/hr)
- Infrastructure costs
- Risk assessment

### 3. PRIORITY MATRIX
Rank by impact potential, effort, and ROI

### 4. QUICK WINS vs LONG-TERM
- Immediate fixes (days)
- Short-term optimizations (weeks-months)
- Strategic improvements (months-quarters)

### 5. MONITORING & VALIDATION
- KPIs to track
- Monitoring tools
- Success criteria

Provide specific technical details and realistic estimates.
"""
    
    def load_and_analyze(self, csv_file="enhanced_system_call_log_95249_events_20250610_143122.csv", threshold_percentile=95):
        """Load data and perform bottleneck analysis"""
        print(f"🔍 Loading and analyzing {csv_file}...")
        
        try:
            # Load data
            raw_data = pd.read_csv(csv_file)
            raw_data['timestamp'] = pd.to_datetime(raw_data['timestamp'])
            
            # Calculate bottleneck threshold
            threshold = raw_data['duration_ms'].quantile(threshold_percentile / 100)
            bottleneck_events = raw_data[raw_data['duration_ms'] > threshold].copy()
            
            print(f"✅ Loaded {len(raw_data):,} events")
            print(f"📊 Identified {len(bottleneck_events):,} bottlenecks (>{threshold:.2f}ms)")
            
            # Extract key bottleneck data
            self.bottleneck_data = self._extract_key_bottlenecks(raw_data, bottleneck_events, threshold)
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
    
    def _extract_key_bottlenecks(self, raw_data, bottleneck_events, threshold):
        """Extract essential bottleneck information"""
        
        total_events = len(raw_data)
        total_time = raw_data['duration_ms'].sum()
        bottleneck_time = bottleneck_events['duration_ms'].sum()
        performance_impact = (bottleneck_time / total_time) * 100
        
        # Top critical combinations
        combined_bottlenecks = bottleneck_events.groupby(['resource', 'activity']).agg({
            'duration_ms': ['count', 'mean', 'sum'],
            'case_id': 'nunique'
        }).round(2)
        combined_bottlenecks.columns = ['frequency', 'avg_duration', 'total_time', 'affected_instances']
        combined_bottlenecks = combined_bottlenecks.sort_values('total_time', ascending=False)
        
        return {
            'system_overview': {
                'total_events': total_events,
                'bottleneck_events': len(bottleneck_events),
                'threshold_ms': threshold,
                'performance_impact_percent': performance_impact,
                'bottleneck_time_seconds': bottleneck_time / 1000,
            },
            'critical_combinations': combined_bottlenecks.head(10).to_dict('index'),
            'system_context': {
                'unique_processes': raw_data['resource'].nunique(),
                'unique_activities': raw_data['activity'].nunique(),
                'analysis_timespan_hours': (raw_data['timestamp'].max() - raw_data['timestamp'].min()).total_seconds() / 3600,
            }
        }
    
    def generate_ai_solutions(self):
        """Generate AI-powered solutions using Gemini"""
        
        if not self.bottleneck_data:
            print("❌ No bottleneck data available")
            return None
        
        if not self.chat_model:
            print("❌ Gemini not available, using local solutions")
            return self._get_local_solutions()
        
        print("🤖 Generating AI solutions with Gemini...")
        
        try:
            # Format data for prompt
            overview = self.bottleneck_data['system_overview']
            
            # Format critical combinations
            critical_text = "### Top Critical Bottlenecks:\n"
            for (process, activity), stats in list(self.bottleneck_data['critical_combinations'].items())[:5]:
                critical_text += f"**{process} → {activity}**: {stats['frequency']} events, {stats['avg_duration']:.1f}ms avg, {stats['total_time']:.1f}ms total impact\n"
            
            # Format system context
            context = self.bottleneck_data['system_context']
            context_text = f"""- System Type: Windows with {context['unique_processes']} processes
- Activities: {context['unique_activities']} different system calls
- Analysis Period: {context['analysis_timespan_hours']:.1f} hours"""
            
            # Create comprehensive prompt
            prompt = self.analysis_template.format(
                total_events=overview['total_events'],
                bottleneck_events=overview['bottleneck_events'],
                performance_impact=overview['performance_impact_percent'],
                threshold_ms=overview['threshold_ms'],
                bottleneck_time=overview['bottleneck_time_seconds'],
                critical_combinations=critical_text,
                system_context=context_text
            )
            
            # Get AI response
            combined_message = f"{self.system_message}\n\n{prompt}"
            response = self.chat_model.invoke([HumanMessage(content=combined_message)])
            
            print("✅ AI solutions generated successfully!")
            return response.content
            
        except Exception as e:
            print(f"❌ Error generating AI solutions: {e}")
            return self._get_local_solutions()
    
    def _get_local_solutions(self):
        """Fallback local solutions"""
        return """
# LOCAL BOTTLENECK SOLUTIONS

## PRIORITY RECOMMENDATIONS

### 1. File I/O Optimization (HIGH IMPACT)
**Problem**: ReadFile/WriteFile operations causing delays
**Solution**: Implement asynchronous I/O with completion ports
**Timeline**: 2-3 weeks
**Team**: 2 senior developers
**Cost**: $15,000-$20,000
**Expected Improvement**: 40-60% I/O performance boost

### 2. Memory Management (MEDIUM IMPACT)
**Problem**: VirtualAlloc bottlenecks
**Solution**: Custom memory pools and large page support
**Timeline**: 3-4 weeks
**Team**: 1 senior developer + 1 architect
**Cost**: $20,000-$30,000
**Expected Improvement**: 30-50% allocation speed

### 3. Registry Optimization (QUICK WIN)
**Problem**: RegQueryValue delays
**Solution**: Implement registry value caching
**Timeline**: 1 week
**Team**: 1 mid-level developer
**Cost**: $3,000-$5,000
**Expected Improvement**: 20-30% registry performance

## IMPLEMENTATION PRIORITY
1. Registry caching (quick win)
2. File I/O optimization (high impact)
3. Memory management (long-term benefit)

## TOTAL INVESTMENT
- **Cost**: $38,000-$55,000
- **Timeline**: 6-8 weeks
- **Expected ROI**: 6-month payback period
- **Performance Gain**: 25-45% overall improvement
"""
    
    def save_results(self, solutions):
        """Save analysis results"""
        output_dir = "bottleneck_analysis_results"
        os.makedirs(output_dir, exist_ok=True)
        
        # Save AI solutions
        with open(f"{output_dir}/ai_solutions.md", 'w', encoding='utf-8') as f:
            f.write(f"# Bottleneck Analysis Solutions\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Model**: {self.model_name}\n\n")
            f.write(solutions)
        
        # Save summary data
        if self.bottleneck_data:
            summary = {
                'total_events': self.bottleneck_data['system_overview']['total_events'],
                'bottleneck_events': self.bottleneck_data['system_overview']['bottleneck_events'],
                'performance_impact': f"{self.bottleneck_data['system_overview']['performance_impact_percent']:.1f}%",
                'threshold_ms': f"{self.bottleneck_data['system_overview']['threshold_ms']:.2f}ms",
                'top_bottlenecks': list(self.bottleneck_data['critical_combinations'].keys())[:5]
            }
            
            with open(f"{output_dir}/analysis_summary.json", 'w') as f:
                json.dump(summary, f, indent=2, default=str)
        
        print(f"✅ Results saved to {output_dir}/")
    
    def create_quick_visualization(self):
        """Create a simple bottleneck visualization"""
        if not self.bottleneck_data:
            return
        
        output_dir = "bottleneck_analysis_results"
        os.makedirs(output_dir, exist_ok=True)
        
        # Create simple bar chart of top bottlenecks
        plt.figure(figsize=(12, 8))
        
        top_bottlenecks = list(self.bottleneck_data['critical_combinations'].items())[:8]
        labels = [f"{proc}\n{act}" for (proc, act), _ in top_bottlenecks]
        impacts = [stats['total_time'] for _, stats in top_bottlenecks]
        
        bars = plt.barh(range(len(labels)), impacts, color='red', alpha=0.7)
        plt.yticks(range(len(labels)), labels, fontsize=10)
        plt.xlabel('Total Time Impact (ms)')
        plt.title('Top System Call Bottlenecks', fontsize=16, fontweight='bold')
        
        # Add value labels
        for i, (bar, impact) in enumerate(zip(bars, impacts)):
            plt.text(bar.get_width() + max(impacts)*0.01, bar.get_y() + bar.get_height()/2,
                    f'{impact:.0f}ms', va='center', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/bottleneck_chart.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📊 Visualization saved to {output_dir}/bottleneck_chart.png")
    
    def print_summary(self):
        """Print analysis summary"""
        if not self.bottleneck_data:
            return
        
        overview = self.bottleneck_data['system_overview']
        
        print("\n" + "="*60)
        print("📊 BOTTLENECK ANALYSIS SUMMARY")
        print("="*60)
        
        print(f"\n🎯 KEY METRICS:")
        print(f"• Total Events: {overview['total_events']:,}")
        print(f"• Bottleneck Events: {overview['bottleneck_events']:,}")
        print(f"• Performance Impact: {overview['performance_impact_percent']:.1f}%")
        print(f"• Time Lost: {overview['bottleneck_time_seconds']:.1f} seconds")
        
        print(f"\n🔥 TOP 5 CRITICAL BOTTLENECKS:")
        for i, ((process, activity), stats) in enumerate(list(self.bottleneck_data['critical_combinations'].items())[:5], 1):
            print(f"{i}. {process} → {activity}")
            print(f"   Impact: {stats['total_time']:.1f}ms ({stats['frequency']} events)")
    
    def run_complete_analysis(self, csv_file="enhanced_system_call_log_95249_events_20250610_143122.csv"):
        """Run complete bottleneck analysis pipeline"""
        
        print("🚀 AUTOMATED BOTTLENECK ANALYSIS")
        print("="*50)
        
        # Step 1: Load and analyze data
        if not self.load_and_analyze(csv_file):
            print("❌ Failed to load data")
            return
        
        # Step 2: Generate AI solutions
        solutions = self.generate_ai_solutions()
        
        # Step 3: Save results
        self.save_results(solutions)
        
        # Step 4: Create visualization
        self.create_quick_visualization()
        
        # Step 5: Print summary
        self.print_summary()
        
        print("\n✅ Analysis Complete!")
        print("📂 Check 'bottleneck_analysis_results/' for detailed results")
        
        return {
            'bottleneck_data': self.bottleneck_data,
            'solutions': solutions
        }

def main():
    """Main execution function"""
    solver = SimpleBottleneckSolver()
    results = solver.run_complete_analysis()
    return results

if __name__ == "__main__":
    results = main()