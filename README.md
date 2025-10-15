# Windows System Call Process Mining & Optimization

A comprehensive system for analyzing Windows system call events using process mining techniques to identify performance bottlenecks and generate AI-powered optimization solutions.

## 🎯 Project Overview

This project provides a complete pipeline for:
- **System Call Data Generation**: Creates realistic system call event logs
- **Process Mining Analysis**: Discovers process models and patterns from system call data
- **Bottleneck Identification**: Identifies performance bottlenecks using statistical analysis
- **AI-Powered Solutions**: Generates optimization recommendations using Large Language Models
- **Visualization**: Creates comprehensive visual reports and process diagrams

## 🏗️ Architecture

The system consists of several interconnected components:

```
┌─────────────────────────────┐    ┌─────────────────────────────┐
│   System Call Generator     │    │   Process Mining Pipeline  │
│   • Simulates real events   │───▶│   • Event log processing    │
│   • Multiple processes      │    │   • Process discovery       │
│   • Realistic patterns      │    │   • Variant analysis        │
└─────────────────────────────┘    └─────────────────────────────┘
                                                  │
┌─────────────────────────────┐    ┌─────────────────────────────┐
│   Baseline Measurement      │    │   Bottleneck Analysis       │
│   • Performance metrics     │◀───│   • Statistical detection   │
│   • System monitoring       │    │   • Resource analysis       │
│   • Baseline establishment  │    │   • Performance hotspots    │
└─────────────────────────────┘    └─────────────────────────────┘
                                                  │
┌─────────────────────────────┐    ┌─────────────────────────────┐
│   AI Solution Generator     │    │   Visualization Suite       │
│   • LLM-powered analysis    │◀───│   • Process diagrams        │
│   • Optimization strategies │    │   • Performance charts      │
│   • Implementation guides   │    │   • Interactive dashboards  │
└─────────────────────────────┘    └─────────────────────────────┘
```

## 📁 Project Structure

```
Windows-System-Call-Process-Mining-Optimization/
├── README.md                              # This file
├── requirements.txt                       # Python dependencies
│
├── Core Scripts/
├── system_call_generator.py              # Generates synthetic system call data
├── process_mining_pipeline.py            # Main process mining analysis
├── baseline_measurement.py               # Performance baseline measurement
├── bottleneck_focussed_analyser.py      # Bottleneck detection and analysis
├── bottleneck_solver.py                 # AI-powered solution generation
├── sequence_diagram_generator.py         # Process flow visualization
├── single_process_analyser.py           # Individual process analysis
│
├── Data/
├── enhanced_system_call_log_95249_events_20250610_143122.csv  # Sample dataset
│
├── Analysis Results/
├── baseline_analysis/                    # Baseline performance reports
│   ├── baseline_analysis.png
│   └── baseline_performance_report.txt
├── bottleneck_analysis/                  # Bottleneck visualizations
│   ├── bottleneck_analysis_dashboard.png
│   └── bottleneck_heatmap.png
├── bottleneck_analysis_results/          # AI-generated solutions
│   ├── ai_solutions.md                   # Detailed optimization strategies
│   ├── ai_solutions_ppt.md              # Executive summary
│   ├── analysis_summary.json            # Structured analysis data
│   └── bottleneck_chart.png             # Performance bottleneck chart
├── process_models/                       # Discovered process models
├── sequence_diagrams/                    # Process flow diagrams
│   ├── all_processes_overview.png
│   ├── chrome_flow_diagram.png
│   ├── explorer_flow_diagram.png
│   ├── guardian_flow_diagram.png
│   ├── notepad_flow_diagram.png
│   ├── system_flow_diagram.png
│   └── sequence_analysis_report.txt
└── single_process_analysis/             # Individual process analytics
    ├── chrome/
    ├── explorer/
    ├── guardian/
    ├── notepad/
    └── system/
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Windows operating system (for system call simulation)
- Graphviz (for process model visualization)

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/your-username/Windows-System-Call-Process-Mining-Optimization.git
cd Windows-System-Call-Process-Mining-Optimization
```

2. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

3. **Install Graphviz** (for process visualizations):
   - Download from: https://graphviz.org/download/
   - Add to system PATH

4. **Set up AI integration** (optional):
   - Create `.env` file with your API keys:
   ```
   GOOGLE_API_KEY=your_gemini_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here  # Optional
   ```

### Basic Usage

1. **Generate System Call Data**:
```bash
python system_call_generator.py
```

2. **Run Process Mining Analysis**:
```bash
python process_mining_pipeline.py
```

3. **Identify Bottlenecks**:
```bash
python bottleneck_focussed_analyser.py
```

4. **Generate AI-Powered Solutions**:
```bash
python bottleneck_solver.py
```

5. **Create Process Visualizations**:
```bash
python sequence_diagram_generator.py
```

## 📊 Core Features

### 1. System Call Data Generation
- **Realistic Simulation**: Generates system call events that mirror real Windows processes
- **Multiple Processes**: Simulates Chrome, Notepad, Explorer, System, and Guardian processes
- **Configurable Parameters**: Adjustable event counts, time ranges, and performance characteristics
- **Export Formats**: CSV output compatible with process mining tools

### 2. Process Mining Pipeline
- **Event Log Processing**: Converts raw system call data into process mining format
- **Process Discovery**: Uses multiple algorithms (Inductive, Alpha, Heuristic miners)
- **Variant Analysis**: Identifies common process execution patterns
- **Statistical Analysis**: Comprehensive process performance metrics

### 3. Bottleneck Detection
- **Multi-dimensional Analysis**: Analyzes by process, activity, and resource
- **Statistical Methods**: Uses percentile-based bottleneck identification
- **Performance Hotspots**: Identifies the most impactful performance issues
- **Trend Analysis**: Tracks performance patterns over time

### 4. AI-Powered Solutions
- **LLM Integration**: Uses Google Gemini and other LLMs for analysis
- **RAG System**: Retrieval-Augmented Generation for contextual solutions
- **Implementation Guides**: Detailed technical implementation strategies
- **Cost-Benefit Analysis**: Realistic cost and timeline estimates

### 5. Comprehensive Visualization
- **Process Models**: Petri nets and process flow diagrams
- **Performance Dashboards**: Interactive bottleneck analysis charts
- **Sequence Diagrams**: Process interaction visualizations
- **Timeline Analysis**: Temporal pattern identification

## 🔧 Advanced Configuration

### Process Mining Parameters
```python
# In process_mining_pipeline.py
miner.preprocess_data(
    min_case_length=5,      # Minimum events per case
    max_case_length=200,    # Maximum events per case
    activity_threshold=10   # Minimum activity frequency
)
```

### Bottleneck Detection Thresholds
```python
# In bottleneck_focussed_analyser.py
duration_threshold = df['duration_ms'].quantile(0.95)  # 95th percentile
min_impact_threshold = 50000  # Minimum total impact (ms)
```

### AI Model Configuration
```python
# In bottleneck_solver.py
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.3,
    max_tokens=8192
)
```

## 📈 Performance Metrics

The system tracks and analyzes various performance metrics:

- **Event Processing Rate**: Events processed per second
- **Memory Usage**: Peak and average memory consumption
- **Processing Time**: End-to-end analysis duration
- **Bottleneck Impact**: Total time impact of identified bottlenecks
- **Solution Effectiveness**: Before/after performance comparisons

## 🎨 Visualization Gallery

### Process Models
- **Petri Nets**: Formal process model representations
- **Heuristic Networks**: Frequency-based process flows
- **BPMN Diagrams**: Business process model notation

### Performance Dashboards
- **Bottleneck Heatmaps**: Visual performance hotspots
- **Timeline Charts**: Temporal performance analysis
- **Resource Utilization**: System resource usage patterns

### Process Flow Diagrams
- **Sequence Diagrams**: Inter-process communication flows
- **Activity Networks**: Process activity relationships
- **Dependency Graphs**: Process execution dependencies

## 🔍 Analysis Results

### Sample Findings
From the included sample analysis:

**Top Performance Bottlenecks:**
1. `notepad.exe → WriteFile`: 691 events, 910.3ms average duration
2. `chrome.exe → VirtualAlloc`: 647 events, 911.0ms average duration
3. `chrome.exe → CreateThread`: 431 events, 916.2ms average duration
4. `chrome.exe → ReadFile`: 433 events, 910.5ms average duration
5. `guardian.exe → CreateFile`: 305 events, 910.8ms average duration

**AI-Generated Solutions:**
- Buffered I/O optimization for Notepad
- Chrome memory management improvements
- Antivirus exclusion recommendations
- Thread pooling optimizations
- Disk I/O performance enhancements

## 🛠️ Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black *.py
flake8 *.py
```

### Performance Profiling
```bash
python -m memory_profiler bottleneck_focussed_analyser.py
```

## 📚 Dependencies

### Core Process Mining
- **pm4py**: Process mining algorithms and tools
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing

### Visualization
- **matplotlib**: Static plotting
- **seaborn**: Statistical visualization
- **plotly**: Interactive charts
- **graphviz**: Process model visualization

### AI Integration
- **langchain**: LLM framework
- **google-generativeai**: Google Gemini API
- **faiss-cpu**: Vector similarity search
- **sentence-transformers**: Text embeddings

### Additional Tools
- **psutil**: System monitoring
- **tqdm**: Progress bars
- **python-dotenv**: Environment management
