section .data

section .text
    global main


main:
    push rbp
    mov  rbp, rsp
    sub  rsp, 256        ; reserve stack space

    ; TAC: a = -5
    mov  rbx, -5
    ; TAC: b = 10
    mov  rcx, 10
    ; TAC: c = 10 - 3
    mov  rdx, 10
    sub  rdx, 3
    ; TAC: print c
    ; --- print(c) ---
    mov  rdi, rdx
    call scandium_print

    ; --- program exit ---
    xor  eax, eax        ; return 0
    leave
    ret
