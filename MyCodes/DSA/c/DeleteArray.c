#include <stdio.h>
int main(){
	int arr[100] = { 0 };
	int i, pos, n = 10;

	// initial array of size 10
	for (i = 0; i < 10; i++)
		arr[i] = i + 1;

	// print the original array
	for (i = 0; i < n; i++)
		printf("%d ", arr[i]);
	printf("\n");

	// position of element delete
    printf("enter the position(delete)");
    scanf("%d",&pos);

	// increase the size by 1
	n--;

    //deleting and shifting our array backwards
    for (i=pos;i<n+1;++i){
        arr[i-1] = arr[i];
    }

	// print the updated array
    printf("\nyour updated array:\n\n");
	for (i = 0; i < n; i++)
		printf("%d ", arr[i]);
	printf("\n");

	return 0;
}
