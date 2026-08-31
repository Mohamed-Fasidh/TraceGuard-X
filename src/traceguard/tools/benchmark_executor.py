
def run_synthetic(code: str, test_cases=None):
    test_cases = test_cases or [
        {"input":"hello","expected":"hello"},
        {"input":"","expected":""},
    ]
    result={"exit_code":0,"tests_passed":0,"tests_total":len(test_cases),"outputs":[],"error":None}
    if "while True" in code or "while 1" in code:
        result["exit_code"]=None
        result["error"]="TIMEOUT (synthetic fixture)"
        return result
    try:
        namespace={}
        exec(compile(code,"candidate.py","exec"),namespace,namespace)
        solve=namespace.get("solve")
        if not callable(solve):
            result["exit_code"]=1; result["error"]="solve is not callable"; return result
        for case in test_cases:
            try:
                out=solve(case.get("input"))
                result["outputs"].append(out)
                if out == case.get("expected"):
                    result["tests_passed"]+=1
            except Exception as exc:
                result["exit_code"]=1
                result["error"]=f"{type(exc).__name__}: {exc}"
        return result
    except Exception as exc:
        result["exit_code"]=1
        result["error"]=f"{type(exc).__name__}: {exc}"
        return result
