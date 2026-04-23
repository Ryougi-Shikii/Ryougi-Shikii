#include<stdio.h>
#include<stdlib.h>
struct node {
	int data;
	struct node *next;
};
struct node *head=NULL;
void add(struct node **start, int data){
	struct node *temp=(struct node*)malloc(sizeof(struct node));
	struct node *t=(struct node*)malloc(sizeof(struct node));
	if (*start==NULL){
		temp->data=data;
		temp->next=NULL;
		*start=temp;
	}
	else{
		for (temp=*start;temp->next!=NULL;temp=temp->next);
		t->data=data;
		t->next=NULL;
		temp->next=t;
	}
}
void display(struct node **start){
	struct node *temp=(struct node*)malloc(sizeof(struct node));
	printf("\nstart -> ");
	for (temp=*start;temp!=NULL;temp=temp->next){
		printf("%d -> ", temp->data);
	}
	printf(" End\n");
}

int main(){
	int i,n;
	printf("Enter number of element: ");
	scanf("%d",&n);
	for (i=0; i<n; i++){
		int val;
		printf("Enter number: ");
		scanf("%d",&val);
		add(&head, val);
	}
	display(&head);
	return 0;
}

