section .data

section .text
    global main


main:
    push rbp
    mov  rbp, rsp
    sub  rsp, 256        ; reserve stack space

    ; TAC: p = 5 * 6
    mov  rbx, 5
    imul  rbx, 6
    ; TAC: q = p
    mov  rcx, rbx
    ; TAC: r = p + p
    mov  rdx, rbx
    add  rdx, rbx
    ; TAC: print r
    ; --- print(r) ---
    mov  rdi, rdx
    call scandium_print

    ; --- program exit ---
    xor  eax, eax        ; return 0
    leave
    ret
