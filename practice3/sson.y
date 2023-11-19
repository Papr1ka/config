%locations
%define parse.error verbose

%{
#include <stdio.h>
#include <locale.h>
#include <string.h>

#define SIZE 2000
#define OBJECT_MAX_KEYS 50
#define MAX_OBJECTS 50

int yylex();

int yyerror(const char* s);
int lexInOpen(char* filename);
void lexInClose();
int tabs;
void addTabs(char* dest, int inc);

extern int yylineno;

int objectId;
int currentObjectFilled;
char objectTables[SIZE][OBJECT_MAX_KEYS][MAX_OBJECTS];

void putKey(char* key);
int findKey(char* key);
void clearTable();
%}

%start program

%token<name> IDENTIFIER STRING NUMBER
%token SEPARATOR_LB SEPARATOR_RB
%token KEYWORD_LIST

%type<name> value list object s_exp s_exp_list dtype dtype_list data

%union{
    char name[2000];
}

%%

value:      IDENTIFIER { strcpy($$, "\""); strcat($$, $1); strcat($$, "\""); } |
            NUMBER { strcpy($$, $1); } |
            STRING { strcpy($$, $1); }
            ;

program:        s_exp_list
                {
                    printf("{\n");
                    
                    printf($1);
                    
                    printf("\n}");
                }
                ;

s_exp:      data { strcpy($$, $1); } |
            SEPARATOR_LB s_exp_list SEPARATOR_RB
            {
                strcpy($$, "{\n");
                
                strcat($$, $2);
                
                strcpy($$, "}\n");
            }
            ;


s_exp_list:     s_exp { strcpy($$, $1); } |
                s_exp s_exp_list { strcpy($$, $1); strcat($$, ",\n"); strcat($$, $2); }
                ;

data:       value dtype {
                if (findKey($1) != -1)
                {
                    char error[2000];
                    sprintf(error, "Semantic error, duplicate key in object: %s", $1);
                    yyerror(error);
                    YYERROR;
                }
                else
                {
                    strcpy($$, ""); addTabs($$, 0); strcat($$, $1); strcat($$, ": "); strcat($$, $2);
                    putKey($1);
                }
            }
            ;


dtype:      list { strcpy($$, $1); } |
            value { strcpy($$, $1); } |
            {
                objectId++;
            }
            object
            {
                strcpy($$, $2);
                clearTable();
            }
            ;

dtype_list:     dtype { strcpy($$, ""); addTabs($$, 1); strcat($$, $1); } |
                dtype dtype_list { strcpy($$, ""); addTabs($$, 1); strcat($$, $1), strcat($$, ",\n"); strcat($$, $2); }
                ;

list:       KEYWORD_LIST SEPARATOR_LB dtype_list SEPARATOR_RB
            {
                strcpy($$, "[\n");
                
                strcat($$, $3);
                
                strcat($$, "\n");
                
                addTabs($$, 0);

                strcat($$, "]");
            }
            ;

object:     SEPARATOR_LB s_exp_list SEPARATOR_RB
            {
                strcpy($$, "{\n");
                
                strcat($$, $2);

                strcat($$, "\n");
                
                addTabs($$, 0);

                strcat($$, "}");
            }
            ;


%%

int main(int argc, char **argv)
{
    objectId = 0;
    currentObjectFilled = 0;
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

int yyerror(const char* s)
{
    printf("error\n");
    fprintf(stderr, "%s at line %d\n", s, yylineno);
}

int yywrap()
{
    return(0);
}

void addTabs(char* dest, int inc)
{
    for (int i = 0; i < tabs + inc; i++)
    {
        strcat(dest, "    ");
    }
}

int findKey(char* key)
{
    for (int i = 0; i < currentObjectFilled; i++)
    {
        if (strcmp(objectTables[objectId][i], key) == 0)
        {
            return 0;
        }
    }
    return -1;
}

void putKey(char* key)
{
    strcpy(objectTables[objectId][currentObjectFilled], key);
    currentObjectFilled++;
}

void clearTable()
{
    for (int i = 0; i < currentObjectFilled; i++)
    {
        strcpy(objectTables[objectId][i], "");
    }
    currentObjectFilled = 0;
    objectId;
}
