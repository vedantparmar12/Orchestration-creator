import subprocess
import asyncio
from typing import Dict, Any, List, Tuple
from concurrent.futures import ThreadPoolExecutor

class ValidationGates:
    """Automated testing and quality assurance"""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def run_pytest(self, test_path: str) -> Dict[str, Any]:
        """Run pytest validation"""
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(self.executor, self._pytest_runner, test_path)
            return result
        except Exception as e:
            return {"error": str(e)}

    def _pytest_runner(self, test_path: str) -> Dict[str, Any]:
        """Synchronous pytest runner"""
        result = subprocess.run(
            ['pytest', test_path, '--maxfail=1', '--disable-warnings', '--tb=short', '-q'],
            capture_output=True,
            text=True
        )
        
        passed = result.returncode == 0
        output = result.stdout + result.stderr
        return {
            "passed": passed,
            "output": output
        }
    
    async def run_ruff_check(self, code_path: str) -> Dict[str, Any]:
        """Run ruff linting"""
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(self.executor, self._ruff_runner, code_path)
            return result
        except Exception as e:
            return {"error": str(e)}

    def _ruff_runner(self, code_path: str) -> Dict[str, Any]:
        """Synchronous ruff lint runner"""
        result = subprocess.run(
            ['ruff', 'check', code_path],
            capture_output=True,
            text=True
        )
        
        passed = result.returncode == 0
        output = result.stdout + result.stderr
        return {
            "passed": passed,
            "output": output
        }
    
    async def run_type_check(self, code_path: str) -> Dict[str, Any]:
        """Run mypy type checking"""
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(self.executor, self._mypy_runner, code_path)
            return result
        except Exception as e:
            return {"error": str(e)}

    def _mypy_runner(self, code_path: str) -> Dict[str, Any]:
        """Synchronous mypy runner"""
        result = subprocess.run(
            ['mypy', code_path],
            capture_output=True,
            text=True
        )
        
        passed = result.returncode == 0
        output = result.stdout + result.stderr
        return {
            "passed": passed,
            "output": output
        }
    
    async def validate_all(self, code_path: str, test_path: str = "tests") -> Tuple[bool, List[str], List[str]]:
        """Run all validation gates in parallel"""
        pytest_result = await self.run_pytest(test_path)
        ruff_result = await self.run_ruff_check(code_path)
        mypy_result = await self.run_type_check(code_path)
        
        results = [pytest_result, ruff_result, mypy_result]
        passed = all(res.get("passed", False) for res in results)
        errors = [res["output"] for res in results if not res.get("passed", False)]
        warnings = [res["output"] for res in results if "warning" in res.get("output", "").lower()]
        
        return passed, errors, warnings

