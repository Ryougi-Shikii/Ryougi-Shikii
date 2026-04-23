#include <stdio.h>
#include <math.h>

void s_even(int *arr, int n){
    int even_sum=0;
    for(int i = 0; i < n; i ++){
        if(arr[i] % 2 == 0){
            even_sum = even_sum + arr[i];
        }
    }
    printf("sum of even is : %d", even_sum);

}

void s_odd(int *arr, int n){
    int odd_sum=0;
    for(int i = 0; i < n; i ++){
        if(arr[i] % 2 != 0){
            odd_sum = odd_sum + arr[i];
        }
    }    
    printf("sum of odd: %d", odd_sum);

}

void s_prime(int *arr, int n){
    int i,j,p,sum=0;
    for (i = 0; i < n; i++) {
        j = 2;
        p = 1;
        while (j < arr[i]) {
            if (arr[i] % j == 0) {
                p = 0;
                break;
            }
            j++;
        }
        if (p == 1)
            sum = sum + arr[i];
    }
    printf("sum of prime: %d", sum);

}

int len(int n){
    int length = 0;  
    while(n != 0){    
        length = length + 1;    
        n = n/10;    
    }
    return length;
}

int isDisarium(int number) {
    int originalNumber = number;
    int digitCount = len(number);
    int sum = 0;

    while (number != 0) {
      int digit = number % 10;
      sum += pow(digit, digitCount);
      digitCount--;
      number /= 10;
    }

    return (sum == originalNumber);
}

void s_dize(int *arr, int n){
    int i,sum;
    for (i=0;i<n;++i){
        int j=arr[i];
        int a=isDisarium(j);
        if (a==1){
            sum+=1;
        }

    }
    printf("%d",sum);

}

void input(int *arr, int n){
    printf("Enter the elements");
    for (int i = 0; i < n; ++i){
        scanf("%d", &arr[i]);
    }

}

int main() {
    int arr[50],n;
    printf("enter array size");
    scanf("%d",&n);
    input(arr, n);
    int choice;
    printf("enter your choice\n  1 for sum of even \n  2 for sum of odd \n  3 for sum of prime\n  4 for sum of dizerium\n");
    scanf("%d",&choice);
    switch(choice)
    {
        case 1 : s_even(arr,n);
            break;
        case 2: s_odd(arr,n);
            break;
        case 3: s_prime(arr,n);
            break;
        case 4 : s_dize(arr,n);
            break;
    }
    return 0;
}



