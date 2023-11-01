%{
#include <stdio.h>
#include <locale.h>

int yylex();

int yyerror(char* s);
int lexInOpen(char* filename);
void lexInClose();
%}

%start PROGRAM

%token<name> IDENTIFIER STRING
%token<number_value>NUMBER
%token SEPARATOR_PLUS SEPARATOR_MINUS SEPARATOR_MUL SEPARATOR_DIV SEPARATOR_GT SEPARATOR_LT SEPARATOR_LB SEPARATOR_RB
%token KEYWORD_CALC KEYWORD_LIST KEYWORD_VAR KEYWORD_PUSH KEYWORD_WHILE KEYWORD_DEFINE KEYWORD_RETURN KEYWORD_CALL KEYWORD_OBJECT

%type<token> DTYPE KEY OPERAND
%type<delim> OPERATIONS_SUM OPERATIONS_COMPARE OPERATIONS_MUL
%type<token> MULTIPLICATION SUMMA EXPRESSION VALUE

%union{
    int lex;
    int number_value;
    char delim;
    unsigned char name[200];
    struct Token {
        int value;
        char name[200];
        // 0 - number, 1 - string
        char type;
        char isIdentifier; //1 if true
        char isAssigned; //1 if true
    } token;
}

%%

PROGRAM:        S_EXP_LIST
                ;

S_EXP_LIST:     S_EXP |
                S_EXP_LIST S_EXP
                ;

S_EXP:      DATA |
            SEPARATOR_LB {printf("{\n");}
            S_EXP_LIST
            SEPARATOR_RB {{printf("}\n");}}
            ;

KEY:        IDENTIFIER { strcpy($$.name, $1); $$.type = 2; } |
            STRING { strcpy($$.name, $1); $$.type = 1; }
            ;

DTYPE:      STRING { strcpy($$.name, $1); $$.type = 1; } |
            NUMBER { $$.value = $1; $$.type = 0; }
            ;


DATA:       CALC_EXP |
            KEYWORD_LIST SEPARATOR_LB DATA SEPARATOR_RB |
            OBJECT |
            KEY_VALUE_S_EXP_LIST |
            SEPARATOR_LB KEY_VALUE_S_EXP SEPARATOR_RB
            ;

OBJECT:     KEYWORD_OBJECT SEPARATOR_LB DATA SEPARATOR_RB

KEY_VALUE_S_EXP_LIST:       KEY_VALUE_S_EXP |
                            KEY_VALUE_S_EXP KEY_VALUE_S_EXP_LIST
                            ;

KEY_VALUE_S_EXP:        KEY DTYPE
                        {
                            if ($2.type == 0)
                            {
                                printf("%d\n", $2.value);
                            }
                            else 
                            {
                                printf("%s\n", $2.name);
                            };
                        }|
                        KEY SEPARATOR_LB DATA SEPARATOR_RB
                        ;

CALC_EXP:       KEYWORD_CALC SEPARATOR_LB OPERATOR_LIST SEPARATOR_RB
                ;

OPERAND:        IDENTIFIER { strcpy($$.name, $1); $$.type = 2; } |
                DTYPE {$$ = $1;}
                ;

EXPRESSION:     SUMMA { $$ = $1; } |
                EXPRESSION OPERATIONS_COMPARE SUMMA
                {
                if ($3.type == 0 && $1.type == 0)
                {
                    printf("Sep: %d\n", $2);
                    if ($2 == 3)
                    {
                        $1.value = $1.value > $3.value;
                    }
                    else
                    {
                        $1.value = $1.value < $3.value;
                    }
                    $$ = $1;
                }
                else 
                {
                    printf("Ошибка, сравнивать можно только числа\n");
                };
            }
                ;

SUMMA:      MULTIPLICATION { $$ = $1; } |
            SUMMA OPERATIONS_SUM MULTIPLICATION
            {
                if ($3.type == 0 && $1.type == 0)
                {
                    printf("Sep: %d\n", $2);
                    if ($2 == 1)
                    {
                        $1.value = $1.value + $3.value;
                    }
                    else
                    {
                        $1.value = $1.value - $3.value;
                    }
                    $$ = $1;
                }
                else if ($3.type == 1 && $1.type == 1)
                {
                    if ($2 == 3)
                    {
                        strcat($1.name, $3.name);
                        $$ = $1;
                    }
                    else
                    {
                        printf("Ошибка, строки нельзя вычитать\n");
                    }
                }
                else 
                {
                    printf("Ошибка, операции сложения применимы только к числам\n");
                };
            }
            ;

MULTIPLICATION:     OPERAND { $$ = $1; } |
                    MULTIPLICATION OPERATIONS_MUL OPERAND
                    {
                        if ($3.type == 0 && $1.type == 0)
                        {
                            printf("Sep: %d\n", $2);
                            if ($2 == 5)
                            {
                                $1.value = $1.value * $3.value;
                            }
                            else
                            {
                                $1.value = $1.value / $3.value;
                            }
                            $$ = $1;
                        }
                        else
                        {
                            printf("Ошибка, операции умножения применимы только к числам\n");
                        };
                    }
                    ;

OPERATOR_LIST:      SEPARATOR_LB OPERATOR SEPARATOR_RB |
                    SEPARATOR_LB OPERATOR SEPARATOR_RB OPERATOR_LIST
                    ;

OPERATOR_RETURN:        KEYWORD_RETURN SEPARATOR_LB VALUE SEPARATOR_RB


OPERATOR:       OPERATOR_ASSIGNMENT |
                OPERATOR_DEFINE |
                OPERATOR_WHILE |
                OPERATOR_CALL |
                OPERATOR_PUSH
                ;

IDENTIFIER_LIST:        IDENTIFIER |
                        IDENTIFIER IDENTIFIER_LIST
                        ;

OPERATOR_PUSH:      KEYWORD_PUSH SEPARATOR_LB VALUE SEPARATOR_RB
                    ;

OPERATOR_CALL:      KEYWORD_CALL IDENTIFIER CALL
                    ;

CALL:       SEPARATOR_LB IDENTIFIER_LIST SEPARATOR_RB
            ;

OPERATOR_WHILE:     KEYWORD_WHILE SEPARATOR_LB EXPRESSION SEPARATOR_RB SEPARATOR_LB OPERATOR_LIST SEPARATOR_RB
                    ;

VALUE:      EXPRESSION { $$ = $1;}|
            IDENTIFIER { $$ = $1; }|
            OPERATOR_CALL { $$ = $1; }
            ;

OPERATOR_ASSIGNMENT:        KEYWORD_VAR IDENTIFIER SEPARATOR_LB VALUE SEPARATOR_RB
                            {
                                ;
                            }
                            ;

OPERATOR_DEFINE:        KEYWORD_DEFINE IDENTIFIER SEPARATOR_LB IDENTIFIER_LIST SEPARATOR_RB SEPARATOR_LB OPERATOR_LIST OPERATOR_RETURN SEPARATOR_RB |
                        KEYWORD_DEFINE IDENTIFIER SEPARATOR_LB IDENTIFIER_LIST SEPARATOR_RB SEPARATOR_LB SEPARATOR_LB OPERATOR_RETURN SEPARATOR_RB SEPARATOR_RB |
                        ;

OPERATIONS_SUM:     SEPARATOR_PLUS { $$ = 1; } |
                    SEPARATOR_MINUS { $$ = 2; }
                    ;

OPERATIONS_COMPARE:     SEPARATOR_GT { $$ = 3; } |
                        SEPARATOR_LT { $$ = 4; }
                        ;

OPERATIONS_MUL:     SEPARATOR_MUL { $$ = 5; } |
                    SEPARATOR_DIV { $$ = 6; }
                    ;

%%

int main(int argc, char **argv)
{
    setlocale(LC_ALL, "");
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
