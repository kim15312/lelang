import sys

variables = {}

def is_valid_varname(name):
    if not name.startswith("ELG"):
        return False
    num_part = name[3:]
    return num_part.isdigit()

def parse_value(token):
    # 숫자면 정수 변환, 변수명일 경우 변수에서 값 가져오기
    if token.isdigit() or (token.startswith('-') and token[1:].isdigit()):
        return int(token)
    elif is_valid_varname(token):
        if token in variables:
            return variables[token]
        else:
            raise ValueError(f"Undefined variable: {token}")
    else:
        raise ValueError(f"Invalid token: {token}")

def assign_variable(varname, value):
    if varname in variables:
        raise ValueError(f"Variable '{varname}' already exists.")
    variables[varname] = value

def update_variable(varname, value):
    variables[varname] = value

def interpret_line(line):
    tokens = line.strip().split()
    if not tokens:
        return

    cmd = tokens[0]

    if cmd == "LOO_BODY":
        # 변수 생성 및 연산
        # 형식 1: LOO_BODY ELGx }}}}}  (단독 할당)
        # 형식 2: LOO_BODY ELGx ELGy } ELGz (변수 덧셈)
        # 형식 3: LOO_BODY ELGx ELGy { ELGz (변수 뺄셈)

        varname = tokens[1]
        if not is_valid_varname(varname):
            raise ValueError(f"Invalid variable name: {varname}")

        # 변수 중복 검사
        if varname in variables:
            raise ValueError(f"Variable '{varname}' already exists.")

        if len(tokens) == 3:
            # 단독 할당
            val_str = tokens[2]
            val = 0
            for ch in val_str:
                if ch == '}':
                    val += 1
                elif ch == '{':
                    val -= 1
                else:
                    raise ValueError(f"Invalid character in value string: {ch}")
            assign_variable(varname, val)

        elif len(tokens) == 5:
            # 연산
            var2 = tokens[2]
            op = tokens[3]
            var3 = tokens[4]

            val2 = parse_value(var2)
            val3 = parse_value(var3)

            if op == '}':
                val = val2 + val3
            elif op == '{':
                val = val2 - val3
            else:
                raise ValueError(f"Invalid operator: {op}")

            assign_variable(varname, val)

        else:
            raise ValueError("Invalid LOO_BODY syntax")

    elif cmd == "LOO_LARM":
        # 입력 받기
        varname = tokens[1]
        if not is_valid_varname(varname):
            raise ValueError(f"Invalid variable name: {varname}")
        if varname in variables:
            raise ValueError(f"Variable '{varname}' already exists.")

        # 입력 받기
        user_input = input()
        # 입력을 정수로 변환 시도
        try:
            val = int(user_input)
        except:
            raise ValueError("Input must be an integer")
        assign_variable(varname, val)

    elif cmd == "LOO_RARM":
        # 출력
        if len(tokens) != 3:
            raise ValueError("Invalid LOO_RARM syntax")
        val_token = tokens[1]
        mode = tokens[2]

        val = parse_value(val_token)

        if mode == "엘":
            print(val)
        elif mode == "구":
            print(chr(val), end='')
        else:
            raise ValueError(f"Invalid output mode: {mode}")

    elif cmd == "LOO_STAR":
        # 조건문 (조건은 변수값 == 2)
        varname = tokens[1]
        if varname not in variables:
            raise ValueError(f"Undefined variable: {varname}")
        cond = (variables[varname] == 2)
        return cond  # 호출하는 쪽에서 조건문 실행 여부 판단

    elif cmd == "LOO_GOGGLE":
        # 주석 - 무시
        pass

    elif cmd == "LOO_LLEG":
        # 반복문 시작
        # 토큰 1이 LOO_LLEG, 토큰 2는 숫자 또는 변수명
        count_token = tokens[1]
        count = parse_value(count_token)
        return ("loop_start", count)

    elif cmd == "LOO_RLEG":
        # 반복문 종료
        return ("loop_end", )

    else:
        raise ValueError(f"Unknown command: {cmd}")

def interpret_program(lines):
    i = 0
    n = len(lines)
    skip_block = False
    loop_stack = []

    while i < n:
        line = lines[i]
        tokens = line.strip().split()
        if not tokens:
            i += 1
            continue
        cmd = tokens[0]

        if skip_block:
            # 조건문에 의해 블록 건너뛰기
            if cmd == "LOO_STAR" or cmd == "LOO_LLEG" or cmd == "LOO_RLEG":
                skip_block = False
                continue
            else:
                i += 1
                continue

        if cmd == "LOO_STAR":
            cond = interpret_line(line)
            if not cond:
                skip_block = True
            i += 1

        elif cmd == "LOO_LLEG":
            res = interpret_line(line)
            if isinstance(res, tuple) and res[0] == "loop_start":
                loop_count = res[1]
                loop_start = i + 1
                # 반복문 범위 찾기
                depth = 1
                j = loop_start
                while j < n and depth > 0:
                    tkns = lines[j].strip().split()
                    if tkns and tkns[0] == "LOO_LLEG":
                        depth += 1
                    elif tkns and tkns[0] == "LOO_RLEG":
                        depth -= 1
                    j += 1
                loop_end = j - 1
                # 반복 실행
                for _ in range(loop_count):
                    interpret_program(lines[loop_start:loop_end])
                i = loop_end + 1
            else:
                i += 1

        else:
            interpret_line(line)
            i += 1

if __name__ == "__main__":
    program = []
    print("Enter LElang code lines. Empty line to end.")
    while True:
        try:
            line = input()
            if line.strip() == "":
                break
            program.append(line)
        except EOFError:
            break
    interpret_program(program)
