#include<stdio.h>
typedef struct student{
    
    int roll;
    char name[100];
    int age;
    
} stu ;

int main( ){



    stu me={584,"sumit",17};

    printf("%d\n",me.roll);
    printf("%s\n",me.name);
    printf("%d\n",me.age);

    return 0;
}