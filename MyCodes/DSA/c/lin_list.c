#include<stdio.h>
#include<stdlib.h>

struct node{
    int data;
    struct node *next;
};

void creat(struct node **head,int data){
    struct node *t,*temp;
    t=(struct node*) malloc (sizeof(struct node));
    t=*head;
    temp=(struct node*) malloc (sizeof(struct node));
    temp->data=data;
    temp->next=NULL;

    if (t==NULL){
        *head=temp;
    }
    else{
        for( t=*head; t->next!=NULL; t=t->next);
        t->next=temp;
    }
}

void display(struct node **head){
    struct node *t;
    t=(struct node*) malloc (sizeof(struct node));
    t=*head;
    if (t==NULL){
        printf("It's Empty");
    }
    else{
        printf("\nStart -> ");
        while (t!=NULL){
            printf("%d -> ",t->data);
            t=t->next;
        }
        printf("End\n");
    }

}

void insert1(struct node **head,int data,int pos){
    struct node *t,*temp;
    if (pos==1){
        t=(struct node*) malloc (sizeof(struct node));
        t->data=data;
        t->next=*head;
        *head=t;
    }
    else if (pos==2){
        t=(struct node*) malloc (sizeof(struct node));
        temp=(*head);
        t->data=data;
        t->next=temp->next;
        temp->next=t;

    }
    else{
        temp=*head;
        for (int i=1; i<pos-1; i++){
            temp=temp->next;
        }
        t=(struct node*) malloc (sizeof(struct node));
        t->data=data;
        t->next=temp->next;
        temp->next=t;
    }
}


int main(){
    int ch,data;
    struct node *head=NULL;
    creat(&head,1);
    creat(&head,2);
    creat(&head,3);
    creat(&head,4);
    creat(&head,5);

    display(&head);
    insert1(&head,-5,5);
    display(&head);
    insert1(&head,-4,4);
    display(&head);
    insert1(&head,-3,3);
    display(&head);
    insert1(&head,-2,2);
    display(&head);
    insert1(&head,-1,1);
    display(&head);
    printf("\n");
    return 0;
}