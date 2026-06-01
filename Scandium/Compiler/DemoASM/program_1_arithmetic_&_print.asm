section .data

section .text
    global main


main:
    push rbp
    mov  rbp, rsp
    sub  rsp, 256        ; reserve stack space

    ; TAC: t1 = 2 * 3
    mov  rbx, 2
    imul  rbx, 3
    ; TAC: a = t1 + 4
    mov  rcx, rbx
    add  rcx, 4
    ; TAC: print a
    ; --- print(a) ---
    mov  rdi, rcx
    call scandium_print

    ; --- program exit ---
    xor  eax, eax        ; return 0
    leave
    ret
