section .data

section .text
    global main


main:
    push rbp
    mov  rbp, rsp
    sub  rsp, 256        ; reserve stack space

    ; TAC: i = 0
    mov  rbx, 0
    ; TAC: L1:
L1:
    ; TAC: t1 = i < 3
    cmp  rbx, 3
    setl al
    movzx rcx, al
    ; TAC: ifFalse t1 goto L2
    cmp  rcx, 0
    je   L2
    ; TAC: print i
    ; --- print(i) ---
    mov  rdi, rbx
    call scandium_print
    ; TAC: i = i + 1
    mov  rbx, rbx
    add  rbx, 1
    ; TAC: goto L1
    jmp  L1
    ; TAC: L2:
L2:

    ; --- program exit ---
    xor  eax, eax        ; return 0
    leave
    ret
