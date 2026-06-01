section .data

section .text
    global main


main:
    push rbp
    mov  rbp, rsp
    sub  rsp, 256        ; reserve stack space

    ; TAC: x = 10
    mov  rbx, 10
    ; TAC: y = 20
    mov  rcx, 20
    ; TAC: t1 = 10 < 20
    mov  rsi, 10
    cmp  rsi, 20
    setl al
    movzx rdx, al
    ; TAC: ifFalse t1 goto L1
    cmp  rdx, 0
    je   L1
    ; TAC: print 10
    ; --- print(10) ---
    mov  rdi, 10
    call scandium_print
    ; TAC: goto L2
    jmp  L2
    ; TAC: L1:
L1:
    ; TAC: print y
    ; --- print(y) ---
    mov  rdi, rcx
    call scandium_print
    ; TAC: L2:
L2:

    ; --- program exit ---
    xor  eax, eax        ; return 0
    leave
    ret
