%option noyywrap yylineno
%{
#include <stdio.h>
#include "y.tab.h"
int state;
void UndefinedTokenPrint();
int lexInOpen(char* filename);
void lexInClose();
%}

LETTER [a-zA-Z]
DIGIT [0-9]
IDENTIFIER {LETTER}({LETTER}|{DIGIT})*
STRING \"([^\"]*)?\"
NUMBER {DIGIT}+
COMMENT \/\*.*\*\/
SEPARATOR_PLUS \+
SEPARATOR_MINUS -
SEPARATOR_MUL \*
SEPARATOR_DIV \/
SEPARATOR_GT >
SEPARATOR_LT <
SEPARATOR_LB \(
SEPARATOR_RB \)
KEYWORD_CALC calc
KEYWORD_LIST list
KEYWORD_VAR var
KEYWORD_PUSH push
KEYWORD_WHILE while
KEYWORD_DEFINE define
KEYWORD_RETURN return

DELIM [ \t\n]

%%
{DELIM} {;}
{KEYWORD_WHILE} { printf("(KEYWORD_WHILE, %s)\n", yytext); return KEYWORD_WHILE; }
{KEYWORD_RETURN} { printf("(KEYWORD_RETURN, %s)\n", yytext); return KEYWORD_RETURN; }
{KEYWORD_DEFINE} { printf("(KEYWORD_DEFINE, %s)\n", yytext); return KEYWORD_DEFINE; }
{KEYWORD_CALC} { printf("(KEYWORD_CALC, %s)\n", yytext); return KEYWORD_CALC; }
{KEYWORD_LIST} { printf("(KEYWORD_LIST, %s)\n", yytext); return KEYWORD_LIST; }
{KEYWORD_VAR} { printf("(KEYWORD_VAR, %s)\n", yytext); return KEYWORD_VAR; }
{KEYWORD_PUSH} { printf("(KEYWORD_PUSH, %s)\n", yytext); return KEYWORD_PUSH; }
{SEPARATOR_PLUS} { printf("(SEPARATOR_PLUS, %s)\n", yytext);return SEPARATOR_PLUS; }
{SEPARATOR_MINUS} { printf("(SEPARATOR_MINUS, %s)\n", yytext); return SEPARATOR_MINUS; }
{SEPARATOR_MUL} { printf("(SEPARATOR_MUL, %s)\n", yytext); return SEPARATOR_MUL; }
{SEPARATOR_DIV} { printf("(SEPARATOR_DIV, %s)\n", yytext);return SEPARATOR_DIV; }
{SEPARATOR_GT} { printf("(SEPARATOR_GT, %s)\n", yytext);return SEPARATOR_GT; }
{SEPARATOR_LT} { printf("(SEPARATOR_LT, %s)\n", yytext);return SEPARATOR_LT; }
{SEPARATOR_LB} { printf("(SEPARATOR_LB, %s)\n", yytext);return SEPARATOR_LB; }
{SEPARATOR_RB} { printf("(SEPARATOR_RB, %s)\n", yytext);return SEPARATOR_RB; }
{NUMBER} { printf("(NUMBER, %s)\n", yytext); sscanf(yytext, "%s", yylval.name); return (NUMBER); }
{IDENTIFIER} { printf("(IDENTIFIER, %s)\n", yytext); sscanf(yytext, "%s", yylval.name); return (IDENTIFIER); }
{STRING} { printf("(STRING, %s)\n", yytext);sscanf(yytext, "%s", yylval.name); return (STRING); }
{COMMENT} {;}
%%

int lexInOpen(char* filename)
{
	if((yyin = fopen(filename, "r")) == NULL)
	{
		printf("\nCannot open file %s.\n", filename);
		return -1;
	}
	yylineno = 1;
    return 0;
}

void lexInClose()
{
    fclose(yyin);
}

void UndefinedTokenPrint()
{
	printf("Error: \"Нераспознанный токен\" in line %d. Token = %s\n", yylineno, yytext);
}