#include<stdio.h>
int main( ){

    int arr[50],rev[50],i,n,j;

    /* taking inputs */
    printf("enter the number of array elements: ");
    scanf("%d",&n);
    printf("Enter the elements: ");
    for (i = 0; i < n; ++i){
        scanf("%d", &arr[i]);
    }

    /* printing  array */
    printf("\noriginal array:\n");
    for (i = 0; i < n; ++i){
        printf("%d\t",arr[i]);
        
    }

    /* reversing */
    for (i = 0,j = n; i < n; ++i,--j){
        rev[i]=arr[j-1]*arr[j-1];

    }

    /* printing reversed array */
    printf("\nreversed squared array:\n");
    for (i = 0; i < n; ++i){
        printf("%d\t",rev[i]);
        
    }

    return 0;
}