from decimal import Decimal
import re

def interpret_pseudocode(code: str, max_iterations=1000):
    variables = {}
    output = []
    lines = code.strip().split("\n")
    i = 0
    
    def evaluate_condition(condition):
        try:
            return bool(evaluate_expression(condition, variables))
        except ValueError as e:
            output.append(f"Error evaluating condition '{condition}': {e}")
            return False
    
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        
        if re.match(r'if (.+) then', line):
            condition = re.match(r'if (.+) then', line).group(1)
            if evaluate_condition(condition):
                i += 1
                block = []
                depth = 1
                while i < len(lines) and depth > 0:
                    if re.match(r'if (.+) then', lines[i]):
                        depth += 1
                    elif re.match(r'endif', lines[i]):
                        depth -= 1
                    if depth > 0:
                        block.append(lines[i])
                    i += 1
                sub_output = interpret_pseudocode("\n".join(block), max_iterations)
                output.extend(sub_output.split('\n'))
            else:
                depth = 1
                while i < len(lines) and depth > 0:
                    i += 1
                    if re.match(r'if (.+) then', lines[i]):
                        depth += 1
                    elif re.match(r'endif', lines[i]):
                        depth -= 1
            i += 1
            continue
        
        if re.match(r'while (.+) do', line):
            condition = re.match(r'while (.+) do', line).group(1)
            loop_start = i
            loop_body = []
            depth = 1
            while i < len(lines) - 1 and depth > 0:
                i += 1
                if re.match(r'while (.+) do', lines[i]):
                    depth += 1
                elif re.match(r'endwhile', lines[i]):
                    depth -= 1
                if depth > 0:
                    loop_body.append(lines[i])
            iteration_count = 0
            while evaluate_condition(condition):
                iteration_count += 1
                if iteration_count > max_iterations:
                    output.append(f"Error: Exceeded maximum iterations ({max_iterations}) in while loop with condition '{condition}'")
                    break
                sub_output = interpret_pseudocode("\n".join(loop_body), max_iterations)
                output.extend(sub_output.split('\n'))
            i += 1
            continue
        
        if re.match(r'endif', line) or re.match(r'endwhile', line):
            i += 1
            continue
        
        match = re.match(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)', line)
        if match:
            var_name, expression = match.groups()
            try:
                variables[var_name] = evaluate_expression(expression, variables)
            except ValueError as e:
                output.append(f"Error evaluating expression '{expression}': {e}")
            i += 1
            continue
        
        print_match = re.match(r'print\((.+)\)', line)
        if print_match:
            expression = print_match.group(1).strip()
            try:
                output.append(str(evaluate_expression(expression, variables)))
            except ValueError as e:
                output.append(f"Error in print statement '{expression}': {e}")
            i += 1
            continue
        
        output.append(f"Unrecognized syntax: {line}")
        i += 1
    
    return "\n".join(output)

def evaluate_expression(expression, variables):
    expression = expression.strip()
    
    if expression.lower() in ["true", "false"]:
        return expression.lower() == "true"
    
    if re.fullmatch(r'\d+(\.\d+)?', expression):
        return Decimal(expression)
    
    if expression.startswith('[') and expression.endswith(']'):
        list_elements = expression[1:-1].split(',')
        return [evaluate_expression(elem.strip(), variables) for elem in list_elements]
    
    if expression.startswith('"') and expression.endswith('"') and len(expression) > 1:
        return expression[1:-1]
    
    if expression in variables:
        return variables[expression]
    
    try:
        return eval(expression, {"__builtins__": {}}, variables)
    except Exception:
        raise ValueError(f"Invalid expression: {expression}")

if __name__ == "__main__":
    code = """
    num1 = 10
    num2 = 20
    if num1 < num2 then
        print("num1 is less than num2")
    endif
    counter = 1
    while counter <= 3 do
        print(counter)
        counter = counter + 1
    endwhile
    """
    output = interpret_pseudocode(code)
    print(output)