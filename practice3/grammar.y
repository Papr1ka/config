%{
#include <stdio.h>
#include <locale.h>

int yylex();

int yyerror(char* s);
int lexInOpen(char* filename);
void lexInClose();
%}

%start PROGRAM

%token IDENTIFIER STRING NUMBER SEPARATOR_PLUS SEPARATOR_MINUS SEPARATOR_MUL SEPARATOR_DIV SEPARATOR_GT SEPARATOR_LT SEPARATOR_LB SEPARATOR_RB KEYWORD_CALC KEYWORD_LIST KEYWORD_VAR KEYWORD_PUSH KEYWORD_WHILE KEYWORD_DEFINE KEYWORD_RETURN

%type <name> STRING
%type <name> NUMBER
%type <name> IDENTIFIER


%union{
    char name[100];
}

%%

KEY:        IDENTIFIER |
            STRING
            ;

DTYPE:      STRING |
            NUMBER
            ;

PROGRAM:        S_EXP_LIST
                ;

S_EXP_LIST:     S_EXP |
                S_EXP_LIST S_EXP
                ;

S_EXP:      DATA |
            SEPARATOR_LB S_EXP_LIST SEPARATOR_RB
            ;

DATA:       CALC_EXP |
            KEYWORD_LIST SEPARATOR_LB DATA SEPARATOR_RB |
            OBJECT
            ;

OBJECT:     SEPARATOR_LB KEY_VALUE_S_EXP_LIST SEPARATOR_RB
            ;

KEY_VALUE_S_EXP_LIST:       KEY_VALUE_S_EXP |
                            KEY_VALUE_S_EXP KEY_VALUE_S_EXP_LIST
                            ;

KEY_VALUE_S_EXP:        SEPARATOR_LB KEY DTYPE SEPARATOR_RB |
                        SEPARATOR_LB KEY SEPARATOR_LB DATA SEPARATOR_RB SEPARATOR_RB
                        ;

CALC_EXP:       KEYWORD_CALC SEPARATOR_LB OPERATOR_LIST SEPARATOR_RB
                ;

OPERAND:        IDENTIFIER |
                DTYPE
                ;

EXPRESSION:     SUMMA |
                EXPRESSION OPERATIONS_COMPARE SUMMA
                ;

SUMMA:      MULTIPLICATION |
            SUMMA OPERATIONS_SUM MULTIPLICATION
            ;

MULTIPLICATION:     OPERAND |
                    MULTIPLICATION OPERATIONS_MUL OPERAND
                    ;

OPERATOR_LIST:      OPERATOR |
                    OPERATOR OPERATOR_LIST
                    ;

OPERATOR_RETURN:        SEPARATOR_LB KEYWORD_RETURN OPERAND SEPARATOR_RB

OPERATOR_INSIDE_DEFINE_LIST:        OPERATOR_INSIDE_DEFINE |
                                    OPERATOR_INSIDE_DEFINE OPERATOR_INSIDE_DEFINE_LIST
                                    ;

OPERATOR_INSIDE_DEFINE:     OPERATOR_ASSIGNMENT |
                            KEYWORD_WHILE |
                            OPERATOR_CALL |
                            OPERATOR_PUSH
                            ;

OPERATOR_INSIDE:        OPERATOR_ASSIGNMENT |
                        KEYWORD_WHILE |
                        OPERATOR_CALL |
                        OPERATOR_PUSH |
                        ;

OPERATOR:       OPERATOR_ASSIGNMENT |
                OPERATOR_DEFINE |
                OPERATOR_WHILE |
                OPERATOR_CALL
                ;

IDENTIFIER_LIST:        IDENTIFIER |
                        IDENTIFIER IDENTIFIER_LIST
                        ;

OPERATOR_PUSH:      SEPARATOR_LB KEYWORD_PUSH EXPRESSION SEPARATOR_RB
                    ;

OPERATOR_CALL:      IDENTIFIER SEPARATOR_LB IDENTIFIER_LIST SEPARATOR_RB
                    ;

OPERATOR_WHILE:     KEYWORD_WHILE SEPARATOR_LB OPERAND OPERATIONS_COMPARE OPERAND SEPARATOR_RB SEPARATOR_LB OPERATOR_INSIDE SEPARATOR_RB
                    ;

OPERATOR_ASSIGNMENT:        KEYWORD_VAR IDENTIFIER SEPARATOR_LB EXPRESSION SEPARATOR_RB
                            ;

OPERATOR_DEFINE:        KEYWORD_DEFINE IDENTIFIER SEPARATOR_LB IDENTIFIER_LIST SEPARATOR_RB SEPARATOR_LB OPERATOR_INSIDE_DEFINE_LIST OPERATOR_RETURN SEPARATOR_RB
                        ;

OPERATIONS_SUM:     SEPARATOR_PLUS |
                    SEPARATOR_MINUS
                    ;

OPERATIONS_COMPARE:     SEPARATOR_GT |
                        SEPARATOR_LT
                        ;

OPERATIONS_MUL:     SEPARATOR_MUL |
                    SEPARATOR_DIV
                    ;

%%

int main(int argc, char **argv)
{
	if(argc < 2)
	{
		printf("\nNot enough arguments. Please specify filename.\n");
		return -1;
	}
	int isOpened = lexInOpen(argv[1]);
    if (isOpened != 0)
    {
        printf("\nFile can't be opened\n");
		return -1;
    }
	int r = yyparse();
	lexInClose();
    return r;
}

int yyerror(char* s)
{
    printf("error\n");
    fprintf(stderr, "%s\n",s);
}

int yywrap()
{
    return(1);
}
