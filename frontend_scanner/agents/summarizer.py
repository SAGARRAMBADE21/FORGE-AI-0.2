"""Summarizer Agent - Generate hierarchical summaries."""
from typing import List, Dict, Any, Optional
from pathlib import Path
from collections import defaultdict
from pydantic import BaseModel, Field
import os

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("Warning: LangChain LLM not available")


class FileSummary(BaseModel):
    """Summary for a single file."""
    file_path: str
    purpose: str
    key_exports: List[str] = Field(default_factory=list)
    api_dependencies: List[str] = Field(default_factory=list)
    framework: Optional[str] = None


class FolderSummary(BaseModel):
    """Summary for a folder."""
    folder_path: str
    purpose: str
    file_count: int
    key_files: List[str] = Field(default_factory=list)


class ProjectSummary(BaseModel):
    """Project-level summary."""
    project_root: str
    framework: Optional[str] = None
    architecture: str
    key_components: List[str] = Field(default_factory=list)
    api_endpoints_used: List[str] = Field(default_factory=list)
    suggested_backend_endpoints: List[str] = Field(default_factory=list)


class SummarizerAgent:
    """Agent that generates hierarchical summaries using LLM."""
    
    def __init__(self, config):
        self.config = config
        self.llm = None
        
        if LLM_AVAILABLE:
            try:
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key:
                    self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
                    print("✓ Initialized LLM for summarization")
                else:
                    print("Warning: OPENAI_API_KEY not set. Summaries will be basic.")
            except Exception as e:
                print(f"Error initializing LLM: {e}")
    
    def generate_summaries(self, parsed_files: List[Any], chunks: List[Any]) -> Dict[str, Any]:
        """Generate file, folder, and project summaries."""
        print("Generating summaries...")
        
        file_summaries = self._generate_file_summaries(parsed_files)
        folder_summaries = self._generate_folder_summaries(file_summaries)
        project_summary = self._generate_project_summary(
            file_summaries,
            folder_summaries,
            parsed_files
        )
        
        return {
            "file_summaries": file_summaries,
            "folder_summaries": folder_summaries,
            "project_summary": project_summary
        }
    
    def _generate_file_summaries(self, parsed_files: List[Any]) -> List[FileSummary]:
        """Generate summary for each file."""
        summaries = []
        
        for parsed in parsed_files:
            if not parsed:
                continue
            
            try:
                # Basic summary without LLM
                purpose = self._generate_basic_summary(parsed)
                
                # Try LLM enhancement if available
                if self.llm:
                    try:
                        purpose = self._generate_llm_summary(parsed)
                    except Exception as e:
                        print(f"LLM summary failed for {parsed.file_path}, using basic: {e}")
                
                summaries.append(FileSummary(
                    file_path=parsed.file_path,
                    purpose=purpose,
                    key_exports=parsed.exports[:5],
                    api_dependencies=[
                        call.get("call", "")[:100] for call in parsed.api_calls[:5]
                    ],
                    framework=parsed.framework
                ))
            
            except Exception as e:
                print(f"Error summarizing {parsed.file_path}: {e}")
                summaries.append(FileSummary(
                    file_path=parsed.file_path,
                    purpose="Error generating summary",
                    framework=parsed.framework
                ))
        
        print(f"✓ Generated {len(summaries)} file summaries")
        return summaries
    
    def _generate_basic_summary(self, parsed) -> str:
        """Generate basic summary without LLM."""
        parts = []
        
        if parsed.components:
            parts.append(f"Contains {len(parsed.components)} component(s)")
        
        if parsed.api_calls:
            parts.append(f"makes {len(parsed.api_calls)} API call(s)")
        
        if parsed.exports:
            parts.append(f"exports {len(parsed.exports)} item(s)")
        
        if parsed.framework:
            parts.append(f"using {parsed.framework}")
        
        return " | ".join(parts) if parts else "Code file"
    
    def _generate_llm_summary(self, parsed) -> str:
        """Generate summary using LLM."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a code analyst. Summarize this file in one concise sentence (max 100 chars)."),
            ("user", "File: {file_path}\n\nComponents: {components}\nExports: {exports}\nImports: {imports}\nAPI Calls: {api_calls}\n\nSummarize:")
        ])
        
        response = self.llm.invoke(
            prompt.format_messages(
                file_path=Path(parsed.file_path).name,
                components=", ".join([c.name for c in parsed.components[:3]]) or "none",
                exports=", ".join(parsed.exports[:3]) or "none",
                imports=", ".join([imp.get("source", "") for imp in parsed.imports[:3]]) or "none",
                api_calls=", ".join([call.get("url", "") for call in parsed.api_calls[:2]]) or "none"
            )
        )
        
        return response.content[:200]
    
    def _generate_folder_summaries(self, file_summaries: List[FileSummary]) -> List[FolderSummary]:
        """Generate summary for each folder."""
        folders = defaultdict(list)
        
        for summary in file_summaries:
            folder = str(Path(summary.file_path).parent)
            folders[folder].append(summary)
        
        folder_summaries = []
        
        for folder_path, files in folders.items():
            purpose = f"Contains {len(files)} file(s)"
            
            # Add framework info
            frameworks = [f.framework for f in files if f.framework]
            if frameworks:
                common_framework = max(set(frameworks), key=frameworks.count)
                purpose += f" | Framework: {common_framework}"
            
            key_files = [Path(f.file_path).name for f in files[:5]]
            
            folder_summaries.append(FolderSummary(
                folder_path=folder_path,
                purpose=purpose,
                file_count=len(files),
                key_files=key_files
            ))
        
        print(f"✓ Generated {len(folder_summaries)} folder summaries")
        return folder_summaries
    
    def _generate_project_summary(self, file_summaries: List[FileSummary],
                                  folder_summaries: List[FolderSummary],
                                  parsed_files: List[Any]) -> ProjectSummary:
        """Generate project-level summary."""
        frameworks = [f.framework for f in file_summaries if f.framework]
        framework = max(set(frameworks), key=frameworks.count) if frameworks else None
        
        all_api_calls = []
        for parsed in parsed_files:
            if parsed:
                all_api_calls.extend([call.get("url", "") for call in parsed.api_calls])
        
        api_endpoints = self._extract_api_endpoints(all_api_calls)
        suggested = self._suggest_backend_endpoints(api_endpoints)
        
        top_components = [f.file_path for f in file_summaries[:5]]
        
        architecture = "Frontend SPA"
        if framework == "nextjs":
            architecture = "Next.js Full-stack"
        elif framework == "react":
            architecture = "React Application"
        elif framework == "vue":
            architecture = "Vue.js Application"
        
        summary = ProjectSummary(
            project_root=str(self.config.project_root),
            framework=framework,
            architecture=architecture,
            key_components=top_components,
            api_endpoints_used=list(set(api_endpoints))[:10],
            suggested_backend_endpoints=suggested
        )
        
        print(f"✓ Generated project summary | Framework: {framework}")
        return summary
    
    def _extract_api_endpoints(self, api_calls: List[str]) -> List[str]:
        """Extract API endpoints from fetch/axios calls."""
        import re
        endpoints = []
        
        for call in api_calls:
            if not call:
                continue
            
            # Extract path patterns
            if call.startswith('/'):
                endpoints.append(call.split('?')[0])
            elif 'http' in call:
                # Extract path from full URL
                match = re.search(r'https?://[^/]+(/[^\s\'"]*)', call)
                if match:
                    endpoints.append(match.group(1).split('?')[0])
        
        return endpoints
    
    def _suggest_backend_endpoints(self, endpoints: List[str]) -> List[str]:
        """Suggest backend endpoints based on frontend usage."""
        suggestions = []
        
        for endpoint in set(endpoints):
            if endpoint.startswith('/api/'):
                suggestions.append(endpoint)
            elif endpoint.startswith('/'):
                suggestions.append(f"/api{endpoint}")
        
        return suggestions[:10]
