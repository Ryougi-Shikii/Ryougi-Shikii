#include<stdio.h>
#include<stdlib.h>

struct stack{
    int data;
    struct stack *next;
};

void creat(struct stack **top,int data){
    struct stack *t=(struct stack*)malloc(sizeof(struct stack)),*temp;
    t->data=data;
    if (*top==NULL){
        t->next=NULL;
        *top=t;
    }
    else{
        t->next=*top;
        *top=t;
    }

}

void display(struct stack **head){
    struct stack *temp;
    temp=(struct stack *)malloc(sizeof(struct stack));
    if (*head==NULL){
        printf("Empty stack!!\n");
    }
    else {
        printf("Start: ");
        temp=*head;

        while (temp!=NULL){
            printf("%d->",temp->data);
            temp=temp->next;
        }
        printf(" End!\n");
    }
}

void pop(struct stack **top){
    struct stack *temp;
    temp=*top;
    *top=(*top)->next;
    printf("pooped: %d\n",temp->data);
    free(temp);
}

struct stack *top=NULL;

int main(){


    creat(&top,1);
    creat(&top,2);
    creat(&top,3);
    creat(&top,4);
    creat(&top,5);

    display(&top);
    pop(&top);
    display(&top);
    pop(&top);
    display(&top);
    pop(&top);
    display(&top);
    pop(&top);
    display(&top);
    pop(&top);
    display(&top);
    return 0;
}