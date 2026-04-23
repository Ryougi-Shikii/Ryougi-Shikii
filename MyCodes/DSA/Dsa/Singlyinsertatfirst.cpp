#include<stdio.h>
#include<conio.h>
#include<stdlib.h>

struct node
{
	int data;
	struct node *next;
};

typedef struct node NODE;

void create(NODE **,int);
void display(NODE **);
void addfirst(NODE **,int);

int main()
{
	NODE *start;
	int n,loc,num;
	char ch;
	start=NULL;

	do{
		printf("Enter the element which you want to enter in the Linked List : ");
		scanf("%d",&n);

		create(&start,n);
		display(&start);

		printf("\n\nDo you want to enter more (Y/y for yes and N/n for no): ");
		ch=getche();
		fflush(stdin);
		printf("\n\n");
	}while(ch=='Y'||ch=='y');
	printf("\n\nThe Resultant Linked List is\n\n");
	display(&start);
	printf("\n\nEnter the element: ");
	scanf("%d",&num);
	addfirst(&start,num);
	display(&start);
	return 0;
}
void create(NODE **start,int n)
{
	NODE *temp,*t;

	if(*start==NULL)
	{
		temp = (NODE *)malloc(sizeof(NODE));
		temp->data=n;
		temp->next=NULL;
		*start=temp;
	}
	else
	{
		for(temp=(*start) ; temp->next!=NULL ; temp=temp->next);

		t =(NODE *)malloc(sizeof(NODE));

		t->data=n;
		t->next=NULL;
		temp->next=t;
	}
}

void display(NODE **start)
{
	NODE *temp;
	temp=*start;
	printf("\n\nStart -> ");
	while(temp!=NULL)
	{
	       printf("%d -> ",temp->data);
	       temp=temp->next;
	}
	printf("End");
}

void addfirst(NODE **start, int num)
{
	NODE *temp;
	temp=(NODE *)malloc(sizeof(NODE));
	temp->data=num;
	temp->next=(*start);
	*start=temp;
}

