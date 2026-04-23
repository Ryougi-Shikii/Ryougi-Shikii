#include <stdio.h>
int main(){
	int arr[100] = { 0 };
	int i, x, pos, n = 10;

	// initial array of size 10
	for (i = 0; i < 10; i++)
		arr[i] = i + 1;

	// print the original array
	for (i = 0; i < n; i++)
		printf("%d ", arr[i]);
	printf("\n");

	// element to be inserted
    printf("enter the element you want in first position: ");
    scanf("%d",&x);

	// position at which element
	// is to be inserted
    printf("enter the position");
    scanf("%d",&pos);

	// increase the size by 1
	n++;

	// shift elements forward
	for (i = n - 1; i >= pos; i--)
		arr[i] = arr[i - 1];

	// insert x,the element, at pos
	arr[pos - 1] = x;

	// print the updated array
    printf("your updated array:\n\n");
	for (i = 0; i < n; i++)
		printf("%d ", arr[i]);
	printf("\n");

	return 0;
}
