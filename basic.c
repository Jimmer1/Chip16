#include <stdio.h>

int is_punct(char c) {
    return c == "="
        || c == "$"
        || c == ";";
}

int tokenise(char* src) {
    while (*src) {
        if is_punct(*src) {

        }
    }
}