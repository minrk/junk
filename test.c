#include <stdio.h>
#include <unistd.h>

int main() {
    for(int i=0; i<=600; i++) {
        if (i % 10 == 0) {
            printf("%d", i);
        }
        printf(".");
        fflush(stdout);
        usleep(1000000);
    }
    printf("\n");
    return 0;
}
