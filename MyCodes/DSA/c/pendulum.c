#include<stdio.h>
int main(){
    /* declaration */
    int i,j,even=0,odd=1,arr[50],rearr[50],rev[50],n,a;

    /* taking inputs */
    printf("enter the number of array elements: ");
    scanf("%d",&n);
    printf("Enter the elements: ");
    for (i = 0; i < n; ++i){
        scanf("%d", &arr[i]);
    }

    /* sorting our array */
    for (i = 0; i < n; ++i){
        for (j = i + 1; j < n; ++j){
            if (arr[i] > arr[j]){
                a = arr[i];
                arr[i] = arr[j];
                arr[j] = a;
            }
        }
    }

    /* rearranging our aray */
    for (i=0; i < n; ++i){
        if ((i+1)%2==0){

            int ev=(n/2)-even;
            rearr[ev]=arr[i];
            even+=1;
        }
        else if ((i+1)%2!=0){
            int od=(n/2)+odd;
            rearr[od]=arr[i];
            odd+=1;
        }

    } 

    /* printing rearranged array */
    printf("\nleft:\n");
    for (i = 0; i < n; ++i){
        printf("%d\t",rearr[i+1]);
        
    }

    /* reversing */
    for (i = 0,j = n; i < n; ++i,--j){
        rev[i]=rearr[j];
        
    }

    /* printing reversed array */
    printf("\nright:\n");
    for (i = 0; i < n; ++i){
        printf("%d\t",rev[i]);
        
    }

    /* end of programme */
    return 0;
}