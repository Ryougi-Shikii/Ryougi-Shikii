section .data

section .text
    global main

    ; TAC: func AddTwo:
AddTwo:
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

    ; TAC: x = 5
    mov  rbx, 5
    ; TAC: y = 6
    mov  rcx, 6
    ; TAC: param 5
    ; TAC: param 6
    ; TAC: t2 = call AddTwo, 2
    mov  rdi, 5
    mov  rsi, 6
    call AddTwo
    mov  rdx, rax   ; save return value
    ; TAC: print t2
    ; --- print(t2) ---
    mov  rdi, rdx
    call scandium_print

    ; --- program exit ---
    xor  eax, eax        ; return 0
    leave
    ret
