import pandas as pd
import random
from datetime import datetime, timedelta
import uuid

class EnhancedSystemCallGenerator:
    def __init__(self):
        # Define meaningful process workflows with clear business context
        self.process_workflows = {
            'document_editing': {
                'executable': 'notepad.exe',
                'description': 'Document Creation and Editing Workflow',
                'stages': [
                    {
                        'stage_name': 'Application_Startup',
                        'activities': ['CreateProcess', 'LoadLibrary', 'RegOpenKey', 'RegQueryValue'],
                        'description': 'Application initialization'
                    },
                    {
                        'stage_name': 'File_Opening',
                        'activities': ['CreateFile', 'ReadFile', 'GetFileSize'],
                        'description': 'Opening existing document'
                    },
                    {
                        'stage_name': 'Content_Modification',
                        'activities': ['WriteFile', 'VirtualAlloc', 'SetFilePointer'],
                        'description': 'Editing document content'
                    },
                    {
                        'stage_name': 'Auto_Save',
                        'activities': ['WriteFile', 'FlushFileBuffers', 'SetFileTime'],
                        'description': 'Automatic saving'
                    },
                    {
                        'stage_name': 'File_Closing',
                        'activities': ['WriteFile', 'CloseHandle', 'RegCloseKey'],
                        'description': 'Saving and closing document'
                    },
                    {
                        'stage_name': 'Application_Shutdown',
                        'activities': ['FreeLibrary', 'TerminateProcess'],
                        'description': 'Clean application termination'
                    }
                ],
                'bottleneck_patterns': {
                    'large_file_io': ['ReadFile', 'WriteFile'],
                    'memory_pressure': ['VirtualAlloc']
                },
                'weight': 0.25
            },
            
            'web_browsing': {
                'executable': 'chrome.exe',
                'description': 'Web Browser Session Workflow',
                'stages': [
                    {
                        'stage_name': 'Browser_Startup',
                        'activities': ['CreateProcess', 'LoadLibrary', 'VirtualAlloc', 'CreateThread'],
                        'description': 'Browser initialization with multiple threads'
                    },
                    {
                        'stage_name': 'Profile_Loading',
                        'activities': ['CreateFile', 'ReadFile', 'RegOpenKey', 'RegQueryValue'],
                        'description': 'Loading user profile and settings'
                    },
                    {
                        'stage_name': 'Network_Request',
                        'activities': ['CreateFile', 'WriteFile', 'ReadFile', 'WaitForSingleObject'],
                        'description': 'Making HTTP requests and loading content'
                    },
                    {
                        'stage_name': 'Cache_Management',
                        'activities': ['CreateFile', 'WriteFile', 'DeleteFile', 'VirtualAlloc'],
                        'description': 'Managing browser cache'
                    },
                    {
                        'stage_name': 'Tab_Management',
                        'activities': ['CreateThread', 'TerminateThread', 'VirtualAlloc', 'VirtualFree'],
                        'description': 'Opening/closing tabs and memory management'
                    },
                    {
                        'stage_name': 'Browser_Shutdown',
                        'activities': ['WriteFile', 'CloseHandle', 'ExitThread', 'TerminateProcess'],
                        'description': 'Saving state and closing browser'
                    }
                ],
                'bottleneck_patterns': {
                    'memory_allocation': ['VirtualAlloc', 'CreateThread'],
                    'network_latency': ['WaitForSingleObject', 'ReadFile']
                },
                'weight': 0.30
            },
            
            'file_management': {
                'executable': 'explorer.exe',
                'description': 'File Explorer Operations Workflow',
                'stages': [
                    {
                        'stage_name': 'Explorer_Startup',
                        'activities': ['CreateProcess', 'LoadLibrary', 'RegOpenKey'],
                        'description': 'Windows Explorer initialization'
                    },
                    {
                        'stage_name': 'Directory_Enumeration',
                        'activities': ['CreateFile', 'ReadFile', 'FindFirstFile', 'FindNextFile'],
                        'description': 'Listing directory contents'
                    },
                    {
                        'stage_name': 'File_Operations',
                        'activities': ['CopyFile', 'MoveFile', 'DeleteFile', 'CreateDirectory'],
                        'description': 'File system operations'
                    },
                    {
                        'stage_name': 'Property_Viewing',
                        'activities': ['GetFileAttributes', 'GetFileSize', 'GetFileTime'],
                        'description': 'Reading file properties'
                    },
                    {
                        'stage_name': 'Thumbnail_Generation',
                        'activities': ['CreateFile', 'ReadFile', 'VirtualAlloc', 'WriteFile'],
                        'description': 'Generating file thumbnails'
                    }
                ],
                'bottleneck_patterns': {
                    'directory_scan': ['FindFirstFile', 'FindNextFile'],
                    'file_access': ['CreateFile', 'ReadFile']
                },
                'weight': 0.20
            },
            
            'antivirus_scan': {
                'executable': 'guardian.exe',
                'description': 'Antivirus File Scanning Workflow',
                'stages': [
                    {
                        'stage_name': 'Scanner_Initialization',
                        'activities': ['CreateProcess', 'LoadLibrary', 'RegOpenKey', 'CreateThread'],
                        'description': 'Antivirus engine startup'
                    },
                    {
                        'stage_name': 'Definition_Update',
                        'activities': ['CreateFile', 'ReadFile', 'WriteFile', 'VerifySignature'],
                        'description': 'Updating virus definitions'
                    },
                    {
                        'stage_name': 'File_Scanning',
                        'activities': ['CreateFile', 'ReadFile', 'AnalyzeFile', 'CheckSignature'],
                        'description': 'Scanning files for threats'
                    },
                    {
                        'stage_name': 'Threat_Detection',
                        'activities': ['QuarantineFile', 'WriteFile', 'LogEvent'],
                        'description': 'Handling detected threats'
                    },
                    {
                        'stage_name': 'Report_Generation',
                        'activities': ['CreateFile', 'WriteFile', 'RegSetValue'],
                        'description': 'Creating scan reports'
                    }
                ],
                'bottleneck_patterns': {
                    'deep_scan': ['AnalyzeFile', 'CheckSignature'],
                    'file_access': ['ReadFile', 'CreateFile']
                },
                'weight': 0.15
            },
            
            'system_maintenance': {
                'executable': 'system',
                'description': 'System Background Tasks Workflow',
                'stages': [
                    {
                        'stage_name': 'Task_Scheduler',
                        'activities': ['CreateProcess', 'WaitForSingleObject', 'SetTimer'],
                        'description': 'Scheduling system tasks'
                    },
                    {
                        'stage_name': 'Registry_Maintenance',
                        'activities': ['RegOpenKey', 'RegQueryValue', 'RegSetValue', 'RegCloseKey'],
                        'description': 'Registry cleanup and maintenance'
                    },
                    {
                        'stage_name': 'Memory_Management',
                        'activities': ['VirtualAlloc', 'VirtualFree', 'HeapCompact'],
                        'description': 'System memory optimization'
                    },
                    {
                        'stage_name': 'Disk_Cleanup',
                        'activities': ['DeleteFile', 'FindFirstFile', 'RemoveDirectory'],
                        'description': 'Temporary file cleanup'
                    }
                ],
                'bottleneck_patterns': {
                    'synchronization': ['WaitForSingleObject'],
                    'registry_access': ['RegQueryValue', 'RegSetValue']
                },
                'weight': 0.10
            }
        }
        
        # Enhanced system calls with better categorization
        self.system_calls = {
            'file_operations': ['CreateFile', 'ReadFile', 'WriteFile', 'CloseHandle', 'DeleteFile', 
                               'CopyFile', 'MoveFile', 'GetFileSize', 'SetFilePointer', 'FlushFileBuffers'],
            'process_management': ['CreateProcess', 'TerminateProcess', 'OpenProcess', 'GetProcessId'],
            'memory_operations': ['VirtualAlloc', 'VirtualFree', 'HeapAlloc', 'HeapFree', 'MapViewOfFile'],
            'registry_operations': ['RegOpenKey', 'RegQueryValue', 'RegSetValue', 'RegCloseKey', 'RegCreateKey'],
            'library_management': ['LoadLibrary', 'GetProcAddress', 'FreeLibrary'],
            'thread_operations': ['CreateThread', 'ExitThread', 'TerminateThread', 'WaitForSingleObject'],
            'file_system': ['FindFirstFile', 'FindNextFile', 'CreateDirectory', 'RemoveDirectory', 
                           'GetFileAttributes', 'SetFileAttributes', 'GetFileTime', 'SetFileTime'],
            'security_operations': ['AnalyzeFile', 'CheckSignature', 'VerifySignature', 'QuarantineFile'],
            'system_operations': ['SetTimer', 'HeapCompact', 'LogEvent']
        }
        
        # Realistic file paths with context
        self.file_contexts = {
            'user_documents': [
                'C:\\Users\\Student\\Documents\\thesis_chapter1.docx',
                'C:\\Users\\Student\\Documents\\research_notes.txt',
                'C:\\Users\\Student\\Documents\\presentation.pptx'
            ],
            'system_files': [
                'C:\\Windows\\System32\\kernel32.dll',
                'C:\\Windows\\System32\\user32.dll',
                'C:\\Program Files\\Common Files\\system.dll'
            ],
            'temp_files': [
                'C:\\Temp\\cache_12345.tmp',
                'C:\\Users\\Student\\AppData\\Local\\Temp\\session.tmp',
                'C:\\Windows\\Temp\\update_cache.tmp'
            ],
            'downloads': [
                'C:\\Users\\Student\\Downloads\\research_paper.pdf',
                'C:\\Users\\Student\\Downloads\\software_installer.exe',
                'C:\\Users\\Student\\Downloads\\dataset.csv'
            ],
            'application_files': [
                'C:\\Program Files\\Application\\config.ini',
                'C:\\Program Files\\Browser\\profile.dat',
                'C:\\Program Files\\Antivirus\\definitions.db'
            ]
        }
        
    def generate_process_workflow(self, workflow_type, case_id, start_time):
        """Generate a realistic workflow following business process patterns"""
        workflow = self.process_workflows[workflow_type]
        events = []
        current_time = start_time
        
        # Add workflow-level metadata
        process_context = {
            'workflow_type': workflow_type,
            'business_process': workflow['description'],
            'executable': workflow['executable']
        }
        
        # Generate events following the stage sequence
        for stage in workflow['stages']:
            stage_start_time = current_time
            
            # Generate 2-5 events per stage
            stage_events = random.randint(2, 5)
            
            for i in range(stage_events):
                # Choose activity from stage-specific activities
                if random.random() < 0.8:  # 80% follow stage pattern
                    activity = random.choice(stage['activities'])
                else:  # 20% can be any system call (noise)
                    all_calls = [call for calls in self.system_calls.values() for call in calls]
                    activity = random.choice(all_calls)
                
                # Determine if this is a bottleneck operation
                is_bottleneck = any(activity in bottleneck_ops 
                                  for bottleneck_ops in workflow['bottleneck_patterns'].values())
                
                # Calculate realistic delay
                if is_bottleneck:
                    delay = random.uniform(100, 1000)  # Bottleneck: 100-1000ms
                    bottleneck_type = next((pattern for pattern, ops in workflow['bottleneck_patterns'].items() 
                                          if activity in ops), 'unknown')
                else:
                    delay = random.uniform(1, 50)     # Normal: 1-50ms
                    bottleneck_type = None
                
                current_time += timedelta(milliseconds=delay)
                
                # Select appropriate file path based on activity
                file_path = self._get_contextual_file_path(activity, workflow_type)
                
                # Create enhanced event record
                event = {
                    # Core process mining attributes
                    'case_id': f"{workflow_type}_{case_id}",
                    'activity': activity,
                    'timestamp': current_time,
                    'resource': workflow['executable'],
                    
                    # Process context
                    'workflow_type': workflow_type,
                    'business_process': workflow['description'],
                    'process_stage': stage['stage_name'],
                    'stage_description': stage['description'],
                    
                    # Technical details
                    'pid': 2000 + case_id,
                    'tid': random.randint(100, 999),
                    'file_path': file_path,
                    'operation_category': self._categorize_activity(activity),
                    
                    # Performance metrics
                    'duration_ms': round(delay, 2),
                    'result': 'SUCCESS' if random.random() > 0.03 else 'ERROR',  # 3% error rate
                    'is_bottleneck': is_bottleneck,
                    'bottleneck_type': bottleneck_type,
                    
                    # Quality labels
                    'event_quality': self._assess_event_quality(delay, is_bottleneck),
                    'anomaly_score': self._calculate_anomaly_score(delay, activity, workflow_type)
                }
                
                events.append(event)
        
        return events
    
    def _get_contextual_file_path(self, activity, workflow_type):
        """Get contextually appropriate file path based on activity and workflow"""
        if 'File' not in activity and 'Directory' not in activity:
            return ''
            
        # Map workflows to appropriate file contexts
        context_mapping = {
            'document_editing': ['user_documents', 'temp_files'],
            'web_browsing': ['temp_files', 'downloads', 'application_files'],
            'file_management': ['user_documents', 'downloads', 'system_files'],
            'antivirus_scan': ['system_files', 'user_documents', 'downloads'],
            'system_maintenance': ['system_files', 'temp_files']
        }
        
        available_contexts = context_mapping.get(workflow_type, ['temp_files'])
        chosen_context = random.choice(available_contexts)
        return random.choice(self.file_contexts[chosen_context])
    
    def _categorize_activity(self, activity):
        """Categorize system call into functional groups"""
        for category, calls in self.system_calls.items():
            if activity in calls:
                return category
        return 'unknown'
    
    def _assess_event_quality(self, duration, is_bottleneck):
        """Assess the quality/normalcy of an event"""
        if duration > 500:
            return 'poor'
        elif is_bottleneck and duration > 100:
            return 'acceptable'
        elif duration < 10:
            return 'excellent'
        else:
            return 'good'
    
    def _calculate_anomaly_score(self, duration, activity, workflow_type):
        """Calculate anomaly score (0-1, higher = more anomalous)"""
        base_score = 0.0
        
        # Duration-based anomaly
        if duration > 1000:
            base_score += 0.5
        elif duration > 500:
            base_score += 0.3
        
        # Context-based anomaly (simplified)
        if workflow_type == 'document_editing' and 'Thread' in activity:
            base_score += 0.2  # Unusual for simple document editing
        elif workflow_type == 'system_maintenance' and 'File' in activity:
            base_score += 0.1  # Somewhat unusual but not rare
            
        return min(base_score, 1.0)
    
    def generate_enhanced_event_log(self, num_cases=1000, time_span_hours=24):
        """Generate enhanced event log with better labeling"""
        base_time = datetime.now() - timedelta(hours=time_span_hours)
        all_events = []
        
        print(f"Generating enhanced event log with {num_cases} cases...")
        
        # Track workflow distribution
        workflow_distribution = {}
        
        for case_id in range(num_cases):
            # Choose workflow type based on weights
            workflow_type = random.choices(
                list(self.process_workflows.keys()),
                weights=[w['weight'] for w in self.process_workflows.values()]
            )[0]
            
            workflow_distribution[workflow_type] = workflow_distribution.get(workflow_type, 0) + 1
            
            # Randomize start time
            start_offset = random.uniform(0, time_span_hours * 3600)
            start_time = base_time + timedelta(seconds=start_offset)
            
            # Generate workflow events
            workflow_events = self.generate_process_workflow(workflow_type, case_id, start_time)
            all_events.extend(workflow_events)
        
        # Sort by timestamp
        all_events.sort(key=lambda x: x['timestamp'])
        
        # Create DataFrame with enhanced structure
        df = pd.DataFrame(all_events)
        
        # Add pm4py compatibility columns
        df['case:concept:name'] = df['case_id']
        df['concept:name'] = df['activity']
        df['time:timestamp'] = df['timestamp']
        df['org:resource'] = df['resource']
        
        print(f"Generated {len(all_events):,} events across {len(workflow_distribution)} workflow types")
        return df
    
    def save_enhanced_log(self, df, filename_prefix='enhanced_system_call_log'):
        """Save enhanced event log"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        main_filename = f"{filename_prefix}_{len(df)}_events_{timestamp}.csv"
        df.to_csv(main_filename, index=False)
        
        print(f"Enhanced event log saved to: {main_filename}")
        return main_filename
    
    def _generate_metadata(self, df):
        """Generate comprehensive metadata about the dataset"""
        metadata = {
            'total_events': len(df),
            'unique_cases': df['case_id'].nunique(),
            'workflow_distribution': df['workflow_type'].value_counts().to_dict(),
            'activity_distribution': df['activity'].value_counts().head(10).to_dict(),
            'bottleneck_percentage': (df['is_bottleneck'].sum() / len(df)) * 100,
            'error_rate': (df['result'] == 'ERROR').sum() / len(df) * 100,
            'average_case_length': len(df) / df['case_id'].nunique()
        }
        return metadata

def main():
    """Enhanced main function with better user interaction"""
    print("Enhanced System Call Event Log Generator")
    print("=" * 50)
    
    generator = EnhancedSystemCallGenerator()
    
    # Get dataset size
    print(f"Select dataset size:")
    print("1. Small (500 cases)")
    print("2. Medium (2000 cases)")
    print("3. Large (5000 cases)")
    
    choice = input("Enter choice (1-3) or press Enter for Medium: ").strip()
    
    size_configs = {
        '1': (500, 12, "Small"),
        '2': (2000, 18, "Medium"),
        '3': (5000, 24, "Large")
    }
    
    num_cases, time_span, size_name = size_configs.get(choice, (2000, 18, "Medium"))
    
    print(f"Generating {size_name} dataset with {num_cases:,} cases...")
    
    # Generate enhanced event log
    event_log = generator.generate_enhanced_event_log(
        num_cases=num_cases, 
        time_span_hours=time_span
    )
    
    # Display key statistics
    print(f"\nDataset Statistics:")
    print(f"Total Events: {len(event_log):,}")
    print(f"Unique Cases: {event_log['case_id'].nunique():,}")
    print(f"Unique Activities: {event_log['activity'].nunique()}")
    print(f"Workflow Types: {event_log['workflow_type'].nunique()}")
    
    # Save the enhanced dataset
    main_file = generator.save_enhanced_log(event_log)
    
    print(f"Dataset generation complete!")
    print(f"File: {main_file}")
    
    return event_log

if __name__ == "__main__":
    enhanced_log = main()