#include<stdio.h>
#include<stdlib.h>
struct stack{
    int data;
    struct stack *next;
};
struct stack *head=NULL;
void push(struct stack *start, int data){
    struct stack *temp, *t;
    temp=(struct stack *)malloc(sizeof(struct stack));
    t=(struct stack *)malloc(sizeof(struct stack));
    if (head==NULL){
        temp->data=data;
        temp->next=NULL;
        head=temp;
    }
    else{
        temp->data=data;
        temp->next=head;
        head=temp;
    }
}
void display(struct stack *head){
    struct stack *temp;
    temp=(struct stack *)malloc(sizeof(struct stack));
    if (head==NULL){
        printf("Empty stack!!\n");
    }
    else {
        printf("Start: ");
        temp=head;

        while (temp!=NULL){
            printf("%d->",temp->data);
            temp=temp->next;
        }
        printf("End!\n");
    }
}
void pop(struct stack *head){
    struct stack *temp;
    temp=(struct stack *)malloc(sizeof(struct stack));
    if (head==NULL){
        printf("Underflow!");
    }
    else {
        int item=head->data;
        temp=head;
        head=head->next;
        free(temp);
        printf("  Poped :p\n");
    }
}
int main(){
    int ab,ba;
    printf("Enter number of element: ");
    scanf("%d", &ab);
    for (int i=0; i<ab; i++){
        printf("Enter value: ");
        scanf("%d", &ba);
        push(head, ba);
    }
    display(head);
    pop(head);
    display(head);
    return 0;
}