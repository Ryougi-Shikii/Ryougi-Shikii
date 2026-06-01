section .data

section .text
    global main

    ; TAC: func add:
add:
    push rbp
    mov  rbp, rsp
    sub  rsp, 128
    ; TAC: a = param_a
    mov  rbx, rdi  ; a = arg0
    ; TAC: b = param_b
    mov  rcx, rsi  ; b = arg1
    ; TAC: t1 = a + b
    mov  rdx, rbx
    add  rdx, rcx
    ; TAC: return t1
    mov  rax, rdx
    leave
    ret
    ; TAC: endfunc
    ; (implicit return 0 if no earlier ret)
    xor  eax, eax
    leave
    ret


main:
    push rbp
    mov  rbp, rsp
    sub  rsp, 256        ; reserve stack space

    ; TAC: param 3
    ; TAC: param 4
    ; TAC: result = call add, 2
    mov  rdi, 3
    mov  rsi, 4
    call add
    mov  rbx, rax   ; save return value
    ; TAC: print result
    ; --- print(result) ---
    mov  rdi, rbx
    call scandium_print

    ; --- program exit ---
    xor  eax, eax        ; return 0
    leave
    ret
