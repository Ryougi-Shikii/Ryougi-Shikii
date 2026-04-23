#include<stdio.h>

int main()
{
	int i,j,k,z,r,p;
	
	printf("Enter the range:- ");
	scanf("%d",&r);
	
	z=4;
	k=1;
	i=1;
	p=(r/2)+2;
	if(r%2==1)
	{
		while(i<=r)
		{
			if(i<p)
			{
				j=1;
				while(j<=r-i)
				{
					printf(" ");
					j++;
				}
				j=1;
				while(j<=k)
				{
					printf("*");
					j++;
				}
				k=k+2;
			}
			else
			{
				j=1;
				while(j<=i-1)
				{
					printf(" ");
					j++;
				}
				j=1;
				while(j<=k-z)
				{
					printf("*");
					j++;
				}
				k=k-2;
			}
			i++;
			printf("\n");
		}
	}
	else
	{
		printf("Please Enter only odd value");
	}
	
	return 0;
}
