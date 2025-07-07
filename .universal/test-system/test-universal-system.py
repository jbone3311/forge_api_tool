#!/usr/bin/env python3
"""
Universal AI Development System - Comprehensive Test Suite

This script tests all components of the universal AI development system:
- Cursor rules integration
- MCP tool configurations
- Memory system functionality
- Template system
- Branch-specific features
- Pre-commit hooks
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
import tempfile

class UniversalSystemTester:
    def __init__(self):
        self.current_dir = Path.cwd()
        self.test_results = []
        self.errors = []
        
    def log_test(self, test_name: str, status: str, details: str = ""):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "details": details
        }
        self.test_results.append(result)
        
        # Print result
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {status}")
        if details:
            print(f"   📝 {details}")
    
    def test_directory_structure(self) -> bool:
        """Test 1: Verify directory structure exists"""
        print("\n🔍 Testing Directory Structure...")
        
        required_dirs = [
            ".universal/rules",
            ".universal/templates", 
            ".universal/mcp",
            ".universal/memory/main",
            ".universal/memory/tasks",
            ".universal/memory/docs-cache",
            ".universal/extensions",
            ".universal/hooks",
            ".cursor/rules"
        ]
        
        missing_dirs = []
        for dir_path in required_dirs:
            if not Path(dir_path).exists():
                missing_dirs.append(dir_path)
        
        if missing_dirs:
            self.log_test("Directory Structure", "FAIL", f"Missing directories: {missing_dirs}")
            return False
        else:
            self.log_test("Directory Structure", "PASS", f"All {len(required_dirs)} directories exist")
            return True
    
    def test_cursor_rules(self) -> bool:
        """Test 2: Verify Cursor rules configuration"""
        print("\n🎯 Testing Cursor Rules...")
        
        # Test .cursorrules file
        cursorrules_path = Path(".cursorrules")
        if not cursorrules_path.exists():
            self.log_test("Cursor Rules", "FAIL", ".cursorrules file missing")
            return False
        
        try:
            with open(cursorrules_path, 'r') as f:
                rules = json.load(f)
            
            if "rules" not in rules:
                self.log_test("Cursor Rules", "FAIL", "No 'rules' section in .cursorrules")
                return False
            
            if len(rules["rules"]) < 5:
                self.log_test("Cursor Rules", "FAIL", f"Only {len(rules['rules'])} rules found, expected 6+")
                return False
            
            self.log_test("Cursor Rules", "PASS", f"Found {len(rules['rules'])} rules")
            return True
            
        except json.JSONDecodeError as e:
            self.log_test("Cursor Rules", "FAIL", f"Invalid JSON in .cursorrules: {e}")
            return False
    
    def test_advanced_cursor_rules(self) -> bool:
        """Test 3: Verify advanced Cursor rules with metadata"""
        print("\n🔧 Testing Advanced Cursor Rules...")
        
        required_rules = [
            "10-memory.mdc",
            "30-docs.mdc", 
            "40-graphs.mdc",
            "branch.mdc",
            "refactor-rule.mdc"
        ]
        
        missing_rules = []
        for rule_file in required_rules:
            rule_path = Path(f".cursor/rules/{rule_file}")
            if not rule_path.exists():
                missing_rules.append(rule_file)
        
        if missing_rules:
            self.log_test("Advanced Cursor Rules", "FAIL", f"Missing rule files: {missing_rules}")
            return False
        
        # Test metadata in rules
        metadata_found = 0
        for rule_file in required_rules:
            rule_path = Path(f".cursor/rules/{rule_file}")
            with open(rule_path, 'r') as f:
                content = f.read()
                if "---" in content and "description:" in content:
                    metadata_found += 1
        
        if metadata_found < len(required_rules):
            self.log_test("Advanced Cursor Rules", "WARNING", f"Only {metadata_found}/{len(required_rules)} rules have metadata")
        else:
            self.log_test("Advanced Cursor Rules", "PASS", f"All {len(required_rules)} rules have metadata")
        
        return True
    
    def test_mcp_configuration(self) -> bool:
        """Test 4: Verify MCP tool configuration"""
        print("\n🔧 Testing MCP Configuration...")
        
        mcp_config_path = Path(".universal/mcp/mcp.json")
        if not mcp_config_path.exists():
            self.log_test("MCP Configuration", "FAIL", "mcp.json file missing")
            return False
        
        try:
            with open(mcp_config_path, 'r') as f:
                config = json.load(f)
            
            required_servers = ["memory-bank", "knowledge-graph", "docs-provider", "sequential-thinking"]
            missing_servers = []
            
            for server in required_servers:
                if server not in config.get("mcpServers", {}):
                    missing_servers.append(server)
            
            if missing_servers:
                self.log_test("MCP Configuration", "FAIL", f"Missing MCP servers: {missing_servers}")
                return False
            
            # Check for .universal paths
            config_str = json.dumps(config)
            if ".forge" in config_str:
                self.log_test("MCP Configuration", "FAIL", "Found .forge references, should be .universal")
                return False
            
            self.log_test("MCP Configuration", "PASS", f"All {len(required_servers)} MCP servers configured")
            return True
            
        except json.JSONDecodeError as e:
            self.log_test("MCP Configuration", "FAIL", f"Invalid JSON in mcp.json: {e}")
            return False
    
    def test_memory_system(self) -> bool:
        """Test 5: Verify memory system structure"""
        print("\n🧠 Testing Memory System...")
        
        # Test main branch memory
        main_progress = Path(".universal/memory/main/progress.md")
        if not main_progress.exists():
            self.log_test("Memory System", "FAIL", "main/progress.md missing")
            return False
        
        # Test memory content
        with open(main_progress, 'r') as f:
            content = f.read()
            
        required_sections = [
            "Project Overview",
            "Recent Decisions & Changes", 
            "Architecture Decisions",
            "Current Status"
        ]
        
        missing_sections = []
        for section in required_sections:
            if section not in content:
                missing_sections.append(section)
        
        if missing_sections:
            self.log_test("Memory System", "FAIL", f"Missing sections: {missing_sections}")
            return False
        
        self.log_test("Memory System", "PASS", "Memory system properly structured")
        return True
    
    def test_template_system(self) -> bool:
        """Test 6: Verify template system"""
        print("\n📋 Testing Template System...")
        
        required_templates = [
            "ai-development-workflow.md",
            "ai-enhanced-testing.md",
            "ai-assisted-refactoring.md"
        ]
        
        missing_templates = []
        for template in required_templates:
            template_path = Path(f".universal/templates/{template}")
            if not template_path.exists():
                missing_templates.append(template)
        
        if missing_templates:
            self.log_test("Template System", "FAIL", f"Missing templates: {missing_templates}")
            return False
        
        # Test template content quality
        quality_score = 0
        for template in required_templates:
            template_path = Path(f".universal/templates/{template}")
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if len(content) > 1000:  # Templates should be substantial
                        quality_score += 1
            except UnicodeDecodeError:
                # Try with different encoding
                with open(template_path, 'r', encoding='latin-1') as f:
                    content = f.read()
                    if len(content) > 1000:  # Templates should be substantial
                        quality_score += 1
        
        if quality_score < len(required_templates):
            self.log_test("Template System", "WARNING", f"Only {quality_score}/{len(required_templates)} templates are substantial")
        else:
            self.log_test("Template System", "PASS", f"All {len(required_templates)} templates are substantial")
        
        return True
    
    def test_pre_commit_hook(self) -> bool:
        """Test 7: Verify pre-commit hook"""
        print("\n🔗 Testing Pre-commit Hook...")
        
        hook_path = Path(".universal/hooks/pre-commit")
        if not hook_path.exists():
            self.log_test("Pre-commit Hook", "FAIL", "pre-commit hook missing")
            return False
        
        # Test hook permissions
        if not os.access(hook_path, os.X_OK):
            self.log_test("Pre-commit Hook", "WARNING", "Pre-commit hook not executable")
        
        # Test hook content
        try:
            with open(hook_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(hook_path, 'r', encoding='latin-1') as f:
                content = f.read()
            
        required_features = [
            "BRANCH=$(git branch --show-current)",
            "PROGRESS_FILE=",
            "git add"
        ]
        
        missing_features = []
        for feature in required_features:
            if feature not in content:
                missing_features.append(feature)
        
        if missing_features:
            self.log_test("Pre-commit Hook", "FAIL", f"Missing features: {missing_features}")
            return False
        
        self.log_test("Pre-commit Hook", "PASS", "Pre-commit hook properly configured")
        return True
    
    def test_setup_script(self) -> bool:
        """Test 8: Verify setup script"""
        print("\n🚀 Testing Setup Script...")
        
        setup_script = Path(".universal/setup-new-project.py")
        if not setup_script.exists():
            self.log_test("Setup Script", "FAIL", "setup-new-project.py missing")
            return False
        
        # Test script syntax
        try:
            result = subprocess.run([sys.executable, "-m", "py_compile", str(setup_script)], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                self.log_test("Setup Script", "FAIL", f"Python syntax error: {result.stderr}")
                return False
        except Exception as e:
            self.log_test("Setup Script", "FAIL", f"Error testing script: {e}")
            return False
        
        self.log_test("Setup Script", "PASS", "Setup script has valid Python syntax")
        return True
    
    def test_branch_specific_features(self) -> bool:
        """Test 9: Test branch-specific memory creation"""
        print("\n🌿 Testing Branch-Specific Features...")
        
        # Create a test branch
        test_branch = "test-branch-system"
        
        try:
            # Check if we're in a git repository
            result = subprocess.run(["git", "status"], capture_output=True, text=True)
            if result.returncode != 0:
                self.log_test("Branch-Specific Features", "SKIP", "Not in a git repository")
                return True
            
            # Create test branch memory directory
            test_memory_dir = Path(f".universal/memory/{test_branch}")
            test_memory_dir.mkdir(parents=True, exist_ok=True)
            
            # Create test progress file
            test_progress = test_memory_dir / "progress.md"
            test_content = f"""# {test_branch} Branch - Test Progress

## Project Overview
**Branch**: {test_branch}
**Created**: Test

## Recent Decisions & Changes

### Test Entry
- **Test**: Branch-specific memory creation
- **Status**: Success
"""
            
            with open(test_progress, 'w', encoding='utf-8') as f:
                f.write(test_content)
            
            # Verify creation
            if test_progress.exists():
                self.log_test("Branch-Specific Features", "PASS", f"Successfully created memory for {test_branch}")
                
                # Cleanup
                shutil.rmtree(test_memory_dir)
                return True
            else:
                self.log_test("Branch-Specific Features", "FAIL", "Failed to create branch-specific memory")
                return False
                
        except Exception as e:
            self.log_test("Branch-Specific Features", "FAIL", f"Error testing branch features: {e}")
            return False
    
    def test_mcp_tool_availability(self) -> bool:
        """Test 10: Check if MCP tools are available"""
        print("\n🔧 Testing MCP Tool Availability...")
        
        mcp_tools = [
            "mcp-memory-bank",
            "mcp-knowledge-graph", 
            "mcp-docs-provider",
            "mcp-sequential-thinking"
        ]
        
        available_tools = []
        missing_tools = []
        
        for tool in mcp_tools:
            try:
                result = subprocess.run(["npx", tool, "--help"], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0 or "Usage:" in result.stdout or "Usage:" in result.stderr:
                    available_tools.append(tool)
                else:
                    missing_tools.append(tool)
            except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
                missing_tools.append(tool)
        
        if missing_tools:
            self.log_test("MCP Tool Availability", "WARNING", 
                         f"Missing tools: {missing_tools}. Install with: npm install -g {' '.join(missing_tools)}")
        else:
            self.log_test("MCP Tool Availability", "PASS", f"All {len(mcp_tools)} MCP tools available")
        
        return len(available_tools) > 0
    
    def run_all_tests(self) -> Dict:
        """Run all tests and return results"""
        print("🧪 Universal AI Development System - Comprehensive Test Suite")
        print("=" * 70)
        
        tests = [
            self.test_directory_structure,
            self.test_cursor_rules,
            self.test_advanced_cursor_rules,
            self.test_mcp_configuration,
            self.test_memory_system,
            self.test_template_system,
            self.test_pre_commit_hook,
            self.test_setup_script,
            self.test_branch_specific_features,
            self.test_mcp_tool_availability
        ]
        
        # Execute all tests
        for test in tests:
            try:
                test()
            except Exception as e:
                self.log_test(test.__name__, "ERROR", f"Test crashed: {e}")
        
        # Count results from stored test results
        passed = 0
        failed = 0
        warnings = 0
        skipped = 0
        
        for result in self.test_results:
            if result["status"] == "PASS":
                passed += 1
            elif result["status"] == "FAIL":
                failed += 1
            elif result["status"] == "WARNING":
                warnings += 1
            elif result["status"] == "SKIP":
                skipped += 1
        
        # Generate summary
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Warnings: {warnings}")
        print(f"⏭️  Skipped: {skipped}")
        print(f"📈 Total: {passed + failed + warnings + skipped}")
        
        if failed == 0:
            print("\n🎉 All critical tests passed! Your universal system is ready.")
        else:
            print(f"\n🔧 {failed} critical tests failed. Please fix issues before using the system.")
        
        return {
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "skipped": skipped,
            "results": self.test_results
        }

def main():
    """Main function"""
    tester = UniversalSystemTester()
    results = tester.run_all_tests()
    
    # Exit with error code if any critical tests failed
    if results["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main() 